import matplotlib as mpl
from matplotlib import pyplot as plt
import json
import numpy as np
import pickle

# Set matplotlib defaults for fonts
mpl.rc('font', family='Times New Roman')
mpl.rc('axes', labelsize=14)
mpl.rc('axes', titlesize=14)
mpl.rc('xtick', labelsize=12)
mpl.rc('ytick', labelsize=12)

tile_name = "h32v11"

with open(f"C:/USRA/test_wsf_{tile_name}_arr", 'rb') as f:
    input_arr = pickle.load(f)

thresholds = []
vnp_2015_pix_counts = []
vnp_2019_pix_counts = []
vnp_size = 2400 * 2400

# For each percentage point
for wsf_pc in np.arange(0, 1, 0.01):
    thresholds.append(wsf_pc * 100)
    vnp_2015_pix_counts.append(np.count_nonzero(input_arr[:, :, 0] > wsf_pc))
    vnp_2019_pix_counts.append(np.count_nonzero(input_arr[:, :, 1] > wsf_pc))

# Figure
fig = plt.figure(figsize=(30, 10))
fig.tight_layout()
# For each 5% threshold
for plot_n, pc_thresh in enumerate(np.arange(0.0001, 0.21, 0.05)):
    # Get a colormap object
    norm = mpl.colors.Normalize(vmin=pc_thresh, vmax=np.max(input_arr))
    cmap = mpl.cm.get_cmap("Spectral_r").copy()
    cmap.set_under('k')
    my_cmap = mpl.cm.ScalarMappable(cmap=cmap, norm=norm)
    ax = fig.add_subplot(2, 3, plot_n + 1)
    ax.imshow(input_arr[:, :, 1], cmap=my_cmap.cmap, norm=norm)
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    if plot_n + 1 == 2:
        ax.set_title(f"WSF 2019 Proportion, Tile: {tile_name},\n Threshold: >{int((np.around(pc_thresh, decimals=2)) * 100)}%")
    else:
        ax.set_title(f"Threshold: >{int((np.around(pc_thresh, decimals=2)) * 100)}%")

ax = fig.add_subplot(2, 3, 6)

line_2015, = ax.plot(thresholds, vnp_2015_pix_counts, linewidth=1, color='r')
line_2019, = ax.plot(thresholds, vnp_2019_pix_counts, linewidth=1, color='k')
ax.set_xlabel("Settled %")
ax.set_ylabel("VNP46A Pixel Count")
ax.legend([line_2015, line_2019], ["WSF 2015", "WSF 2019"],
                  edgecolor='k')
ax.set_title("Pixel Count for Settled Proportion Thresholds")
plt.show()
#
# fig = plt.figure(figsize=(20, 10))
# ax = fig.add_subplot(1, 1, 1)
# plt.imshow(input_arr[:, :, 1], cmap=my_cmap.cmap, norm=norm)
# plt.colorbar()
# ax.set_title(f"WSF 2019 Proportion Settled VNP46A Tile h17v03 (United Kingdom)")
# ax.set_xlabel(f"VNP46A in-tile horizontal coordinate")
# ax.set_ylabel(f"VNP46A in-tile vertical coordinate")
#
# plt.show()
#
# diff_arr = input_arr[:, :, 1] - input_arr[:, :, 0]
# norm = mpl.colors.Normalize(vmin=0.01, vmax=np.max(diff_arr))
# cmap = mpl.cm.get_cmap("Spectral_r").copy()
# cmap.set_under('k')
# my_cmap = mpl.cm.ScalarMappable(cmap=cmap, norm=norm)
# fig = plt.figure(figsize=(20, 10))
# ax = fig.add_subplot(1, 1, 1)
# plt.imshow(diff_arr, cmap=my_cmap.cmap, norm=norm)
# plt.colorbar()
# ax.set_title(f"Difference in Settled Proportion (2019 - 2015) VNP46A Tile h17v03 (United Kingdom)")
# ax.set_xlabel(f"VNP46A in-tile horizontal coordinate")
# ax.set_ylabel(f"VNP46A in-tile vertical coordinate")
#
# plt.show()