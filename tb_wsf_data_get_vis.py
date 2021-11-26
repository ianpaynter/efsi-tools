import matplotlib as mpl
from matplotlib import pyplot as plt
import json
import numpy as np
import pickle


with open("C:/USRA/test_wsf_h17v3_arr", 'rb') as f:
    input_arr = pickle.load(f)

# Get a colormap object
norm = mpl.colors.Normalize(vmin=0, vmax=np.max(input_arr))

my_cmap = mpl.cm.ScalarMappable(cmap="Spectral_r", norm=norm)

fig = plt.figure(figsize=(20, 10))
ax = fig.add_subplot(1, 1, 1)
plt.imshow(input_arr[:, :, 0], cmap=my_cmap.cmap, norm=norm)
plt.colorbar()
ax.set_title(f"WSF 2015 Proportion Settled VNP46A Tile h17v03 (United Kingdom)")
ax.set_xlabel(f"VNP46A in-tile horizontal coordinate")
ax.set_ylabel(f"VNP46A in-tile vertical coordinate")

plt.show()

fig = plt.figure(figsize=(20, 10))
ax = fig.add_subplot(1, 1, 1)
plt.imshow(input_arr[:, :, 1], cmap=my_cmap.cmap, norm=norm)
plt.colorbar()
ax.set_title(f"WSF 2019 Proportion Settled VNP46A Tile h17v03 (United Kingdom)")
ax.set_xlabel(f"VNP46A in-tile horizontal coordinate")
ax.set_ylabel(f"VNP46A in-tile vertical coordinate")

plt.show()

diff_arr = input_arr[:, :, 1] - input_arr[:, :, 0]
norm = mpl.colors.Normalize(vmin=0.01, vmax=np.max(diff_arr))
cmap = mpl.cm.get_cmap("Spectral_r").copy()
cmap.set_under('k')
my_cmap = mpl.cm.ScalarMappable(cmap=cmap, norm=norm)
fig = plt.figure(figsize=(20, 10))
ax = fig.add_subplot(1, 1, 1)
plt.imshow(diff_arr, cmap=my_cmap.cmap, norm=norm)
plt.colorbar()
ax.set_title(f"Difference in Settled Proportion (2019 - 2015) VNP46A Tile h17v03 (United Kingdom)")
ax.set_xlabel(f"VNP46A in-tile horizontal coordinate")
ax.set_ylabel(f"VNP46A in-tile vertical coordinate")

plt.show()