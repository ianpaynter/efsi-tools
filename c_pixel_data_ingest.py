import datetime
import json
import numpy as np


class PixelDataBlock:

    def __init__(self, json_path):

        self.pixel_dict = {}
        self.dates = []

        # Open specified json
        with open(json_path, 'r') as f:
            in_dict = json.load(f)
        # Load data into dictionary
        for date_key in in_dict.keys():
            self.pixel_dict[date_key] = {}
            for col_key in in_dict[date_key].keys():
                if int(col_key) not in self.pixel_dict[date_key].keys():
                    self.pixel_dict[date_key][int(col_key)] = {}
                for row_key in in_dict[date_key][col_key]:
                    self.pixel_dict[date_key][int(col_key)][int(row_key)] = in_dict[date_key][col_key][row_key]
        # Set the full date series
        self.set_full_date_series()

    def set_full_date_series(self):
        # For each date key
        for date_key in self.pixel_dict.keys():
            # Split the key
            split_key = date_key.split("_")
            # Append a datetime date object to the list
            self.dates.append(datetime.date(year=int('20' + split_key[0]),
                                            month=int(split_key[1]),
                                            day=int(split_key[2])))
        # Sorted the date objects
        self.dates = sorted(self.dates)
        # Get the first date object
        prev_date = self.dates[0]
        # Dates to add
        dates_to_add = []
        # For each date afterwards
        for date_obj in self.dates[1:]:
            # While the date is more than 1 day since the previous
            while (date_obj - prev_date).days > 1:
                # Create a new date at + 1 day
                new_date = datetime.date(year=prev_date.year,
                                         month=prev_date.month,
                                         day=prev_date.day) + datetime.timedelta(days=1)
                # Reference in dates to add
                dates_to_add.append(new_date)
                # Reference as previous date
                prev_date = new_date
            # Reference current date as previous
            prev_date = date_obj
        # Add the dates
        self.dates.extend(dates_to_add)
        # Sort the dates in place
        self.dates = sorted(self.dates)

    def get_observation(self, date_obj, row, column):
        # Make a date key
        date_key = date_obj.strftime("%y_%m_%d")
        # If the date_obj is available in the dictionary
        if date_key in self.pixel_dict.keys():
            # Reference the results dictionary
            results_dict = self.pixel_dict[date_key][column][row]
            # If not a fill value
            if results_dict["ntl_datum"] != 65535:
                # If the QA flag is not poor
                if results_dict["qa_flag"] != 2:
                    # If the pixel is not flagged for snow/ice:
                    if results_dict["snow_flag"] != 1:
                        # Return the value
                        return results_dict["ntl_datum"]
        # Otherwise (failed any of the above) return numpy nan
        return np.nan

    def get_date_inds(self, start_date, end_date):
        # If there was a start date specified
        if start_date is not None:
            # If start date in dates
            if start_date in self.dates:
                # Starting index in dates
                start_ind = self.dates.index(start_date)
            # Otherwise
            else:
                # Print warning
                print(f"Start date {start_date} not in timeseries ({self.dates[0]} - {self.dates[-1]})")
                # Cancel the whole darn thing
                exit()
        # Otherwise (no start date specified)
        else:
            # Starting index
            start_ind = 0
        # If there was an end date specified
        if end_date is not None:
            # If end date in dates
            if end_date in self.dates:
                # Ending index in dates
                end_ind = self.dates.index(end_date) + 1
            # Otherwise
            else:
                # Print warning
                print(f"End date {end_date} not in timeseries ({self.dates[0]} - {self.dates[-1]})")
                # Cancel the whole darn thing
                exit()
        # Otherwise (no end date specified)
        else:
            # Starting index
            end_ind = len(self.dates)

        return start_ind, end_ind

    def get_time_series(self, row, column, start_date=None, end_date=None):
        # Clean time series
        clean_ntls = []
        # Get start and end indices
        start_ind, end_ind = self.get_date_inds(start_date, end_date)
        # For each date key
        for date_obj in self.dates[start_ind:end_ind]:
            # Add NTL or fill value
            clean_ntls.append(self.get_observation(date_obj, row, column))

        # Return date objects and ntls
        return self.dates[start_ind:end_ind], clean_ntls

    def get_rolling_average(self,
                            row,
                            column,
                            sample_size,
                            fixed_window=True,
                            previous_days_only=False,
                            get_window_size=False,
                            start_date=None,
                            end_date=None):
        # List for rolling average NTLs
        ra_ntls = []
        # Get start and end ind
        start_ind, end_ind = self.get_date_inds(start_date, end_date)
        # If we are returning the window size
        if get_window_size is True:
            # Lost for rolling window sizes
            ra_window_sizes = []
        # If we are not fixing the window width
        if fixed_window is False:
            # For each center day
            for date in self.dates[start_ind:end_ind]:
                # Values to average
                values_to_average = []
                # Forward switch
                forward = False
                # Day delta (search window length)
                day_delta = 0
                # While we need more values to meet the required number
                while len(values_to_average) < sample_size:
                    # If the day delta has become longer than the timeseries
                    if day_delta > len(self.dates):
                        # Stop trying
                        break
                    # If looking forward
                    if forward is True:
                        # Add the day delta to the date
                        target_date = date + datetime.timedelta(days=day_delta)
                        # If the target date is in the timeseries
                        if target_date in self.dates:
                            # Get the observation
                            target_obs = self.get_observation(target_date, row, column)
                            # If the observation is not a nan
                            if (target_obs is np.nan) is False:
                                # Append ntl
                                values_to_average.append(target_obs)
                        # Flip to look backwards for the next value
                        forward = False
                    # Otherwise (looking backwards)
                    else:
                        # Target date
                        target_date = date - datetime.timedelta(days=day_delta)
                        # If the target date is in the timeseries
                        if target_date in self.dates:
                            # Get the observation
                            target_obs = self.get_observation(target_date, row, column)
                            # If the observation is not a nan
                            if (target_obs is np.nan) is False:
                                # Append ntl
                                values_to_average.append(target_obs)
                        # If we're not only looking backwards
                        if previous_days_only is False:
                            # Flip to look forward for the next value
                            forward = True
                        # Increment day delta
                        day_delta += 1
                # If there are any values
                if len(values_to_average) > 0:
                    # Now we have enough values, append the mean
                    ra_ntls.append(np.mean(values_to_average))
                # Otherwise
                else:
                    # Append a nan
                    ra_ntls.append(np.nan)
                # If we are collecting window size
                if get_window_size is True:
                    # Append the search window width
                    ra_window_sizes.append((day_delta * 2) + 1)

        # Otherwise (window width is fixed)
        else:
            # For each center day
            for date in self.dates[start_ind:end_ind]:
                # Values to average
                values_to_average = []
                # If we're not only looking backwards
                if previous_days_only is False:
                    # Get the window start index
                    window_start_ind = int(self.dates.index(date) - np.floor(sample_size / 2))
                # Otherwise (using previous data only)
                else:
                    # Get the window start index
                    window_start_ind = int(self.dates.index(date) - (sample_size - 1))
                # If the window start is less than 0
                if window_start_ind < 0:
                    # Set to 0
                    window_start_ind = 0
                # If we're not only looking backwards
                if previous_days_only is False:
                    # Get the window end index
                    window_end_ind = int(self.dates.index(date) + np.ceil((sample_size / 2) - 1))
                    # If the window end is beyond the date list length - 1
                    if window_end_ind > len(self.dates) - 1:
                        # Set it as such
                        window_end_ind = len(self.dates) - 1
                # Otherwise (using previous data only)
                else:
                    # Set end of window to current date
                    window_end_ind = int(self.dates.index(date))
                #print(np.arange(window_start_ind, window_end_ind + 1))
                # For each date index
                for date_ind in np.arange(window_start_ind, window_end_ind + 1):
                    # Get the observation
                    target_obs = self.get_observation(self.dates[date_ind], row, column)
                    # If the observation is not a nan
                    if (target_obs is np.nan) is False:
                        # Append ntl
                        values_to_average.append(target_obs)
                # If there are any values to average
                if len(values_to_average) > 0:
                    # Append the mean
                    ra_ntls.append(np.mean(values_to_average))
                # Otherwise (no viable values)
                else:
                    # Append a nan
                    ra_ntls.append(np.nan)
                # If we are collecting window size
                if get_window_size is True:
                    # Append the search window width
                    ra_window_sizes.append(len(values_to_average))

        if get_window_size is False:

            return self.dates[start_ind:end_ind], ra_ntls

        # Otherwise (returning window size)
        else:

            return self.dates[start_ind:end_ind], ra_ntls, ra_window_sizes