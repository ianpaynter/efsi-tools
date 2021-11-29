import matplotlib as mpl
from matplotlib import pyplot as plt
import dotenv
import json
import os

dotenv.load_dotenv()




#
# # Open file containing json (r = read, f = File)
# with open(f'E:/USRA/Black Marble/FUA_TS/Inputs/poly_to_tile_to_pixel.json', "r", encoding="utf-8") as f:
#     # Load dictionary from json as loaded_data
#     poly_dict = json.load(f)
#
# # New dictionary
# new_dict = {}
#
# #
# for poly in poly_dict.keys():
#     # Add to new dict
#     if poly not in new_dict.keys():
#         new_dict[poly] = {}
#     for tile in poly_dict[poly]:
#         if tile not in new_dict[poly].keys():
#             new_dict[poly][tile] = {}
#         for px_x in poly_dict[poly][tile].keys():
#             for px_y in poly_dict[poly][tile][px_x]:
#                 if px_x == 0 or px_y == 0:
#                     print(px_x, px_y)
#                     input()
#
# # Open the ASCII file containing the complete list of pixels that are part of polygons
# with open(os.environ["support_files_path"] + "FUA_polygon_pixels_output.txt", "r", encoding="utf-8") as f:
#     # Line counter
#     line_count = 0
#     # For each line in the file
#     for line in f:
#         print(line)
#         input()


with open(os.environ["support_files_path"] + "poly_to_tile_to_pixel.json", 'r') as f:
    poly_dict = json.load(f)

overall_min_x = 2400
overall_max_x = 0
overall_min_y = 2400
overall_max_y = 0

for polygon in poly_dict.keys():
    for tile in poly_dict[polygon].keys():
        tile_h = int(tile[1:3])
        tile_v = int(tile[4:6])
        x_cos = []
        y_cos = []
        for x_co in poly_dict[polygon][tile].keys():
            for y_co in poly_dict[polygon][tile][x_co].keys():
                int_x = int(x_co)
                int_y = int(y_co)

                x_cos.append(int_x)
                y_cos.append(int_y)

                if int_y < overall_min_y:
                    overall_min_y = int_y
                    print(f"Overall min Y = {overall_min_y}")
                if int_y > overall_max_y:
                    overall_max_y = int_y
                    print(f"Overall max Y = {overall_max_y}")
                if int_x < overall_min_x:
                    overall_min_x = int_x
                    print(f"Overall min X = {overall_min_x}")
                if int_x > overall_max_x:
                    overall_max_x = int_x
                    print(f"Overall max X = {overall_max_x}")

        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(1, 1, 1)
        ax.scatter(x_cos, y_cos, 3, marker='.')
        ax.set_aspect("equal")
        ax.set_xlim(0, 2400)
        ax.set_ylim(0, 2400)
        ax.set_title(f"Polygon {polygon}, Tile {tile}")
        plt.show()

