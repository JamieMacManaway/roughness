import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point
from pathlib import Path
import rasterio

scotland = 'data/vectors/scotland/lochfree.shp'
greenland = 'data/vectors/greenland/exposed_land.shp'

output_folder = Path('data/parquets')
output_folder.mkdir(parents=True, exist_ok=True)

def create_random_points(shape, num_points):
    shape = gpd.read_file(shape)
    sample = gpd.GeoDataFrame((shape.sample_points(size=num_points).explode(ignore_index=True)))
    points = sample.rename(columns={'sampled_points': 'geometry'})
    points = points.set_geometry('geometry')
    points['x'] = points.geometry.x
    points['y'] = points.geometry.y
    return points
    return gpd.GeoDataFrame(geometry=points, crs=polygons.crs)

scotland_points = create_random_points(scotland, 1000000)
greenland_points = create_random_points(greenland, 4500000)

def extract_values(points, rasters, dataset):
    coords = [(x, y) for x, y in zip(points['geometry'].x, points['geometry'].y)]
    values = []
    raster_folder = Path(rasters)
    for fname in Path.iterdir(raster_folder):
        if fname.suffix == ".tif":
            with rasterio.open(fname) as src:
                points[dataset] = [x for x in src.sample(coords, masked=True)]
                points[dataset] = points[dataset].astype(float)
                filtered = points.dropna()
                values.append(filtered)

    df = pd.concat(values)
    return df

scotland_elevation = extract_values(scotland_points, 'data/rasters/scotland/dems', 'elevation')
scotland_roughness15 = extract_values(scotland_elevation, 'data/rasters/scotland/ssdn/15', 'roughness_15')
scotland_roughness150 = extract_values(scotland_roughness15, 'data/rasters/scotland/ssdn/150', 'roughness_150')
scotland_roughness1500 = extract_values(scotland_roughness150, 'data/rasters/scotland/ssdn/1500', 'roughness_1500')
scotland_roughness3000 = extract_values(scotland_roughness1500, 'data/rasters/scotland/ssdn/3000', 'roughness_3000')

greenland_elevation = extract_values(points, 'data/rasters/greenland/dems', 'elevation')
greenland_roughness15 = extract_values(greenland_elevation, 'data/rasters/greenland/ssdn/15', 'roughness_15')
greenland_roughness150 = extract_values(greenland_roughness15, 'data/rasters/greenland/ssdn/150', 'roughness_150')
greenland_roughness1500 = extract_values(greenland_roughness150, 'data/rasters/greenland/ssdn/1500', 'roughness_1500')
greenland_roughness3000 = extract_values(greenland_roughness1500, 'data/rasters/greenland/ssdn/3000', 'roughness_3000')
greenland_precipitation = extract_values(greenland_roughness3000, 'data/rasters/greenland/climate/precipitation', 'precipitation')
greenland_temperature = extract_values(greenland_precipitation, 'data/rasters/greenland/climate/temperature', 'temperature')

print('rasters sampled')

def sample_vector_layers(points_gdf, vector_folder, vectors):
    vector_paths = [vector_folder / x for x in vectors]
    enriched = points_gdf.copy()

    for path in vector_paths:
        layer = gpd.read_file(path).to_crs(points_gdf.crs)
        layer_name = path.stem

        # Spatial join: points get attributes from overlapping polygons
        joined = gpd.sjoin(enriched, layer, how="left", predicate="intersects")
        grouped = joined.groupby(joined.index)

        # Add selected attributes to point layer
        for col in layer.columns:
            if col != "geometry":
                enriched[f"{layer_name}_{col}"] = grouped[col].first() 

    return enriched

scottish_vector_folder = Path('data/vectors/scotland')
scottish_vectors = ['temperature.shp', 'precipitation.shp', 'bedrock.shp']

scotland_final = sample_vector_layers(scotland_roughness3000, scottish_vector_folder, scottish_vectors)

scotland_final.drop(['geometry'], axis=1)

scotland_final.to_parquet(output_folder / 'scotland.parquet')

greenland_vector_folder = Path('data/vectors/greenland')
greenland_vectors = ['bedrock.shp']

greenland_final = sample_vector_layers(greenland_temperature, greenland_vector_folder, greenland_vectors)

greenland_final.drop(['geometry'], axis=1)

greenland_final.to_parquet(output_folder / 'greenland.parquet')
