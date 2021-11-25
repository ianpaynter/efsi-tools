import requests
import json
from time import sleep
import h5py
import io
import datetime
import dotenv
import os
from pathlib import Path
import matplotlib as mpl
from matplotlib import pyplot as plt

# Load the .env file
dotenv.load_dotenv()

# Function to submit request to LAADS and keep trying until we get a response
def try_try_again(r, s, target_url):

    # If we get timed out
    while r.status_code != 200:
        # Print a warning
        print(f'Warning, bad response for {target_url}.')
        # Wait a hot second
        sleep(10)
        # Try again
        r = s.get(target_url)
    return r

# Connect to LAADS and return a session object
def connect_to_laads():
    # Header command utilizing security token
    authToken = {'Authorization': f'Bearer {os.environ["laads_token"]}'}
    # Create session
    s = requests.session()
    # Update header with authorization
    s.headers.update(authToken)
    # Return the session object
    return s

# Get a VNP46A2 H5 file from laads and return it as a numpy array
def get_VNP46A2_file(session_obj, target_url):

    # Request the H5 file from the provided URL
    r = session_obj.get(target_url)
    # If the request failed
    if r.status_code != 200:
        # Send to repeated submission function
        r = try_try_again(r, session_obj, target_url)
    # Try to convert into an h5 object
    try:
        # Convert to h5 file object
        h5file = h5py.File(io.BytesIO(r.content), 'r')
        # Convert the response content to an H5py File object and return
        return h5file
    # If it fails (incomplete file)
    except:
        # Print a warning
        print('Warning: File could not be converted to h5. Possibly incomplete.')
        # Return False
        return False

# Function to return a dictionary of URLs to a VNP46A- product on LAADS (will update existing)
def get_VNP46A_availability(data_product,
                            start_fresh=False,
                            check_old_gaps=False,
                            cleanup_old_files=False):
    # Latest date
    latest_date = None
    # Walk the support file directory
    for root, dirs, files in os.walk(os.environ["support_files_path"]):
        # For each file name
        for name in files:
            # If the file is one of the URL files
            if "laads_urls" in name:
                # Split the name
                split_name = name.split('_')
                # If the first part of the name matches the data product
                if split_name[0] == data_product:
                    # Make a datetime date object from the name
                    file_date = datetime.date(year=int(split_name[-1][4:8]),
                                              month=int(split_name[-1][0:2]),
                                              day=int(split_name[-1][2:4]))
                    # If there is no latest date yet
                    if latest_date is None:
                        # Set the file's date
                        latest_date = file_date
                    # Otherwise, if the file's date is later
                    elif file_date > latest_date:
                        # Set the file's date as latest
                        latest_date = file_date
    # If there was a file (as indicated by the presence of a latest date)
    if latest_date is not None:
        # Print update
        print(f"Investigating file from {latest_date}")
        # Assemble the path to the file
        latest_file_path = Path(os.environ["support_files_path"] + data_product + "_laads_urls_" + latest_date.strftime("%m%d%Y") + ".json")
        # Open the file
        with open(latest_file_path, 'r') as f:
            # Load as dictionary
            urls_dict = json.load(f)
    # Otherwise (no previous url file)
    else:
        # Make an empty dictionary
        urls_dict = {}
    # Latest spidered date
    latest_spider = None
    # For each tile
    for tile in urls_dict.keys():
        # Get the highest day in the highest year
        highest_year = sorted(list(urls_dict[tile].keys()), key=int)[-1]
        highest_day = sorted(list(urls_dict[tile][highest_year]), key=int)[-1]
        # Get datetime object from day of year
        tile_last_date = datetime.date(year=int(highest_year), month=1, day=1) + datetime.timedelta(days=int(highest_day))
        # If there is no latest spider date
        if latest_spider is None:
            # Reference date
            latest_spider = tile_last_date
        # Otherwise, if this is new latest date
        elif tile_last_date > latest_spider:
            # Reference data
            latest_spider = tile_last_date
    # Print update
    print(f"Getting URLs from {latest_spider.year, latest_spider.month, latest_spider.day} onwards.")
    # Target URL for laads data
    target_url = os.environ["vnp46a_laads_url"] + data_product + ".json"
    # Get a laads session
    laads_session = connect_to_laads()
    # Reference laads token
    laads_token = os.environ["laads_token"]
    # Header command utilizing security token
    auth_token = {'Authorization': f'Bearer {laads_token}'}
    # Update header with authorization
    laads_session.headers.update(auth_token)
    # Get the years in json format from the target URL
    r = laads_session.get(target_url)
    # If the request failed
    if r.status_code != 200:
        # Send to repeated submission function
        r = try_try_again(r, laads_session, target_url)
    # Load the content of the response
    years = json.loads(r.text)
    # For each year in the data
    for year in years:
        # Get year value
        year_value = int(year["name"])
        # If the year is before the latest spider
        if year_value < latest_spider.year:
            # Skip it
            continue
        # Construct year URL
        year_url = target_url.replace(".json", f"/{year_value}.json")
        # Get the days (adding the year to the original URL
        r = laads_session.get(year_url)
        # If the request failed
        if r.status_code != 200:
            # Send to repeated submission function
            r = try_try_again(r, laads_session, year_url)
        # Load the data as text
        days = json.loads(r.text)
        # For each day
        for day in days:
            # Get day value
            day_value = int(day["name"])
            # If the year is the same as latest spider and day is before
            if year_value == latest_spider.year and day_value <= (latest_spider - datetime.date(year=latest_spider.year, month=1, day=1)).days:
                # Skip it
                continue
            # Construct day URL
            day_url = target_url.replace(".json", f"/{year_value}/{day_value}.json")
            # Get the tiles (adding the day and year to the URL)
            r = laads_session.get(day_url)
            print(f"Processing: {year_value}, day of year: {day_value}")
            # If the request failed
            if r.status_code != 200:
                # Send to repeated submission function
                r = try_try_again(r, laads_session, day_url)
            # Load the data as text
            tiles = json.loads(r.text)
            # For each of the tiles
            for tile in tiles:
                # Pull the file name of the tile
                file_name = tile["name"]
                # Split the name on the periods
                split_name = file_name.split('.')
                # Extract the year, day, and tile name
                tile_year = split_name[1][1:5]
                tile_doy = split_name[1][5:]
                tile_name = split_name[2]
                # Store the filename in the urls dictionary
                if tile_name not in urls_dict.keys():
                    urls_dict[tile_name] = {}
                if tile_year not in urls_dict[tile_name].keys():
                    urls_dict[tile_name][tile_year] = {}
                if tile_doy not in urls_dict[tile_name][tile_year].keys():
                    urls_dict[tile_name][tile_year][tile_doy] = file_name
    # Get today's date as a string
    file_date = datetime.datetime.now().strftime("%m%d%Y")
    # Construct save path
    save_path = os.environ["support_files_path"] + f'VNP46A2_laads_urls_{file_date}.json'
    # Write the dictionary
    with open(save_path, 'w') as of:
        json.dump(urls_dict, of)
    # Close the session
    laads_session.close()


# Visualize LAADS availability
def visualize_laads_availability(url_file_path):
    # Gain rate (determines angle for time series representation)
    gain_rate = 0.5
    # Open the file
    with open(url_file_path, 'r') as f:
        # Input dictionary
        url_dict = json.load(f)
    # Plotting variables
    line_starts = []
    line_ends = []
    # For each tile
    for tile in url_dict.keys():
        # Get tile coordinates from the tile name
        tile_h = int(tile[1:3])
        tile_v = int(tile[4:])


# Function to return a dictionary of VNP46A2 data available on LAADS
def get_VNP46A2_availability(start_year=None, start_doy=None):

    # Data dictionary
    data_dict = {}
    # Header command utilizing security token
    authToken = {'Authorization': f'Bearer {laadsToken}'}
    # Target URL for laads data
    target_url = f"https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/5000/VNP46A2.json"
    # Create session
    s = requests.session()
    # Update header with authorization
    s.headers.update(authToken)
    # Get the years in json format from the target URL
    r = s.get(target_url)
    # Load the content of the response
    years = json.loads(r.text)
    # For each year in the data
    for year in years:
        # Get year value
        year_value = year["name"]
        # If there is a start year specified
        if start_year is not None:
            if int(year_value) < start_year:
                continue
        # Construct year URL
        year_url = target_url.replace(".json", f"/{year_value}.json")
        # Get the days (adding the year to the original URL
        r = s.get(year_url)
        # If the request failed
        if r.status_code != 200:
            # Send to repeated submission function
            r = try_try_again(r, s, year_url)
        # Load the data as text
        days = json.loads(r.text)
        # For each day
        for day in days:
            # Get day value
            day_value = day["name"]
            # If there is a start day specified
            if start_doy is not None:
                if int(day_value) < start_doy:
                    continue
            # Construct day URL
            day_url = target_url.replace(".json", f"/{year_value}/{day_value}.json")
            # Get the tiles (adding the day and year to the URL)
            r = s.get(day_url)
            print(year_value, day_value)
            # If the request failed
            if r.status_code != 200:
                # Send to repeated submission function
                r = try_try_again(r, s, day_url)
            # Load the data as text
            tiles = json.loads(r.text)
            # For each of the tiles
            for tile in tiles:
                # Pull the file name of the tile
                file_name = tile["name"]
                # Split the name on the periods
                split_name = file_name.split('.')
                # Extract the year, day, and tile name
                tile_year = split_name[1][1:5]
                tile_doy = split_name[1][5:]
                tile_name = split_name[2]
                tile_collection = split_name[3]
                # Store the filename in the dictionary
                if tile_name not in data_dict.keys():
                    data_dict[tile_name] = {}
                if tile_year not in data_dict[tile_name].keys():
                    data_dict[tile_name][tile_year] = {}
                if tile_doy not in data_dict[tile_name][tile_year].keys():
                    data_dict[tile_name][tile_year][tile_doy] = file_name
    # Close the session
    s.close()

    return data_dict

if __name__ == '__main__':

    #stime = time()

    data_dict = get_VNP46A2_availability()

    #print(time() - stime)
    file_date = datetime.datetime.now().strftime("%m%d%Y")
    dl_folder = interrim_path
    filepath = f'{dl_folder}VNP46A2_laads_urls_{file_date}.json'
    # with open(file, 'wb') as of:
    # of.write(r.content)
    with open(filepath, 'w') as of:
        json.dump(data_dict, of)




