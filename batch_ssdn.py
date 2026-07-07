# import required libraries. 
# Note that Whitebox Tools should be downloaded from https://github.com/jblindsay/whitebox-tools
# The WBT folder containing Whitebox Tools should be in the same directory as this script
from WBT.whitebox_tools import WhiteboxTools
from pathlib import Path

wbt = WhiteboxTools()
wbt.set_compress_rasters(True)

# define scales of interest
scales = [15, 150, 1500, 3000]

# define folders
greenland_dems = Path('data/rasters/greenland/dems/')
greenland_ssdns = Path('data/rasters/greenland/ssdn')
scotland_dems = Path('data/rasters/scotland/dems/')
scotland_ssdns = Path('data/rasters/scotland/ssdn')

# define a function to process all dem tiles in the input folder
# and save them in an output directory with subdirectories for each resolution
# with window size determined by resolution of dataset
def process_raster(input_folder, output_folder, resolution):
    output_folder.mkdir(parents=True, exist_ok=True)
    for scale in scales:
        window = scale // resolution
        scale_folder = output_folder / str(scale)
        scale_folder.mkdir(parents=True, exist_ok=True)
        for raster in input_folder.rglob('*.tif'):
            ssdn_path = scale_folder / raster.name
            if not ssdn_path.exists():
                print('')
                print(f'processing {raster}')
                wbt.spherical_std_dev_of_normals(str(raster), str(ssdn_path), filter=window)
                print(f"{raster} successfully processed.")
            else:
                print('')
                print(f"{raster} already processed, skipping...")

print('processing greenland dems')
process_raster(greenland_dems, greenland_ssdns, 2)
print('successfully processed all greenland dems')
print('')
print('processing scotland dems')
process_raster(scotland_dems, scotland_ssdns, 5)
print('successfully processed all scotland dems')
print('')

print('All dems successfully processed! \U0001F680')