import json
import matplotlib as mpl
from matplotlib import pyplot as plt
import c_VNP46A
import numpy as np


# Set matplotlib defaults for fonts
mpl.rc('font', family='Times New Roman')
mpl.rc('axes', labelsize=14)
mpl.rc('axes', titlesize=14)
mpl.rc('xtick', labelsize=12)
mpl.rc('ytick', labelsize=12)

global_ys = []
areas = []

# For the full y-range of pixels
for global_y in np.arange(0, 43200):
    global_ys.append(global_y)
    areas.append(c_VNP46A.get_pixel_area(global_y))

fig = plt.figure(figsize=(6, 6))
ax = fig.add_subplot(1, 1, 1)
VNP462_pixels = ax.scatter(global_ys, areas, 1, 'r', label="VNP46A2 Pixels")
ax.set_xlabel("Pixel v coordinate (North = 0, South = 43199)")
ax.set_ylabel("Pixel area (km$^2$)")
ax.set_title("VNP46A2 Pixel Area by Latitude (Trapezoid Approximation)")
equator, = ax.plot([21620, 21620], [0, 0.23], linestyle='--', color='k', label="Equator")
plt.legend(edgecolor='k')
#plt.legend([VNP462_pixels, equator], labels=["VNP46A2 Pixels", "Equator"], edgecolor='k')
plt.show()


# with open("F:/USRA/FUA_Processing/files/poly_to_tile_to_pixel.json", 'r') as f:
#     old_poly_dict = json.load(f)
#
# global_ys = []
# areas = []
#
# for poly_id in old_poly_dict.keys():
#     for tile_id in old_poly_dict[poly_id].keys():
#         # Get the tile v
#         tile_v = tile_id[4:]
#         tile_h = tile_id[1:3]
#         if tile_h == "35":
#             tile_v = int(tile_v)
#             for pix_x in old_poly_dict[poly_id][tile_id].keys():
#                 for pix_y in old_poly_dict[poly_id][tile_id][pix_x].keys():
#                     # Get the global y
#                     global_y = (tile_v * 2400) + int(pix_y)
#                     # Append y and area
#                     global_ys.append(global_y)
#                     areas.append(old_poly_dict[poly_id][tile_id][pix_x][pix_y])
#
# fig = plt.figure(figsize=(10, 10))
# ax = fig.add_subplot (1, 1, 1)
# ax.scatter(global_ys, areas, 1, 'r')
# plt.show()