from concurrent.futures import ProcessPoolExecutor
import c_VNP46A
import t_laads_tools
import datetime

def process_time_sync_file(target_url, tile_dict, current_session):

    # Get the file from LAADS
    h5file = t_laads_tools.get_VNP46A_file()
    # While the status of the return is False (incomplete file?)
    while h5file is None:
        # Retry the request
        h5file = t_laads_tools.get_VNP46A2_file(curr_session, target_url[0])
    # For each data field
    # Make numpy arrays of NTL data, GapFilled data Quality flags, and snow flags
    ntl_data = np.array(h5file['HDFEOS']['GRIDS']['VNP_Grid_DNB']['Data Fields']['DNB_BRDF-Corrected_NTL'])
    gf_data = np.array(
        h5file['HDFEOS']['GRIDS']['VNP_Grid_DNB']['Data Fields']['Gap_Filled_DNB_BRDF-Corrected_NTL'])
    qa_flags = np.array(h5file['HDFEOS']['GRIDS']['VNP_Grid_DNB']['Data Fields']['Mandatory_Quality_Flag'])
    snow_flags = np.array(h5file['HDFEOS']['GRIDS']['VNP_Grid_DNB']['Data Fields']['Snow_Flag'])

    # Results dict
    results_dict = {}
    # For each pixel x
    for px_x in x_cos:
        if int(px_x) not in results_dict.keys():
            results_dict[int(px_x)] = {}
        # For each pixel y
        for px_y in y_cos:
            # Results to dictionary
            results_dict[int(px_x)][int(px_y)] = {"ntl_datum": int(ntl_data[int(px_y)][int(px_x)]),
                                                  "gf_datum": int(gf_data[int(px_y)][int(px_x)]),
                                                  "qa_flag": int(qa_flags[int(px_y)][int(px_x)]),
                                                  "snow_flag": int(snow_flags[int(px_y)][int(px_x)])}

    return target_url[1], results_dict

    pass

def main(tiles=[], data_product="VNP46A2", max_workers=2, start_date=None, end_date=None):

    # Update VNP46A2 availability
    t_laads_tools.get_VNP46A_availability(data_product)
    # Get a TimeSyncSession
    tsync_session = c_VNP46A.TimeSyncSession()
    # Create a LAADS session
    curr_session = t_laads_tools.connect_to_laads()
    # Get a (now up to date) LAADS URL dictionary
    url_dict = t_laads_tools.LaadsUrlsDict(data_product)
    # For each tile in the supplied list
    for tile in tiles:
        # Set the new tile and get the dictionary
        tile_dict = tsync_session.set_target_tile(tile, wsf_threshold=0.05)
        # List for urls for this tile
        tile_urls_list = []
        # For each year in the url dict
        for year in url_dict[tile].dictionary.keys():
            # For day of year in the year
            for day in url_dict[tile][year].keys():
                # Append URL to list
                tile_urls_list.append(url_dict[tile][year][day])
        # Start a ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            future_events = [executor.submit(process_day,
                                             target_url,
                                             curr_session,
                                             fua_info, fua_polygon, target_tile, x_cos, y_cos) for target_url in
                             target_urls]
            for completed_event in as_completed(future_events):
                date_obj, day_results = completed_event.result()
                date_key = date_obj.strftime("%y_%m_%d")
                print(f"Date: {date_key} completed")
                # Make subdict
                results_dict[date_key] = day_results


if __name__ == "__main__":

    tile_list = ["h17v03"]

    main(tiles=tile_list, end_date=datetime.datetime.today())