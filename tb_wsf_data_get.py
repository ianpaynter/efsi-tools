import requests
import tifffile
import numpy as np
from PIL import Image
from functools import partial
import io
import c_WSF
import matplotlib as mpl
from matplotlib import pyplot as plt
import json
import pickle
#
# test_arr = np.zeros((2400, 2400))
# wsf_tile = [-2, 52]
# # -10 to -2
# # 58 to 50
# vnp_h = 479
# vnp_v = 0
#
# vnp_overall_h = int(vnp_h + (480 * (np.floor(((10 + wsf_tile[0]) % 10) / 2))))
# vnp_overall_v = int(vnp_v + (480 * (np.floor(((8 - wsf_tile[1]) % 10) / 2))))
# print(vnp_overall_h, vnp_overall_v)
#


# vnp_overall_v = int(vnp_v + (480 * (np.floor(((10 + wsf_tile[0]) % 10) / 2))))
# vnp_overall_v = int(vnp_h + (480 * (np.floor(((8 - wsf_tile[1]) % 10) / 2))))
#
# test_arr[vnp_overall_v, vnp_overall_h] = 255
#
# fig = plt.figure(figsize=(10, 10))
# plt.imshow(test_arr)
# plt.scatter(vnp_overall_h, vnp_overall_v, 50, 'r', marker='x')
# plt.show()
# #print(vnp_overall_h, vnp_overall_v)
#
# exit()
# wsf_arr = c_WSF.get_wsf_tile_file(-2, 50, "WSF2019")
#
# fig = plt.figure(figsize=(10, 10))
#
# h_slice_start, h_slice_end, v_slice_start, v_slice_end = c_WSF.get_wsf_chunk_for_vnp_pixel(0, 479)
# plt.imshow(wsf_arr)
# plt.scatter(h_slice_start, v_slice_start, 15, 'r')
# plt.scatter(h_slice_start, v_slice_end, 15, 'r')
# plt.scatter(h_slice_end, v_slice_start, 15, 'r')
# plt.scatter(h_slice_end, v_slice_end, 15, 'r')
#
# #plt.imshow(wsf_arr[h_slice_start : h_slice_end, v_slice_start : v_slice_end])
# #plt.show()
#
#
# plt.show()
#
#
# exit()
# # tile_list = c_WSF.get_wsf_tiles("VNP46A", 17, 3)
# print(tile_list)



# Crapped out on -8 52
#
# vnp_h = 479
# vnp_v = 479
# wsf_tile = [-100, 8]
# print((10 + wsf_tile[0]) % 10)
# print((np.floor((abs(8 - wsf_tile[1]) % 10) / 2)))
# vnp_overall_h = int(vnp_h + (480 * (np.floor(((10 + wsf_tile[0]) % 10) / 2))))
# vnp_overall_v = int(vnp_v + (480 * (np.floor(((8 - wsf_tile[1]) % 10) / 2))))
#
# print(vnp_overall_h, vnp_overall_v)
#
# exit()

vnp_h = 17
vnp_v = 3

vnp_arr = c_WSF.get_wsf_proportion_of_vnp(vnp_h, vnp_v)

# with open(f"C:/USRA/test_wsf_h{vnp_h}v{vnp_v}", 'w') as of:
#     json.dump(vnp_dict, of)

with open(f"C:/USRA/test_wsf_h{vnp_h}v{vnp_v}_arr", 'wb') as of:
    pickle.dump(vnp_arr, of)

exit()

v_span = 0
h_span = 0



# For each VNP pixel h and v
for vnp_h in np.arange(0, 480):
    v_span = 0
    v_list = []
    for vnp_v in np.arange(0, 480):
        h_slice_start, h_slice_end, v_slice_start, v_slice_end = c_WSF.get_wsf_chunk_for_vnp_pixel(vnp_h, vnp_v)
        #print(h_slice_start, h_slice_end, v_slice_start, v_slice_end)

        v_span += v_slice_end - v_slice_start
        v_list.append(v_span)
    print(v_span)
    print(len(v_list))
    exit()
# wsf_tile_list = c_WSF.get_wsf_tiles("VNP46A2", 2, 3)
# print(wsf_tile_list)
# print(len(wsf_tile_list))
# So if there's 22488 x 22488 pixels (10 meter ish) in a WSF tile file
# And it's a 0.1 degree buffer on a 2 deg x 2 deg file, it should be 2.2 x 2.2 or...
# 1124 pixels extra on each side. (20240 x 20240)
# Never mind that if you count them in the viewer it's around 213 AND IN THE DATA 22269
# So we actually need to ignore 112 pixels at each edge (all the way round)
# s = requests.session()
# r = s.get("https://download.geoservice.dlr.de/WSF2019/files/WSF2019_v1_-72_42.tif")
# file = tifffile.TiffFile(io.BytesIO(r.content))

wsf_array = c_WSF.get_wsf_tile_file(-72, 42, "WSF2015")
print(wsf_array.shape)
plt.imshow(wsf_array)
#plt.plot([1124, 1124], [0, 4000], 'w')
plt.show()


# chunk_size = 1024

# with open(r"C:\USRA\WSF2019_v1_-100_16.tif", "rb") as f:
#     for chunk in iter(partial(f.read, chunk_size)):
#         input()

#im = Image.open(r"C:\USRA\WSF2019_v1_-100_16.tif")

#im.show()

#s = requests.session()
#r = s.get("https://download.geoservice.dlr.de/WSF2019/files/WSF2019_v1_-100_16.tif")




#im = Image.open(r.content)
#im.show()
#print(r.status_code)

#data_array = np.array(r.bytes)
#print(data_array.shape)
#tifffile.imread(np.array(r.content))
