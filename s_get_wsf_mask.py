import c_WSF
import os
import dotenv
import pickle
import numpy as np

# Function for getting tile name from vnp h and v
def get_vnp_tile_name(vnp_h, vnp_v):
    # Padded vnp_h
    padded_vnp_h = str(vnp_h)
    # If the string needs padding with a 0
    if len(padded_vnp_h) < 2:
        # Prepend a 0
        padded_vnp_h = '0' + padded_vnp_h
    # Padded vnp_v
    padded_vnp_v = str(vnp_v)
    # If the string needs padding with a 0
    if len(padded_vnp_v) < 2:
        # Prepend a 0
        padded_vnp_v = '0' + padded_vnp_v
    # Return the tile name
    return 'h' + padded_vnp_h + 'v' + padded_vnp_v

# Load environmental variables from .env file
dotenv.load_dotenv()

# List for previously completed tiles
previously_completed = []

# Walk the results directory
for root, dirs, files in os.walk(os.environ["wsf_vnp_results_path"]):
    # For each file name
    for name in files:
        # If it is a results file
        if "wsf_for_vnp" in name:
            # Split the name
            split_name = name.split('_')
            # Append the tile name to previously completed
            previously_completed.append(split_name[3])
        # Otherwise, if is it is the list of tiles with no wsf data
        elif "tiles_with_no_wsf" in name:
            # Open the file
            no_wsf_file = open(os.path.join(os.environ["wsf_vnp_results_path"], name), 'r')
            # For each tile name in the file
            for line in no_wsf_file:
                # Append the tile name stripped of newline
                previously_completed.append(line.strip())
# Convert previously completed list to set for faster searching
previously_completed = set(previously_completed)

# For each VNP tile in the h direction
for vnp_h in np.arange(0, 36):
    # For each VNP tile in the v direction
    for vnp_v in np.arange(0, 18):
        # Get the tile name
        tile_name = get_vnp_tile_name(vnp_h, vnp_v)
        # If the tile name was not already processed
        if tile_name not in previously_completed:
            # Print message
            print(f"Processing tile {tile_name}.")
            # Get the array of results for the tile
            wsf_array, any_wsf_tiles = c_WSF.get_wsf_proportion_of_vnp(vnp_h, vnp_v)
            # If there were any wsf tiles for the VNP46A tile
            if any_wsf_tiles is True:
                # Print a message
                print(f"Saving array for {tile_name}.")
                # Open a file for the array
                with open(os.path.join(os.environ["wsf_vnp_results_path"], f"wsf_for_vnp_{tile_name}"), 'wb') as of:
                    # Save the array
                    pickle.dump(wsf_array, of)
            # Otherwise (no WSF tiles)
            else:
                # Print a message
                print(f"No WSF data for {tile_name}.")
                # Open the file
                no_wsf_file = open(os.path.join(os.environ["wsf_vnp_results_path"], "tiles_with_no_wsf"), 'w')
                # Write a new line
                no_wsf_file.write(f"{tile_name}\n")
                # Close the file
                no_wsf_file.close()
        # Otherwise (tile previously completed)
        else:
            # Print message
            print(f"Tile {tile_name} was processed previously.")
