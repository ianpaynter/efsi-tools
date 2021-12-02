import h5py
import os
import subprocess as sub
from google.cloud import storage
from time import time
import numpy as np
import dotenv
import t_laads_tools
import io

# Specify a laads file
laads_files = ["VNP46A2.A2020045.h09v04.001.2021054214350.h5",
               "VNP46A2.A2020045.h09v05.001.2021054204445.h5",
               "VNP46A2.A2020045.h08v04.001.2021055030438.h5",
               "VNP46A2.A2020045.h08v05.001.2021054234805.h5",
               "VNP46A2.A2020045.h07v04.001.2021055053939.h5",
               "VNP46A2.A2020045.h07v05.001.2021055061735.h5"]


for laads_file in laads_files:

    # Construct a laads url
    laads_url = os.environ["vnp46a_laads_url"] + "VNP46A2/2020/045/" + laads_file
    # Start a laads session
    laads_session = t_laads_tools.connect_to_laads()
    # Print update
    print(f"Fetching {laads_url}")
    # Get a file from the laads url
    h5_file = t_laads_tools.get_VNP46A_file(laads_session, laads_url, return_content=True)
    # Write it to disk
    with open(os.path.join(os.environ["cog_temp"], laads_file), "wb") as of:
        of.write(h5_file)
    # Convert to h5py file
    h5_file = h5py.File(io.BytesIO(h5_file))
    # Start time
    stime = time()
    # Load environmental variables
    dotenv.load_dotenv()

    # Form the base name of the file (removing the .h5 suffix)
    basename = os.path.splitext(os.path.basename(laads_file))[0]
    # Print an update
    print(f'File: {basename}.\n'
          f'Step 1 of 5: Get bounding box from h5 metadata.')
    # Get the metadata
    metadata = str(h5_file["HDFEOS INFORMATION"]['StructMetadata.0'][()])
    # Split metadata on newlines
    metadata = metadata.split('\\n')
    # Digest the strings down to the coordinates
    # Retrieve Upper Left (ul) coordinates of bounding box
    upper_left = metadata[7].split('=')
    upper_left = upper_left[1].split(',')
    ulx = upper_left[0].replace('(', '')
    uly = upper_left[1].replace(')', '')
    ulx = ulx.split('.')[0][:-6]
    uly = uly.split('.')[0][:-6]
    # Retrieve Lower Right (lr) coordinates of bounding box
    lower_right = metadata[8].split('=')
    lower_right = lower_right[1].split(',')
    lrx = lower_right[0].replace('(', '')
    lry = lower_right[1].replace(')', '')
    lrx = lrx.split('.')[0][:-6]
    lry = lry.split('.')[0][:-6]
    # Make the separate data set (sds) base name for the file (they will end up as <sdsname>_1.tif, <sdsname>_2.tif etc.
    sds_in = os.path.join(os.environ["cog_temp"], laads_file)
    sdsname = os.path.join(os.environ["cog_temp"], "ds" + basename + '.tif')
    # Form the gdal translate call to convert h5 to one tif per layer
    my_call = [os.environ["osgeo4w_path"],
               'gdal_translate',
               '-sds',
               sds_in,
               sdsname]
    # Print an update
    print(f'Step 2 of 5: Translate .h5 to .tif (one .tif for each band).')
    # Submit the call to the shell
    p = sub.Popen(my_call, stdout=sub.PIPE, stderr=sub.PIPE)
    # Read the response from the call
    stdout, stderr = p.communicate()
    # Print any errors
    if p.returncode != 0:
        print(stdout)
        print(stderr)
    # Form name for merged file
    merged_name = os.path.join(os.environ["cog_temp"], basename + '_merged.tif')
    # Make path to separated band files
    #separate_path = path.replace('Original', 'Separate')
    # Get the separate band files
    band_files = [str(f) for f in os.listdir(os.environ["cog_temp"]) if f.startswith(f"ds{basename}")]
    # Form the call to gdal merge
    my_call = [os.environ["osgeo4w_path"],
               'gdal_merge',
               '-separate',
               '-o',
               merged_name]
    # Append the band paths to the call (as input files)
    for band_file in band_files:
        my_call.append(os.path.join(os.environ["cog_temp"], band_file))
    # Print an update
    print(f'Step 3 of 5: Merging per-band .tifs in a single .tif file.')
    # Submit the call to the shell
    p = sub.Popen(my_call, stdout=sub.PIPE, stderr=sub.PIPE)
    # Read the response from the call
    stdout, stderr = p.communicate()
    # Print any errors
    if p.returncode != 0:
        print(stdout)
        print(stderr)
    # For each per-band file
    # for band_file in band_files:
    #     # Remove the band file
    #     os.remove(os.path.join(os.environ["cog_temp"], band_file))
    # Name for the COG file
    cog_name = os.path.join(os.environ["cog_temp"], basename + '_cog.tif')
    # For the call to gdal translate
    my_call = [os.environ["osgeo4w_path"],
               'gdal_translate',
               '-a_srs', 'EPSG:4326',
               '-a_ullr', ulx, uly, lrx, lry,
               merged_name,
               cog_name,
               '-of', 'COG',
               '-co', 'COMPRESS=DEFLATE']
    # Print an update
    print(f'Step 4 of 5: Converting merged .tif to COG.')
    # Submit the call to the shell
    p = sub.Popen(my_call, stdout=sub.PIPE, stderr=sub.PIPE)
    # Read the response from the call
    stdout, stderr = p.communicate()
    # Print any errors
    if p.returncode != 0:
        print(stdout)
        print(stderr)
    # Remove the merged file
    #os.remove(merged_name)
    # Print an update
    print(f'Step 5 of 5: Hosting COG on Google Cloud Storage.')
    # Set Google App Credentials
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.environ["google_app_creds"]
    # Make Google Cloud client object linked to COG project
    client = storage.Client(os.environ["google_bucket"])
    # Make storage client
    storage_client = storage.Client.from_service_account_json(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
    # Form the destination blob for the COG
    blob = storage_client.bucket(os.environ["google_bucket"]).blob(f'{basename}_cog.tif')
    # Open the COG
    with open(cog_name, 'rb') as upload_file:
        # Upload the file
        blob.upload_from_file(upload_file)
    # Print an update
    #print(f'Time to process and upload {basename}: {np.around(time() - ptime, decimals=2)}s')