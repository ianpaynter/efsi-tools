import numpy as np
import json
import datetime


class FUAPolygon:

    def __init__(self):

        # Polygon ID (FUA ID)
        self.id = None
        # Start date of study
        self.start_date = datetime.datetime(year=2012, month=1, day=19)
        # Years of data
        self.years = []
        # Days of year
        self.doys = []
        # Days of study (for linear plotting)
        self.doss = []
        # Datetimes
        self.dates = []
        # Any observations?
        self.any_observations = []
        # Night time lights estimates
        self.ntls = []
        # Gapfilled nighttime light estimates
        self.ntls_gapfilled = []
        self.ntls_gf_raw = []
        # Area estimates
        self.areas = []
        # Count of pixels used
        self.pixels_used = []
        # Membership metrics
        self.same_pixels = []
        self.lost_pixels = []
        self.gained_pixels = []
        # Apples to Apples (same pixels in consecutive days)
        self.apples_to_apples_ntls = []

    def load_from_json(self, path):
        # Open the first part of the time series
        with open(path, 'r') as f:
            poly_dict = json.load(f)
        # Load from dict
        self.load_from_dict(poly_dict)

    def load_from_dict(self, poly_dict):
        # Get polygon ID
        self.id = poly_dict["poly_id"]
        # For each year in the polygon data
        for year in sorted(poly_dict["observations"].keys(), key=int):
            # For each day in the year
            for doy in sorted(poly_dict["observations"][year].keys(), key=int):
                # Reference the observation dictionary
                obs_dict = poly_dict["observations"][year][doy]
                # Make a date object
                self.dates.append(self.start_date + datetime.timedelta(days=int(obs_dict["dos"])))
                self.years.append(int(obs_dict["year"]))
                self.doys.append(int(obs_dict["doy"]))
                self.doss.append(int(obs_dict["dos"]))
                # Append gapfilled (NEED TO DIVIDE BY TRUE TOTAL AREA)
                #self.ntls_gapfilled.append((obs_dict["total_gapfilled_ntl"] / (poly_dict["total_area"] * 1E10)) * 0.1)
                #self.ntls_gf_raw.append(obs_dict["total_gapfilled_ntl"] * 0.1)
                # If there were eligible pixels for this day
                if obs_dict["total_pixels"] > 0:
                    # Add to any observations
                    self.any_observations.append(True)
                    # Add the plottable attributes to the polygon
                    self.ntls.append(obs_dict["total_ntl"] / (obs_dict["total_area"] * 1E10))
                    self.areas.append(obs_dict["total_area"])
                    self.pixels_used.append(obs_dict["total_pixels"])
                    # If there were membership metrics
                    if obs_dict["px_same_as_prev"] is not None:
                        self.same_pixels.append(obs_dict["px_same_as_prev"])
                        self.lost_pixels.append(obs_dict["px_lost_since_prev"])
                        self.gained_pixels.append(obs_dict["px_gained_since_prev"])
                        if obs_dict["px_same_as_prev"] > 0:
                            self.apples_to_apples_ntls.append(
                                obs_dict["px_same_as_prev_ntl_change"] / obs_dict["px_same_as_prev"])
                        else:
                            self.apples_to_apples_ntls.append(0)
                    # Otherwise (no membership metrics)
                    else:
                        # Add 0 values
                        self.same_pixels.append(0)
                        self.lost_pixels.append(0)
                        self.gained_pixels.append(0)
                        self.apples_to_apples_ntls.append(0)
                # Otherwise (no eligible pixels)
                else:
                    # Add to any observations
                    self.any_observations.append(False)
                    # Add numpy nans
                    self.ntls.append(np.nan)
                    self.areas.append(np.nan)
                    self.pixels_used.append(np.nan)
                    # Add 0 values
                    self.same_pixels.append(np.nan)
                    self.lost_pixels.append(np.nan)
                    self.gained_pixels.append(np.nan)
                    self.apples_to_apples_ntls.append(np.nan)

    def get_time_series(self):

        clean_ntls = []
        clean_dates = []
        clean_doss = []
        obs_count = 0
        # Get the clean sequence of NTLs and DOSS
        for ntl, date, doss, obs in zip(self.ntls, self.dates, self.doss, self.any_observations):

            if obs is True:
                obs_count += 1
                clean_ntls.append(str(ntl))
                clean_dates.append(date)
                clean_doss.append(str(obs_count))

        return clean_dates, clean_ntls

    def get_rolling_average(self, rolling_average):

        clean_ntls = []
        clean_dates = []
        clean_doss = []
        # Get the clean sequence of NTLs and DOSS
        for ntl, date, doss, obs in zip(self.ntls, self.dates, self.doss, self.any_observations):
            if obs is True:
                clean_ntls.append(ntl)
                clean_dates.append(date)
                clean_doss.append(doss)
        # List for plottable rolling average
        rolling_average_dates = []
        rolling_average_rads = []

        # Window start and end
        window_start_ind = 0
        window_end_ind = 0
        wdw_start_day = clean_doss[window_start_ind]
        wdw_end_day = clean_doss[window_end_ind]

        # While the end of the window is inside the bounds of the days
        while window_end_ind + 1 < len(clean_ntls):
            # While the length of the window is less than required by the rolling average
            while wdw_end_day - wdw_start_day < rolling_average and window_end_ind + 1 < len(clean_ntls):
                # Expand the index
                window_end_ind += 1
                # Get the new candidate end day
                wdw_end_day = clean_doss[window_end_ind]
            # If the window ended up longer than the rolling average
            if wdw_end_day - wdw_start_day > rolling_average:
                # Retract the index by one
                window_end_ind -= 1
                # Get the new end day
                wdw_end_day = clean_doss[window_end_ind]
            # Get the ntl window
            ntl_window = clean_ntls[window_start_ind: window_end_ind]
            # If there is at least one observation
            if len(ntl_window) > 0:
                # Average across the window values
                rolling_average_rads.append(np.mean(clean_ntls[window_start_ind: window_end_ind]))
                # Append the midpoint day
                rolling_average_dates.append(self.start_date + datetime.timedelta(days=int(wdw_start_day + np.ceil((wdw_end_day - wdw_start_day) / 2))))
            # Move the start day index by one
            window_start_ind += 1
            # Change the start day
            wdw_start_day = clean_doss[window_start_ind]
            # Reset the end index to the start index
            window_end_ind = window_start_ind
            # Reset the end day
            wdw_end_day = clean_doss[window_end_ind]

        return rolling_average_dates, rolling_average_rads


    def get_interpolated_rolling_average(self, number_of_values, gapfilled=False):

        ra_ntls = []
        ra_window_sizes = []

        # So we want to make sure we go for all the dates
        start_date = datetime.date(year=2012, month=1, day=19)
        end_date = datetime.date(year=2021, month=10, day=25)
        date_list = [start_date + datetime.timedelta(days=x) for x in range((end_date - start_date).days + 1)]

        # For each center day
        for date in date_list:
            # Values to average
            values_to_average = []
            # Forward switch
            forward = False
            # Day delta (search window length)
            day_delta = 0
            # While we need more values to meet the required number
            while len(values_to_average) < number_of_values:
                # If looking forward
                if forward is True:
                    # Target date
                    target_date = date + datetime.timedelta(days=day_delta)
                    # Add the day delta to the date
                    if target_date in self.dates:
                        # Get the index
                        target_date_ind = self.dates.index(target_date)
                        # If the date has viable ntl data
                        if self.any_observations[target_date_ind] is True:
                            # Append ntl
                            values_to_average.append(self.ntls[target_date_ind])
                    # Flip to look backwards for the next value
                    forward = False
                # Otherwise (looking backwards)
                else:
                    # Target date
                    target_date = date - datetime.timedelta(days=day_delta)
                    # Add the day delta to the date
                    if target_date in self.dates:
                        # Get the index
                        target_date_ind = self.dates.index(target_date)
                        # If the date has viable ntl data
                        if self.any_observations[target_date_ind] is True:
                            # Append ntl
                            values_to_average.append(self.ntls[target_date_ind])
                    # Flip to look forward for the next value
                    forward = True
                    # Increment day delta
                    day_delta += 1
            # Now we have enough values, append the mean
            ra_ntls.append(np.mean(values_to_average))
            # Append the search window width
            ra_window_sizes.append((day_delta * 2) + 1)

        return date_list, ra_ntls, ra_window_sizes

    def get_plottable_rolling_average(self, rolling_average):

        clean_ntls = []
        clean_doss = []
        # Get the clean sequence of NTLs and DOSS
        for ntl, doss, obs in zip(self.ntls, self.doss, self.any_observations):
            if obs is True:
                clean_ntls.append(ntl)
                clean_doss.append(doss)
        # List for plottable rolling average
        rolling_average_days = []
        rolling_average_rads = []

        # Window start and end
        window_start_ind = 0
        window_end_ind = 0
        wdw_start_day = clean_doss[window_start_ind]
        wdw_end_day = clean_doss[window_end_ind]

        # While the end of the window is inside the bounds of the days
        while window_end_ind + 1 < len(clean_ntls):
            # While the length of the window is less than required by the rolling average
            while wdw_end_day - wdw_start_day < rolling_average and window_end_ind + 1 < len(clean_ntls):
                # Expand the index
                window_end_ind += 1
                # Get the new candidate end day
                wdw_end_day = clean_doss[window_end_ind]
            # If the window ended up longer than the rolling average
            if wdw_end_day - wdw_start_day > rolling_average:
                # Retract the index by one
                window_end_ind -= 1
                # Get the new end day
                wdw_end_day = clean_doss[window_end_ind]
            # Get the ntl window
            ntl_window = clean_ntls[window_start_ind: window_end_ind]
            # If there is at least one observation
            if len(ntl_window) > 0:
                # Average across the window values
                rolling_average_rads.append(np.mean(clean_ntls[window_start_ind: window_end_ind]))
                # Append the midpoint day
                rolling_average_days.append(wdw_start_day + np.ceil((wdw_end_day - wdw_start_day) / 2))
            # Move the start day index by one
            window_start_ind += 1
            # Change the start day
            wdw_start_day = clean_doss[window_start_ind]
            # Reset the end index to the start index
            window_end_ind = window_start_ind
            # Reset the end day
            wdw_end_day = clean_doss[window_end_ind]

        return rolling_average_days, rolling_average_rads
