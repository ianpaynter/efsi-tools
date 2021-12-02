import h5py
import io
from matplotlib import pyplot as plt
import pickle
import dotenv

dotenv.load_dotenv()

# Open the appropriate WSF file
with open(os.path.join(os.environ["wsf_vnp_results_path"], "wsf_for_vnp_" + "h29v05"), 'rb') as f:
    # Load the numpy array
    wsf_array = pickle.load(f)

#with open(r"F:\USRA\Quarantine\Original\VNP46A2.A2016009.h29v05.001.2020258174450.h5", 'rb') as f:
  #  in_file = io.BytesIO(f)
#
# Convert to h5 file object
h5file = h5py.File(r"F:\USRA\Quarantine\Original\VNP46A2.A2016009.h29v05.001.2020258174450.h5", 'r')

print(h5file['HDFEOS']['GRIDS']['VNP_Grid_DNB']['Data Fields']['DNB_BRDF-Corrected_NTL'][0][0])

fig = plt.figure(figsize=(10, 10))
plt.imshow(h5file['HDFEOS']['GRIDS']['VNP_Grid_DNB']['Data Fields']['DNB_BRDF-Corrected_NTL'])

plt.show()