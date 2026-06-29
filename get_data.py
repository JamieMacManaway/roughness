# import required libraries
import subprocess
from pathlib import Path
import geopandas as gpd
import tarfile

# specify a folder in which to save ArcticDEM tiles
folder = Path('Project/Data/dems/Greenland')
folder.mkdir(parents=True, exist_ok=True)

# read in the exposed land and ArcticDEM mosaic index shapefiles
land = gpd.read_file('Project/Data/vectors/Greenland/exposed_land.shp').to_crs(epsg=3413)
index = gpd.read_file('Project/Data/vectors/Greenland/ArcticDEM_Mosaic_Index_v4_1_2m.shp').to_crs(epsg=3413)

# extract tiles from the index which correspond to exposed land
gland_index = index[index.intersects(land.union_all())]

# extract corresponding urls for tiles of interest 
tiles = list(gland_index['fileurl'])

# function which downloads the tiles of interest into the previously specified folder, only if they don't already exist
def get_data(tiles):
    for tile in tiles:
        url = tile
        cmd = [
            "wget",
            "-r", "-N", "-nH", "-np",
            "-R", "index.html*",
            "--cut-dirs=3",
            "-P", folder,
            url
        ]
        subprocess.run(cmd, check=True)

# run the function and download the tiles of interest
get_data(tiles)

# function to check that downloaded files are complete and uncorrupted
def check_tar_integrity(tar_path):
    try:
        with tarfile.open(tar_path, "r:*") as tar:
            tar.getmembers()  # Attempt to list members to verify integrity
        print(f"{tar_path.name}: OK")
    except EOFError as eof_error:
        print(f"{tar_path.name}: Corrupted (EOFError - {eof_error})")
        tar_path.unlink()  # Delete corrupted file
        print(f"{tar_path.name}: Deleted due to corruption.")
        get_data(tiles)
    except tarfile.TarError as tar_error:
        print(f"{tar_path.name}: Corrupted (TarError - {tar_error})")
        tar_path.unlink()  # Delete corrupted file
        print(f"{tar_path.name}: Deleted due to corruption.")
        get_data(tiles)

# Iterate through all .tar files in the directory and check their integrity
# If any files corrupted, run the script again to ensure completeness of dataset
for tar_file in folder.rglob('*'):
    if tar_file.suffix in [".tar", ".gz"]:  # Check for .tar or .gz files
        print(f"Checking {tar_file.name}...")
        check_tar_integrity(tar_file)