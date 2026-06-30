from pathlib import Path
import geopandas as gpd
import tarfile
import subprocess

# read in the greenland boundary, ice sheet and ArcticDEM mosaic index shapefiles
boundary = gpd.read_file('data/vectors/greenland/GRL_adm0.shp').to_crs(epsg=3413)
ice_sheet = gpd.read_file('data/vectors/greenland/GRE_IceSheet_IMBIE2_v1.shp').to_crs(epsg=3413)
index = gpd.read_file('data/vectors/greenland/ArcticDEM_Mosaic_Index_v4_1_2m.shp').to_crs(epsg=3413)

# find area of Greenland surrounding the ice sheet
periphery = boundary.overlay(ice_sheet, how='difference')

# locate tiles from the index which correspond to the periphery
gland_index = index[index.intersects(periphery.union_all())]

# extract corresponding urls for tiles of interest 
tiles = list(gland_index['fileurl'])

# take a subset of the list for testing
short = tiles[:3]
short

# specify a folder in which to save downloaded ArcticDEM tiles
tar_folder = Path('data/rasters/greenland/tars')
tar_folder.mkdir(parents=True, exist_ok=True)

# function which downloads the tiles of interest into the previously specified folder, only if they don't already exist
def get_data(tiles):
    for tile in tiles:
        url = tile
        cmd = [
            "wget",
            "-N",
            "-P", tar_folder,
            url
        ]
        subprocess.run(cmd, check=True)

# get the tiles from the subset
get_data(short)

# function to check that downloaded files are complete and uncorrupted
# If any files corrupted, runs the download function again to ensure completeness of dataset
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
for tar_file in tar_folder.rglob('*'):
    if tar_file.suffix in [".tar", ".gz"]:  # Check for .tar or .gz files
        print(f"Checking {tar_file.name}...")
        check_tar_integrity(tar_file)

# create a new folder into which the dems will be unpacked
dem_folder = Path('data/rasters/greenland/dems')
dem_folder.mkdir(parents=True, exist_ok=True)

# iterate through the tar files and unpack the dems into the previously specified folder
for tar_file in tar_folder.iterdir():
    with tarfile.open(tar_file, 'r') as tar:
        members = tar.getmembers()
        for member in members:
            if 'dem.tif' in member.name:
                tar.extract(member, path=dem_folder)
