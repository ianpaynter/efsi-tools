import numpy as np
import pickle
import os
import dotenv

dotenv.load_dotenv()

# Set matplotlib defaults for fonts
mpl.rc('font', family='Times New Roman')
mpl.rc('axes', labelsize=14)
mpl.rc('axes', titlesize=14)
mpl.rc('xtick', labelsize=12)
mpl.rc('ytick', labelsize=12)

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
         ""
         ]
