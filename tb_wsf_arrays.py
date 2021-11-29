import pickle
import os
import dotenv
import matplotlib as mpl
from matplotlib import pyplot as plt

dotenv.load_dotenv()

tile = "h17v03"
# Open the appropriate WSF file
with open(os.path.join(os.environ["wsf_vnp_results_path"], "wsf_for_vnp_" + tile), 'rb') as f:
    wsf_dict = pickle.load(f)
# For each column in keys
for vnp_h in wsf_dict:
    for index, vnp_v in enumerate(vnp_h):
        if vnp_v[1] > 0:
            print(index, vnp_v[1])
    input()