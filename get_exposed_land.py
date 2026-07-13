# import required libraries
import geopandas as gpd
import pandas as pd

# read in datasets
# scotland
scotland = gpd.read_file('data/vectors/scotland/scotland.shp').to_crs(epsg=27700).dissolve()
lochs = gpd.read_file('data/vectors/scotland/GLAKES_eu.shp').to_crs(epsg=27700)

# greenland
greenland = gpd.read_file('data/vectors/greenland/GRL_adm0.shp').to_crs(epsg=3413)
glaciers = gpd.read_file('data/vectors/greenland/RGI2000-v7.0-G-05_greenland_periphery.shp').to_crs(epsg=3413)
ice_sheet = gpd.read_file('data/vectors/greenland/GRE_IceSheet_IMBIE2_v1.shp').to_crs(epsg=3413)
# merge the two GLAKES datasets as they're read in
glakes = pd.concat([gpd.read_file('data/vectors/greenland/GLAKES_na1.shp').to_crs(epsg=3413), gpd.read_file('data/vectors/greenland/GLAKES_na2.shp').to_crs(epsg=3413)])
hlakes = gpd.read_file('data/vectors/greenland/HydroLAKES_polys_v10.shp').to_crs(epsg=3413)

# remove areas covered by lochs in Scotland
lochless = scotland.overlay(lochs, how='difference')

# save scotland dataset to file
lochless.to_file('data/vectors/scotland/lochfree.shp')

# merge the hlakes dataset above 76 degrees latitude with the glakes dataset below
lakes = pd.concat([hlakes[hlakes['Pour_lat'] > 76], glakes[glakes['Lat'] <= 76]])

# iteratively remove areas covered by ice or water around the periphery of the greenland ice sheet
greenland_without_ice_sheet = greenland.overlay(ice_sheet, how='difference')
greenland_without_ice = greenland_without_ice_sheet.overlay(glaciers, how='difference')
greenland_wihout_ice_or_water = greenland_without_ice.overlay(lakes, how='difference')

# save greenland dataset to file
greenland_without_ice_or_water.to_file('data/vectors/greenland/exposed_land.shp')