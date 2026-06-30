import geopandas as gpd

# define a function that takes two shapefiles and returns the area where they don't overlap
def vector_difference(input_shape, overlay_shape, projection):
    input_layer = gpd.read_file(input_shape).to_crs(epsg=projection)
    overlay_layer = gpd.read_file(overlay_shape).to_crs(epsg=projection)

    difference_layer = input_layer.overlay(overlay_layer, how='difference')
    return difference_layer

scotland = gpd.read_file('Project/Data/vectors/Scotland/scotland.shp')
lochs = gpd.read_file('Project/Data/vectors/Scotland/scotlochs.shp') 

scotland.to_crs(epsg=27700, inplace=True)
lochs.to_crs(epsg=27700, inplace=True)

waterless = scotland.overlay(lochs, how='difference')

waterless.to_file('Project/Data/vectors/Scotland/lochfree.shp')
