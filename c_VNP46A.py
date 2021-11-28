import numpy as np


class VNP46APixel:

    def __init__(self):

        self.location = None


class VNP46A2Pixel(VNP46APixel):

    def __init__(self):

        self.laads_url = None


class FUAPolygon:

    def __init__(self):

        self.efua_id = None


class VNP46A2Tile:

    def __init__(self):

        self.name = None


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
