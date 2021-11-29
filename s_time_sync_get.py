from concurrent.futures import ProcessPoolExecutor
import c_VNP46A
import t_laads_tools
import datetime

def main(tiles=[], max_workers=2, start_date=None, end_date=None):

    # Get a TimeSyncSession
    tsync_session = c_VNP46A.TimeSyncSession()
    # Create a LAADS session
    curr_session = t_laads_tools.connect_to_laads()
    # For each tile in the supplied list
    for tile in tiles:
        # Set the new tile and get the dictionary
        tile_dict = tsync_session.set_target_tile(tile, wsf_threshold=0.05)
        # Start a ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=12) as executor:
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