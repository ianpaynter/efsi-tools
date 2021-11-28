import numpy as np
import json
import c_VNP46A
import os
import dotenv

# Load environmental variables from .env file
dotenv.load_dotenv()

# First script to run. Needs to be run any time a new polygon is added, or the polygons are updated.
# Takes a list of the pixels that are contained in any polygon from ENVI
# Retrieves an exclusive and inclusive list of tiles that contain pixels from at least one FUApolygon

# There are 36 tiles horizontally, each 1,200 columns
# There are 18 tile vertically, each 1,200 rows
# The output is for 500 meter pixels (2,400 x 2,400 pixels)

# Dictionary for poly : tile : pixel records
poly_dict = {}
# Dictionary for tile : poly records
tile_dict = {}

# Open the ASCII file containing the complete list of pixels that are part of polygons
with open(os.path.join(os.environ["support_files_path"], "FUA_polygon_pixels_output.txt"), "r", encoding="utf-8") as f:
    # Line counter
    line_count = 0
    # For each line in the file
    for line in f:
        # Skip some lines for header
        if line_count <= 7:
            # Iterate line count
            line_count += 1
            # End loop
            continue
        # Split the line
        curr_line = line.split()
        # Get essential components
        pix_x = int(curr_line[0])
        pix_y = int(curr_line[1])
        poly_id = curr_line[2]
        # Get the tile numbers
        tile_h = str(int(np.floor(pix_x / 1200)))
        tile_v = str(int(np.floor(pix_y / 1200)))
        # Assemble the tile name
        if len(tile_h) < 2:
            # Add a zero
            tile_h = '0' + tile_h
        if len(tile_v) < 2:
            # Add a zero
            tile_v = '0' + tile_v
        tile_name = 'h' + tile_h + 'v' + tile_v
        # If the tile is not in the tile dict
        if tile_name not in tile_dict.keys():
            # Add it with a list for polygons
            tile_dict[tile_name] = []
        # Add the polygon to the tile's list
        tile_dict[tile_name].append(poly_id)
        # If the ID is not in the poly dictionary keys
        if poly_id not in poly_dict.keys():
            # Add a subdict
            poly_dict[poly_id] = {}
        # If the tile name is not in the subdict
        if tile_name not in poly_dict[poly_id].keys():
            # Add a subdict
            poly_dict[poly_id][tile_name] = {}
        # Get within-tile x and y
        in_tile_x = pix_x % 1200
        in_tile_y = pix_y % 1200
        # Convert the pixel into 4 x 500 meter pixels
        new_pixels = [
            [int(in_tile_x * 2), int(in_tile_y * 2)],
            [int(in_tile_x * 2), int((in_tile_y * 2) + 1)],
            [int((in_tile_x * 2) + 1), int(in_tile_y * 2)],
            [int((in_tile_x * 2) + 1), int((in_tile_y * 2) + 1)]
        ]
        # For each new pixel
        for new_pixel in new_pixels:
            # If the x is not in the subdictionary for the tile
            if new_pixel[0] not in poly_dict[poly_id][tile_name].keys():
                # Add a subdict
                poly_dict[poly_id][tile_name][new_pixel[0]] = {}
            # Get adjusted global y
            adj_global_y = pix_y + ((new_pixel[1] - (in_tile_y * 2)) / 2)
            # Save the pixel's adjusted area. Why the heck not?
            poly_dict[poly_id][tile_name][new_pixel[0]][new_pixel[1]] = c_VNP46A.get_pixel_area(adj_global_y)

# Save the tile dictionary
# Open new file to save dictionary as json (of = Output File)
with open(os.path.join(os.environ["support_files_path"], "tile_to_poly.json"), "w", encoding="utf-8") as of:
    # Save dictionary as json, indent=4 adds indentation
    json.dump(tile_dict, of, indent=4)

# Save the polygon dictionary
# Open new file to save dictionary as json (of = Output File)
with open(os.path.join(os.environ["support_files_path"], "poly_to_tile_to_pixel.json"), 'w', encoding="utf-8") as of:
    # Save dictionary as json, indent=4 adds indentation
    json.dump(poly_dict, of, indent=4)

# Empty dictionary to contain polygon info.
polygon_info_dict = {}

# Open the ASCII file containing the list of polygons, their IDs, names, and countries.
with open(os.path.join(os.environ["support_files_path"], "GHS_FUA_Reference_Summary.txt"), 'r') as f:
    # Line counter
    line_count = 0
    # For each line in the file
    for line in f:
        # Skip some lines for header
        if line_count <= 0:
            # Iterate line count
            line_count += 1
            # End loop
            continue
        # Split the line
        currLine = line.split('\t')
        # Make a dictionary entry with the polygon ID as key
        # And a list containing eFUA_id, the city name, country ISO code, and country name
        polygon_info_dict[currLine[0]] = [currLine[1], currLine[2], currLine[3], currLine[4].strip()]

# Save the polygon info dictionary
# Open new file to save dictionary as json (of = Output File)
with open(os.path.join(os.environ["support_files_path"], "poly_info.json"), "w", encoding="utf-8") as of:
    # Save dictionary as json, indent=4 adds indentation
    json.dump(polygon_info_dict, of, indent=4, ensure_ascii=False)
