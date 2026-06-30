import geopandas as gpd

# define a function which loads in two shapefiles and clips one to the other
def clip_vector(input_shape, clip_shape, projection):
    # Load layers and ensure that they are both projected to the same crs
    input_layer = gpd.read_file(input_shape).to_crs(epsg=projection)
    clip_layer = gpd.read_file(clip_shape).to_crs(epsg=projection)

    # Perform spatial clip
    clipped_layer = input_layer.clip(clip_layer, keep_geom_type=True)

    # return result
    return clipped_layer

# clip 

        clip_layer = gpd.read_file("Project/Data/vectors/Greenland/exposed_land.shp").to_crs(epsg=3413)
    input_layer = gpd.read_file("Project/Data/vectors/Greenland/landscape_classification.shp").to_crs(epsg=3413)

    # Perform spatial clip
    clipped_layer = input_layer.clip(clip_layer, keep_geom_type=True)

    # Save result
    clipped_layer.to_file("Project/Data/vectors/Greenland/land_class.shp")