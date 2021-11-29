import numpy as np
import pickle
import


class PolyInfoDict:

    __slots__: ["dictionary"]

    def __init__(self):

        # Load polygon information dictionary
        with open(f'{interrim_path}poly_info.json') as f:
            poly_info = json.load(f)
        # Reference
        self.dictionary = poly_info


class PolyTilePixelDict:

    __slots__: ["dictionary"]

    def __init__(self):

        # Load polygon > tile > pixel > area dictionary
        with open(f'{interrim_path}poly_to_tile_to_pixel.json') as f:
            poly_to_tile_to_pixel = json.load(f)
        # Reference dictionary
        self.dictionary = poly_to_tile_to_pixel


class TilePolyDict:

    __slots__: ["dictionary"]

    def __init__(self):

        # Load tile > polygon dictionary
        with open(f'{interrim_path}tile_to_poly.json') as f:
            tile_to_poly = json.load(f)
        # Reference the loaded dictionary
        self.dictionary = tile_to_poly


class TimeSyncSession:

    def __init__(self):

        # Grab the support dictionaries you might want
        self.poly_tile_pixel = PolyTilePixelDict()
        self.tile_poly = TilePolyDict()
        # Current target tile name
        self.target_tile = None

    def set_target_tile(self, tile_name, wsf_threshold=None):
        # Change the target tile to the supplied tile
        self.target_tile = tile_name
        # Open the URLs file
        with open()

        # Return the time sync dictionary
        return  self.get_time_sync_dict(data_product, self.target_tile, wsf_threshold)


    def get_time_sync_tile(self, data_product, tile_name, wsf_threshold=None, start_date=None, end_date=None):
        # Change the target tile to the supplied tile
        self.target_tile = tile_name
        # Get the time sync dictionary
        time_sync_dict = self.get_time_sync_dict(data_product, self.target_tile, wsf_threshold)
        # Kick off the parallel process
        get_time_sync_tile()

    # Get a time sync dictionary (which pixels for which product) for a VNP46A tile
    def get_time_sync_dict(self, data_product, tile, wsf_threshold=None):
        # Time sync dictionary
        time_sync_dict = {}
        # If the data product is VNP46A2
        if data_product == "VNP46A2":
            # Open the appropriate WSF file
            with open(os.path.join(os.environ["wsf_vnp_results_path"], "wsf_for_vnp_" + tile), 'rb') as f:
                # Load the numpy array
                wsf_array = pickle.load(f)
            # For each column in keys
            for vnp_h, vnp_col in enumerate(wsf_array):
                # For each row
                for vnp_v, wsf_values in enumerate(vnp_col):
                    # If there is a wsf threshold
                    if wsf_threshold is not None:
                        # If the value in either year is greater than the threshold
                        if wsf_values[0] > wsf_threshold or wsf_values[1] > wsf_threshold:
                            # Add the coordinates to the time sync dict
                            if vnp_h not in time_sync_dict.keys():
                                time_sync_dict[vnp_h] = {}
                            if vnp_v not in time_sync_dict[vnp_h].keys():
                                time_sync_dict[vnp_h][vnp_v] = []
                            # Add the WSF tag to indicate the pixel should be stored with the WSF
                            time_sync_dict[vnp_h][vnp_v].append("WSF")
            # Get the FUA polygons in the tile
            polys_in_tile = self.tile_poly.dictionary[tile]
            # For each FUA polygon id
            for poly_id in polys_in_tile:
                # For each pixel in the poly in the tile
                for vnp_h in self.poly_tile_pixel[poly_id][tile].keys():
                    for vnp_v in self.poly_tile_pixel[poly_tile_pixel][poly_id][tile][vnp_h].keys():
                        # Add to the time sync dictionary
                        if vnp_h not in time_sync_dict.keys():
                            time_sync_dict[vnp_h] = {}
                        if vnp_v not in time_sync_dict[vnp_h].keys():
                            time_sync_dict[vnp_h][vnp_v] = []
                        # Add the FUA tag to indicate the pixel should be stored with the WSF
                        time_sync_dict[vnp_h][vnp_v].append("FUA")
        # Return the dictionary
        return time_sync_dict


# For calculating top and bottom lengths for pixel
def longitude_distance(latitude):
    # Convert latitude to radians
    latitude = np.radians(latitude)
    # Calculate degrees of longitude for one pixel
    long_degs_per_pixel = 360 / 86400
    # Return longitudinal distance given latitude
    return long_degs_per_pixel * ((111.41288 * (np.cos(latitude))) - (0.09350 * (np.cos(3 * latitude))) + (
            0.00012 * (np.cos(5 * latitude))))


# For calculating height of pixel
def latitude_distance(latitude):
    # Convert latitude to radians
    latitude = np.radians(latitude)
    # Calculate degrees of latitude for one pixel
    lat_degs_per_pixel = 180 / 43200
    # Return latitudinal distance given latitude
    return lat_degs_per_pixel * 111.13295 - 0.55982 * np.cos(2 * latitude) + 0.00117 * np.cos(4 * latitude)


# Pixel latitudes (top and bottom of pixel) given the y coordinate of the pixel (where 0 is at the top)
def pixel_lat(y_co):
    # Degrees per pixel
    lat_degs_per_pixel = 180 / 43200
    # Pixel top and bottom latitudes
    pixel_top_lat = 90 - (y_co * lat_degs_per_pixel)
    pixel_bottom_lat = 90 - ((y_co + 1) * lat_degs_per_pixel)
    # Return top and bottom lats
    return pixel_top_lat, pixel_bottom_lat


# Derive true area of pixel given y coordinate (0 is top "row" of the world)
def get_pixel_area(global_y):
    # Retrieve pixel top and bottom latitudes
    pixel_top_lat, pixel_bottom_lat = pixel_lat(global_y)
    # Retrieve pixel top and bottom distances
    pixel_top_dist = longitude_distance(pixel_top_lat)
    pixel_bottom_dist = longitude_distance(pixel_bottom_lat)

    # Retrieve pixel "height" distance based on top latitude
    pixel_height = latitude_distance(pixel_top_lat)
    # Trapezoid approximation of area
    pixel_area = ((pixel_top_dist + pixel_bottom_dist) / 2) * pixel_height
    # Convert area from km^2 to cm^2
    pixel_area *= 1e10

    # Return area as trapezoid approximation
    return ((pixel_top_dist + pixel_bottom_dist) / 2) * pixel_height
