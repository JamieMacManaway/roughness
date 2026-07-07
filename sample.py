import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point
from pathlib import Path
import rasterio

shape = 'Project/Data/vectors/Scotland/lochfree.shp'

def create_random_points(shape, num_points):
    shape = gpd.read_file(shape)
    sample = gpd.GeoDataFrame((shape.sample_points(size=num_points).explode(ignore_index=True)))
    points = sample.rename(columns={'sampled_points': 'geometry'})
    points = points.set_geometry('geometry')
    points['x'] = points.geometry.x
    points['y'] = points.geometry.y
    return points
    return gpd.GeoDataFrame(geometry=points, crs=polygons.crs)

points = create_random_points(shape, 1000000)

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

elevation = extract_values(points, 'Project/Data/dems/Scotland/DEMS', 'elevation')
roughness15 = extract_values(elevation, 'Project/Data/dems/Scotland/SSDN/15', 'roughness_15')
roughness150 = extract_values(roughness15, 'Project/Data/dems/Scotland/SSDN/150', 'roughness_150')
roughness1500 = extract_values(roughness150, 'Project/Data/dems/Scotland/SSDN/1500', 'roughness_1500')
roughness3000 = extract_values(roughness1500, 'Project/Data/dems/Scotland/SSDN/3000', 'roughness_3000')

print('rasters sampled')

def sample_vector_layers(points_gdf, vector_folder):
    vector_paths = list(vector_folder.glob("*.shp")) + list(vector_folder.glob("*.gpkg"))
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

vector_folder = Path('Project/Data/vectors/Scotland/combined')

final = sample_vector_layers(roughness3000, vector_folder)

final.drop(['geometry'], axis=1)

final.to_parquet('Project/Output/Scotland_Sample_Data.parquet')
