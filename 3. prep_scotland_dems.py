# import required libraries
from osgeo import gdal
from pathlib import Path
import shutil

# locate directory containing Scottish dataset
asc_folder = Path('data/rasters/scotland/ascs')

# create directories for pre-processing
warp_folder = Path('data/rasters/scotland/warped')
warp_folder.mkdir(parents=True, exist_ok=True)

dem_folder = Path('data/rasters/scotland/dems')
dem_folder.mkdir(parents=True, exist_ok=True)

# reproject data to epsg 277700
for asc in asc_folder.rglob('*.asc'):
    if (warp_folder / asc.name).exists():
        print(f'{asc.name} already processed. Skipping...')
        continue
    else:
        print(f'Reprojecting {asc.name}...')
        gdal.Warp(str(warp_folder / asc.name), asc, dstSRS='EPSG:27700')
        print(f'{asc.name} reprojected successfully.')

# convert ascs to tifs
for file in warp_folder.rglob('*.asc'):
    if Path(dem_folder / file.stem).with_suffix('.tif').is_file():
        print(f'{file.name} already processed. Skipping...')
        continue
    else:
        print(f'Converting {file.name}...')
        gdal.Translate((dem_folder / file.stem).with_suffix('.tif'), file, format='GTiff')
        print(f'{file.name} converted successfully.')

print('')
print('Tidying up...')
print('')

# remove extraneous directory
shutil.rmtree(warp_folder)
print('Scotland data ready for further analysis. \U0001F680')
