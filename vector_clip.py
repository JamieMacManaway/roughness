import geopandas as gpd

# Load layers
clip_layer = gpd.read_file("Project/Data/vectors/Greenland/exposed_land.shp").to_crs(epsg=3413)
input_layer = gpd.read_file("Project/Data/vectors/Greenland/landscape_classification.shp").to_crs(epsg=3413)

# Perform spatial clip
clipped_layer = input_layer.clip(clip_layer, keep_geom_type=True)

# Save result
clipped_layer.to_file("Project/Data/vectors/Greenland/land_class.shp")