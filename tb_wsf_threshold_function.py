import numpy as np
import pickle
import os
import dotenv
import c_VNP46A
import matplotlib as mpl
from matplotlib import pyplot as plt
import c_WSF

dotenv.load_dotenv()

# Set matplotlib defaults for fonts
mpl.rc('font', family='Times New Roman')
mpl.rc('axes', labelsize=14)
mpl.rc('axes', titlesize=14)
mpl.rc('xtick', labelsize=12)
mpl.rc('ytick', labelsize=12)

# WSF proportion settled per VNP46A2 pixel threshold at equator
wsf_eq_threshold = 0.01
# Estimate of absolute area at equator in square kilometers
equator_area = c_VNP46A.get_pixel_area(21600) * wsf_eq_threshold
# Estimate of settlement extent in meters
equator_extent = np.sqrt(equator_area) * 1000

# Get the area of a pixel at the equator, print the area equivalent
print(f"The threshold will retain {np.around(equator_area, decimals=3)} square km of area per VNP46A2 pixel.\n"
      f"This is equivalent to a {np.around(equator_extent, decimals=1)}m x {np.around(equator_extent, decimals=1)}m area.")

# Lists for plotting variables
global_ys = []
thresholds = []

# For the full y-range of pixels
for global_y in np.arange(0, 43200):
    global_ys.append(global_y)
    thresholds.append(c_WSF.get_threshold_for_lat(global_y, wsf_eq_threshold) * 100)

fig = plt.figure(figsize=(6, 6))
ax = fig.add_subplot(1, 1, 1)
VNP462_pixels = ax.scatter(global_ys, thresholds, 1, 'r', label="VNP46A2 Pixels")
ax.set_xlabel("Pixel v coordinate (North = 0, South = 43199)")
ax.set_ylabel("VNP46A2 Settled Threshold (%)")
ax.set_title(f"VNP46A2 Settled Threshold by Latitude for {wsf_eq_threshold * 100}% Threshold at Equator\n"
             f"Retains {np.around(equator_area, decimals=3)}km$^2$ of area per VNP46A2 pixel.\n"
             f"Equivalent to a {np.around(equator_extent, decimals=1)}m x {np.around(equator_extent, decimals=1)}m area.")
equator, = ax.plot([21620, 21620], [0, max(thresholds)], linestyle='--', color='k', label="Equator")
ax.set_ylim([0, (wsf_eq_threshold * 100) + 0.1])
plt.legend(edgecolor='k')
plt.show(block=False)

tiles = ["h20v02",
         "h17v03",
         "h08v04",
         "h08v05",
         "h21v06",
         "h21v07",
         "h22v08",
         "h20v09",
         "h20v10",
         "h20v11",
         "h11v13",
         "h11v14"]

# Figure
fig = plt.figure(figsize=(18, 12))
plt.subplots_adjust(hspace=0.1, wspace=0.05)
# Plot number
plot_n = 0

# For each tile
for tile in tiles:
    plot_n += 1

    with open(os.path.join(os.environ["wsf_vnp_results_path"], "wsf_for_vnp_" + tile), 'rb') as f:
        input_arr = pickle.load(f)

    vnp_2015_pix_counts = []
    vnp_2019_pix_counts = []
    vnp_size = 2400 * 2400

    # Get the central pixel v for the tile
    pixel_v = (int(tile[4:]) * 2400) + 1200

    # Get threshold for tile
    tile_threshold = c_WSF.get_threshold_for_lat(pixel_v, wsf_eq_threshold)

    # Get a colormap object
    norm = mpl.colors.Normalize(vmin=tile_threshold, vmax=np.max(input_arr))
    cmap = mpl.cm.get_cmap("Spectral_r").copy()
    cmap.set_under('k')
    my_cmap = mpl.cm.ScalarMappable(cmap=cmap, norm=norm)
    ax = fig.add_subplot(3, 4, plot_n)
    ax.imshow(input_arr[:, :, 1], cmap=my_cmap.cmap, norm=norm)
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    ax.set_title(f"Tile: {tile}, threshold: {np.around(tile_threshold * 100, decimals=3)}%")

plt.show()