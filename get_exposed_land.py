# import required libraries
import geopandas as gpd
import pandas as pd
from pathlib import Path
import shutil

# create scratch directory
print('\ncreating scratch directory')
scratch = Path('data/vectors/greenland/scratch')
scratch.mkdir(parents=True, exist_ok=True)

# read in datasets
# scotland
print('\nreading in datasets')
scotland = gpd.read_file('data/vectors/scotland/scotland.shp').to_crs(epsg=27700).dissolve()
lochs = gpd.read_file('data/vectors/scotland/GLAKES_eu.shp').to_crs(epsg=27700)

# greenland
greenland = gpd.read_file('data/vectors/greenland/GRL_adm0.shp').to_crs(epsg=3413)
glaciers = gpd.read_file('data/vectors/greenland/RGI2000-v7.0-G-05_greenland_periphery.shp').to_crs(epsg=3413)
ice_sheet = gpd.read_file('data/vectors/greenland/GRE_IceSheet_IMBIE2_v1.shp').to_crs(epsg=3413)
# merge the two GLAKES datasets as they're read in
glakes = pd.concat([gpd.read_file('data/vectors/greenland/GLAKES_na1.shp').to_crs(epsg=3413), gpd.read_file('data/vectors/greenland/GLAKES_na2.shp').to_crs(epsg=3413)])
hlakes = gpd.read_file('data/vectors/greenland/HydroLAKES_polys_v10.shp').to_crs(epsg=3413)

print('\nprocessing Scottish datasets')
# remove areas covered by lochs in Scotland
lochless = scotland.overlay(lochs, how='difference')

# save scotland dataset to file
lochless.to_file('data/vectors/scotland/lochfree.shp')

print('\nprocessing Greenland datasets')
# merge the hlakes dataset above 76 degrees latitude with the glakes dataset below
print('\nmerging glakes and hlakes datasets')
lakes = pd.concat([hlakes[hlakes['Pour_lat'] > 76], glakes[glakes['Lat'] <= 76]])
lakes.to_file('data/vectors/greenland/lakes.shp')

# iteratively remove areas covered by ice or water around the periphery of the greenland ice sheet
print('\nremoving ice sheet')
greenland_without_ice_sheet = greenland.overlay(ice_sheet, how='difference')
greenland_without_ice_sheet.to_file('data/vectors/greenland/scratch/periphery.shp')

print('\nremoving glaciers')
greenland_periphery = gpd.read_file('data/vectors/greenland/scratch/periphery.shp')
greenland_without_ice = greenland_periphery.overlay(glaciers, how='difference')
greenland_without_ice.to_file('data/vectors/greenland/scratch/ice_free.shp')

print('\nremoving lakes')
ice_free_greenland = gpd.read_file('data/vectors/greenland/scratch/ice_free.shp')
greenland_lakes = gpd.read_file('data/vectors/greenland/lakes.shp')
greenland_wihout_ice_or_water = ice_free_greenland.overlay(lakes, how='difference')

# save greenland dataset to file
greenland_without_ice_or_water.to_file('data/vectors/greenland/exposed_land.shp')

# remove scratch folder
print('\nfinishing up!')
shutil.rmtree(scratch)
print('\nall done')