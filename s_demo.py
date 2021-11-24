import t_laads_tools
import json

# with open(f"C:/USRA/support_files/VNP46A2_laads_urls_11182021.json", 'r') as f:
#     tile_dict = json.load(f)
#
# for tile in tile_dict.keys():
#     for year in tile_dict[tile].keys():
#         print(tile_dict[tile].keys())
#         print(tile_dict[tile][year].keys())
#         exit()

# print(tile_dict.keys())
# print(len(tile_dict.keys()))

t_laads_tools.get_VNP46A_availability("VNP46A2")