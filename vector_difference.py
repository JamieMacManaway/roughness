import geopandas as gpd

scotland = gpd.read_file('Project/Data/vectors/Scotland/scotland.shp')
lochs = gpd.read_file('Project/Data/vectors/Scotland/scotlochs.shp') 

scotland.to_crs(epsg=27700, inplace=True)
lochs.to_crs(epsg=27700, inplace=True)

waterless = scotland.overlay(lochs, how='difference')

waterless.to_file('Project/Data/vectors/Scotland/lochfree.shp')
