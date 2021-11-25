import matplotlib as mpl
from matplotlib import pyplot as plt
import dotenv
import json
import os

dotenv.load_dotenv()

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

