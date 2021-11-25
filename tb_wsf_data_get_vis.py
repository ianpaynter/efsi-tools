import matplotlib as mpl
from matplotlib import pyplot as plt
import json

with open("C:/USRA/test_wsf_h17v3", 'r') as f:
    input_dict = json.load(f)

vnp_hs = []
vnp_vs = []
wsf_2015 = []
wsf_2019 = []
wsf_difference = []

for vnp_h in input_dict.keys():
    for vnp_v in input_dict[vnp_h].keys():
        vnp_hs.append(int(vnp_h))
        vnp_vs.append(2400 - int(vnp_v))
        wsf_2015.append(input_dict[vnp_h][vnp_v]["WSF2015"])
        wsf_2019.append(input_dict[vnp_h][vnp_v]["WSF2019"])
        wsf_difference.append(input_dict[vnp_h][vnp_v]["WSF2019"] - input_dict[vnp_h][vnp_v]["WSF2015"])

for data_set in [wsf_2015, wsf_2019, wsf_difference]:

    fig = plt.figure(figsize=(10, 10))

    ax = fig.add_subplot(1, 1, 1)

    ax.scatter(vnp_hs, vnp_vs, 3, data_set, marker='.')
    plt.show()


