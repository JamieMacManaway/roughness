# import required libraries
import geopandas as gpd
from pathlib import Path
import pandas as pd

# identify data folders
greenland_data_folder = Path('data/vectors/greenland/Isochrone_polygon_shapefiles')
scotland_data_folder = Path('data/vectors/scotland/isochrones')

print('\nloading datasets')

# read in country outlines
scotland = gpd.read_file('data/vectors/scotland/scotland.shp').to_crs(epsg=27700)
greenland = gpd.read_file('data/vectors/greenland/GRL_adm0.shp').to_crs(epsg=3413)

# define a function to process isochrone shapefiles
def merge_isochrones(data_folder, crs):
    isochrone_polygons = []
    shapefiles = [i for i in data_folder.glob('*.shp')]
    for shapefile in shapefiles:
        isochrone = gpd.read_file(shapefile).to_crs(epsg=crs)
        if shapefile.stem.split('_')[0].strip('ka') == 'LLS':
            isochrone['time since deglaciation'] = '12'
        elif crs == 3413:
            isochrone['time since deglaciation'] = (shapefile.stem.split('_')[0].strip('ka')).split('-')[1]
        else:
            isochrone['time since deglaciation'] = shapefile.stem.split('_')[0].strip('ka')
        isochrone_polygons.append(isochrone)
    isochrones = pd.concat(isochrone_polygons)
    return isochrones

print('\nprocessing greenland data')

# process greenland data
greenland_chrones = merge_isochrones(greenland_data_folder, 3413)
greenland_chrones.drop(['Id', 'Area', 'gridcode', 'ORIG_FID', 'area', 'OBJECTID'], axis=1, inplace=True)
greenland_chrones_clipped = greenland_chrones.clip(greenland)
greenland_chrones_clipped.to_file('data/vectors/greenland/time since deglaciation.shp')

print('\nprocessing scotland data')

# process scotland data
scotland_chrones = merge_isochrones(scotland_data_folder, 27700)
scotland_chrones.drop(['Id', 'thickness', 'Area'], axis=1, inplace=True)
scotland_chrones_dissolved = scotland_chrones.dissolve(by='time since deglaciation')
scotland_chrones_clipped = scotland_chrones_dissolved.clip(scotland)
scotland_chrones_clipped.to_file('data/vectors/scotland/time since deglaciation.shp')

print('\nall done!')
