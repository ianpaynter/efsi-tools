import numpy as np
import requests
import io
import tifffile
from matplotlib import pyplot as plt


def get_wsf_tiles(tile_grid, tile_h, tile_v):

    # If it's a VNP46A tile grid
    if "VNP46A" in tile_grid:
        # Start of tiles
        west_edge = -180 + (tile_h * 10)
        south_edge = 88 - (tile_v * 10)
        # WSF tile list
        wsf_tile_list = []
        # For the horizontal tiles
        for wsf_h in np.arange(west_edge, west_edge + 10, 2):
            for wsf_v in np.arange(south_edge, south_edge - 10, -2):
                # Append to tile list
                wsf_tile_list.append([wsf_h, wsf_v])
        # Return the list
        return wsf_tile_list


def get_wsf_tile_file(tile_h, tile_v, wsf_dataset, current_session=None, clip=112):

    # If there is no ongoing session
    if current_session is None:
        # Start a requests session
        current_session = requests.session()
    # If 2015 layer data is the target
    if wsf_dataset == "WSF2015":
        # Set target
        dataset_url = wsf_dataset + "_v2_"
    # Otherwise, if 2019 is the target
    elif wsf_dataset == "WSF2019":
        # Set target
        dataset_url = wsf_dataset + "_v1_"
    # Otherwise
    else:
        # Print warning
        print(f"{wsf_dataset} is not a valid dataset. Use WSF2015 or WSF2019.")
    print(f"https://download.geoservice.dlr.de/{wsf_dataset}/files/{dataset_url}{tile_h}_{tile_v}.tif")
    # Try to request the file
    try:
        # Request the tile file
        r = current_session.get(f"https://download.geoservice.dlr.de/{wsf_dataset}/files/{dataset_url}{tile_h}_{tile_v}.tif")
    except:
        # Start a new session
        current_session = requests.session()
        # Request the tile file
        r = current_session.get(
            f"https://download.geoservice.dlr.de/{wsf_dataset}/files/{dataset_url}{tile_h}_{tile_v}.tif")
    # If the request was succesful
    if r.status_code == 200:
        # Convert it to a numpy array
        wsf_array = tifffile.TiffFile(io.BytesIO(r.content)).pages[0].asarray()
        # Apply clip
        wsf_array = wsf_array[clip:-clip, clip:-(clip-1)]
        # Return array
        return wsf_array
    # Otherwise (not an available tile)
    else:
        # Return None
        return None

# Get the WSF proportion for a vnp tile's pixel
def get_wsf_proportion_of_vnp(tile_h, tile_v):
    # Dictionary for the VNP tile results
    vnp_dict = {}
    # Start a requests session
    current_session = requests.session()
    # Get the WSF tile names for the 25 WSF tiles that fit in a VNP tile
    wsf_tile_list = get_wsf_tiles("VNP46A", tile_h, tile_v)
    # For each WSF tile
    for wsf_tile in wsf_tile_list:
        # For 2015 and 2019
        for wsf_dataset in ["WSF2015", "WSF2019"]:
            # Get the tile file
            wsf_tile_file = get_wsf_tile_file(wsf_tile[0], wsf_tile[1], wsf_dataset, current_session=current_session)
            # If there was a tile file
            if wsf_tile_file is not None:
                print(wsf_tile)
                # For each VNP pixel h and v
                for vnp_h in np.arange(0, 480):
                    for vnp_v in np.arange(0, 480):
                        # Get the chunk indices for the wsf tile
                        h_slice_start, h_slice_end, v_slice_start, v_slice_end = get_wsf_chunk_for_vnp_pixel(vnp_h, vnp_v)
                        # Get the chunk of the array
                        wsf_chunk = wsf_tile_file[h_slice_start : h_slice_end, v_slice_start : v_slice_end]
                        # Get the denominator
                        wsf_array_size = wsf_chunk.shape[0] * wsf_chunk.shape[1]
                        # Get the numerator
                        settlement_count = np.count_nonzero(wsf_chunk > 0)
                        # Get the settlement proportion
                        settlement_proportion = settlement_count / wsf_array_size
                        # Get the VNP tile-level coordinates
                        vnp_overall_h = int(vnp_h + (480 * (np.floor(((10 + wsf_tile[0]) % 10) / 2))))
                        vnp_overall_v = int(vnp_v + (480 * (np.floor(((8 - wsf_tile[1]) % 10) / 2))))
                        # Add to the dictionary
                        if vnp_overall_h not in vnp_dict.keys():
                            vnp_dict[vnp_overall_h] = {}
                        if vnp_overall_v not in vnp_dict[vnp_overall_h].keys():
                            vnp_dict[vnp_overall_h][vnp_overall_v] = {}
                        vnp_dict[vnp_overall_h][vnp_overall_v][wsf_dataset] = settlement_proportion
                        #
                        # if settlement_count / wsf_array_size > 0.1:
                        #     print(wsf_array_size, settlement_count, settlement_count / wsf_array_size)
                        #     print(vnp_h, vnp_v)
                        #     plt.imshow(wsf_chunk)
                        #     plt.show()
    # Return the results
    return vnp_dict

def get_wsf_chunk_for_vnp_pixel(vnp_h, vnp_v):
    # Accrual rate for leftover pixels
    pixel_accrual = (22264 / 480) % 46
    # Get each of the slice indices
    h_slice_start = int(np.floor((vnp_h * 46) + (vnp_h * pixel_accrual)))
    h_slice_end = int(np.floor(((vnp_h + 1) * 46) + ((vnp_h + 1) * pixel_accrual)))
    v_slice_start = int(np.floor((vnp_v * 46) + (vnp_v * pixel_accrual)))
    v_slice_end = int(np.floor(((vnp_v + 1) * 46) + ((vnp_v + 1) * pixel_accrual)))
    # Return the slice indices
    return h_slice_start, h_slice_end, v_slice_start, v_slice_end