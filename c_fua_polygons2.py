import numpy as np
import config
import t_main_processing
import t_laads_tools
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor


class FUAPolygon:

    def __init__(self, input_dict=None):

        self.poly_id = None
        self.tile_id = None
        self.years = []
        self.observations = []
        self.years_dict = {}

        # If an input dictionary was provided
        if input_dict is not None:
            # Load the information from the input dictionary
            self.load_from_json(input_dict)

    # Load the data for this polygon from an input dictionary
    def load_from_json(self, input_dict):
        # Transfer poly ID and tile ID
        self.poly_id = input_dict['poly_id']
        self.tile_id = input_dict['tile_id']
        # For each year in observations
        for year in input_dict['observations'].keys():
            # Create a year object
            curr_year = Year(year)
            # Reference the year by its year in the dictionary
            self.years_dict[curr_year.year] = curr_year
            # For each observation in the year
            for observation in input_dict['observations'][year].keys():
                # Create an observation object with the dictionary
                curr_observation = Observation(input_dict['observations'][year][observation])
                # Reference in the year
                curr_year.observations.append(curr_observation)
                # Reference by its doy value in the year
                curr_year.obs_dict[curr_observation.doy] = curr_observation

    # Return a time series of the radiance as plottable variables
    def get_time_series(self, start=None, end=None, average_window=None, toa=False, apples=False):
        # NTL list
        ntl_list = []
        # For each year (in order)
        for year in sorted(self.years_dict.keys()):
            # For each observation (in order)
            for observation in sorted(self.years_dict[year].obs_dict.keys()):
                # Append the NTL / area
                ntl_list.append(observation.total_ntl / (observation.total_area * 1E10))

    # Return an NTL value from a rolling average window list
    def get_rolling_average_value(self, active_window):
        # Reduce the list to exclude the None values
        ntl_values = [x for x in active_window if x != None]
        # If there are any usable values in the ntl values from the windows
        if len(ntl_values) > 0:
            # Return the mean of the values in the window
            return np.mean(ntl_values)
        # Otherwise
        else:
            # Append a numpy NaN
            return np.nan

    # Return the rolling average from the NTL based on a specified window length
    def get_rolling_average(self, window_length):
        # Active window
        active_window = []
        # Rolling average (we want 1 value per day if possible)
        rolling_average = []
        # Observation (day) counter
        observation_counter = 0
        # For each year (in order)
        for year_key in sorted(self.years_dict.keys()):
            # Reference the year
            year = self.years_dict[year_key]
            # For each observation (in order)
            for observation_key in sorted(year.obs_dict.keys()):
                # Reference the observation object
                observation = year.obs_dict[observation_key]
                # Iterate observation counter
                observation_counter += 1
                # If there was sampled area
                if observation.total_area > 0:
                    # Append the NTL / area to the window
                    active_window.append(observation.total_ntl / (observation.total_area * 1E10))
                # Otherwise (no pixels available for NTL)
                else:
                    # Append a None
                    active_window.append(None)
                # If the active window has reached more than half the length (start of actually recording values)
                if len(active_window) > window_length / 2:
                    # Get a value from the window
                    rolling_average.append(self.get_rolling_average_value(active_window))
                # If the active window has grown to the length of the window
                if len(active_window) == window_length:
                    # Pop the oldest value
                    active_window.pop(0)
        # While there are less ntl values than observations
        while len(rolling_average) < observation_counter:
            # Pop the oldest value
            active_window.pop(0)
            # Get a value from the window
            rolling_average.append(self.get_rolling_average_value(active_window))
        # Return the rolling average
        return rolling_average

    # Get the last year/day of data in the time series
    def get_latest(self):
        # Latest year
        latest_year = sorted(self.years_dict.keys(), key=int)[-1]
        # Latest day
        latest_day = sorted(self.years_dict[latest_year].obs_dict.keys(), key=int)[-1]
        # Return year and day
        return latest_year, latest_day


class Year:

    def __init__(self, year):

        self.year = int(year)
        self.observations = []
        self.obs_dict = {}


class Observation:

    def __init__(self, input_dict=None):

        self.year = None
        self.doy = None
        self.dos = None
        self.total_ntl = None
        self.total_area = None
        self.total_pixels = None
        self.filled_pixels = None
        self.poor_quality_pixels = None
        self.ephemeral_pixels = None
        self.snow_ice_pixels = None
        self.px_same_as_prev = None
        self.px_lost_since_prev = None
        self.px_gained_since_prev = None
        self.px_same_as_prev_ntl_change = None

        # If there was an input dictionary provided
        if input_dict is not None:
            # For each attribute
            for attr in input_dict.keys():
                # If the attr is not the ntl or area
                if attr != "total_ntl" and attr != "total_area":
                    # If the attribute value is not None
                    if input_dict[attr] is not None:
                        # Transfer the attribute as an int
                        setattr(self, attr, int(input_dict[attr]))
                    # Otherwise
                    else:
                        # Set as None
                        setattr(self, attr, None)
                # Otherwise (total ntl or area)
                else:
                    # If the attribute value is not None
                    if input_dict[attr] is not None:
                        # Transfer the attribute as a float
                        setattr(self, attr, float(input_dict[attr]))
                    # Otherwise
                    else:
                        # Set as None
                        setattr(self, attr, None)


# Update a polygon's time series from LAADS
def update_timeseries(polygon, urls_file):
    # Get the latest year/day
    latest_year, latest_day = polygon.get_latest()
    # Make a tile list
    tile_list = list(t_main_processing.poly_to_tile_to_pixel[polygon.poly_id].keys())
    # Update the tiles
    update_multiple_tiles(tile_list, urls_file, latest_year, latest_day)


def update_multiple_tiles(tile_list, urls_file, latest_year, latest_day):

    # If the tile list is a single tile
    if isinstance(tile_list, list) is False:
        # Encapsulate in a list
        tile_list = [tile_list]

    # Create a LAADS session
    currSession = t_laads_tools.connect_to_laads()

    # Start a ProcessPoolExecutor
    process_exec = ProcessPoolExecutor(max_workers=5)
    # Submit the tiles
    for tile in tile_list:
        process_exec.submit(update_tile, tile, urls_file, latest_year, latest_day, laads_session=currSession)
        print(f'Processing {tile}')


def update_tile(tile_id, urls_file, latest_year, latest_day, laads_session=None):
    # If there is no existing session
    if laads_session is None:
        # Create a session
        laads_session = t_laads_tools.connect_to_laads()
    # Create tile object
    currTile = t_main_processing.VNP46A2Tile(tile_id)
    # For each Polygon in the tile
    for poly_id in t_main_processing.tile_to_poly[tile_id]:
        # Create a polygon object
        currTile.polygons.append(t_main_processing.FUAPolygon(poly_id, tile_id))
    for year in sorted(urls_file[tile_id].keys(), key=int):
        #print(year < latest_year)
        if int(year) < latest_year:
            continue
        for doy in sorted(urls_file[tile_id][year].keys(), key=int):
            if int(year) == latest_year and int(doy) < latest_day:
                continue
            print(f"Processing day {doy} of {year}")
            # Get the URL for the VNP46A2 file
            target_file_url = urls_file[tile_id][year][doy]
            # Assemble the full URL
            target_url = f"{config.VNP46A2_base_url}{year}/{doy}/{target_file_url}"
            # Get the H5 file on LAADS
            h5file = t_laads_tools.get_VNP46A2_file(laads_session, target_url)
            # While the status of the return is False (incomplete file?)
            while h5file is False:
                # Retry the request
                h5file = t_laads_tools.get_VNP46A2_file(laads_session, target_url)
            # Make numpy arrays of NTL data, Quality flags, and snow flags
            ntl_data = np.array(h5file['HDFEOS']['GRIDS']['VNP_Grid_DNB']['Data Fields']['DNB_BRDF-Corrected_NTL'])
            qa_flags = np.array(h5file['HDFEOS']['GRIDS']['VNP_Grid_DNB']['Data Fields']['Mandatory_Quality_Flag'])
            snow_flags = np.array(h5file['HDFEOS']['GRIDS']['VNP_Grid_DNB']['Data Fields']['Snow_Flag'])
            # For each polygon
            for polygon in currTile.polygons:
                # Create an observation object
                currObs = t_main_processing.Observation(int(year), int(doy), t_main_processing.get_dos(year, doy), polygon)
                # Append the observation to the polygon
                polygon.observations.append(currObs)
                # For each pixel x
                for px_x in t_main_processing.poly_to_tile_to_pixel[polygon.id][tile_id].keys():
                    # For each pixel y
                    for px_y in t_main_processing.poly_to_tile_to_pixel[polygon.id][tile_id][px_x].keys():
                        # Get the NTL datum
                        ntl_datum = int(ntl_data[int(px_y)][int(px_x)])
                        # If the NTL datum is not a fill value
                        if ntl_datum != 65535:
                            # If the QA flag is not poor
                            if int(qa_flags[int(px_y)][int(px_x)]) != 2:
                                # If the pixel is not flagged for snow/ice:
                                if int(snow_flags[int(px_y)][int(px_x)]) != 1:
                                    # If the pixel is flagged for ephemerality (QA Flag value 1)
                                    if int(qa_flags[int(px_y)][int(px_x)]) == 1:
                                        # Add to count
                                        currObs.ephemeral_pixels += 1
                                    # Apply the 0.1 scale factor to convert to nW / cm^2 / sr
                                    ntl_datum *= 0.1
                                    # Add the pixel coordinates and value to pixel dictionary
                                    if px_x not in currObs.px_dict.keys():
                                        currObs.px_dict[px_x] = {}
                                    # Adjust the NTL value for the area of its pixel (weighting the sample by area)
                                    ntl_datum *= t_main_processing.poly_to_tile_to_pixel[polygon.id][tile_id][px_x][px_y] * 1E10
                                    # Store the NTL value
                                    currObs.px_dict[px_x][px_y] = ntl_datum
                                    # Add to pixel count
                                    currObs.total_pixels += 1
                                    # Add to total NTL
                                    currObs.total_ntl += ntl_datum
                                    # Add to total area for the observation
                                    currObs.total_area += t_main_processing.poly_to_tile_to_pixel[polygon.id][tile_id][px_x][px_y]
                                # Otherwise (snow/ice)
                                else:
                                    # Add to count
                                    currObs.snow_ice_pixels += 1
                            # Otherwise (bad QA Flag)
                            else:
                                # Add to poor QA flag count
                                currObs.poor_quality_pixels += 1
                                # Check if there was also a snow/ice flag
                                if int(snow_flags[int(px_y)][int(px_x)]) == 1:
                                    # Add to count
                                    currObs.snow_ice_pixels += 1
                            # Otherwise (filed value)
                        else:
                            currObs.filled_pixels += 1
                # Deal with the membership metrics etc. for the previous observation
                currObs.compareToPrev()
                # Set the polygon's previous observation to the current observation
                polygon.prev_obs = currObs
            # Print update
        print(f'Year {year} processed for tile {tile_id}')
    # For each polygon
    for polygon in currTile.polygons:
        # Save the dictionary for the polygon (polyid_tile.json)
        polygon.save(suffix=f"_{latest_year}{latest_day}")
    # Print update
    print(f'Finished processing {tile_id}')


