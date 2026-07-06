# import required libraries. 
# Note that Whitebox Tools should be downloaded from https://github.com/jblindsay/whitebox-tools
# The WBT folder containing Whitebox Tools should be in the same directory as this script
from WBT.whitebox_tools import WhiteboxTools
from pathlib import Path

wbt = WhiteboxTools()
wbt.set_compress_rasters(True)

scales = [15, 150, 1500, 3000] # change to the spatial scales of interest

resolution = 5 # adjust according to the resolution of your dataset

def process_raster(raster_path, output_folder):
    output_folder.mkdir(parents=True, exist_ok=True)

    for scale in scales:
        result = -(-scale//resolution)
        window = str(result) if result % 2 != 0 else str(result +1)
        scale_folder = output_folder / str(scale)
        scale_folder.mkdir(parents=True, exist_ok=True)
        ssdn_path = scale_folder / raster_path.name
        if not ssdn_path.exists():
            wbt.spherical_std_dev_of_normals(str(raster_path), str(ssdn_path), filter=window)
            print(f"ssdn done: {ssdn_path}")
        else:
            print(f"ssdn exists, skipping: {ssdn_path}")

def batch_ssdn(input_root):
    input_root = Path(input_root)

    for folder in input_root.rglob("*"):
        if folder.is_dir():
            raster_files = folder.glob("*.tif")
            output_folder = input_root / "SSDN"
            for raster_path in raster_files:
                process_raster(
                    raster_path,
                    output_folder
                )
    print("Batch processing complete.")

input_folder = Path("/mnt/gpfs01/home/gy/gyjlm2/Project/Data/dems/Scotland/")
batch_ssdn(input_folder)