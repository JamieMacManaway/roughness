# import required libraries
import geopandas as gpd
import rioxarray as rio
from pathlib import Path

# create output directories
temp_folder = Path('data/rasters/greenland/climate/temperature')
temp_folder.mkdir(parents=True, exist_ok=True)
prcp_folder = Path('data/rasters/greenland/climate/precipitation')
prcp_folder.mkdir(parents=True, exist_ok=True)

# import climate datasets and national boundaries
gland = gpd.read_file('data/vectors/greenland/GRL_adm0.shp').to_crs(epsg=4326)
temp = rio.open_rasterio('data/rasters/greenland/climate/cru_ts4.09.1901.2024.tmp.dat.nc')
prcp = rio.open_rasterio('data/rasters/greenland/climate/cru_ts4.09.1901.2024.pre.dat.nc')

sland = gpd.read_file('data/vectors/scotland/scotland.shp').to_crs(epsg=27700)
s_temp = gpd.read_file('data/vectors/scotland/Monthly_Temperature_Observations_1991-2020.shp').to_crs(epsg=27700)
s_prcp = gpd.read_file('data/vectors/scotland/Monthly_Precipitation_Observations_1991-2020.shp').to_crs(epsg=27700)

# assign the greenland shapefile CRS to climate data
temp.rio.write_crs(gland.crs, inplace=True)
prcp.rio.write_crs(gland.crs, inplace=True)

# clip climate data to Greenland boundary
tclipped = temp.rio.clip(gland.geometry.values, drop=True)
tclean = tclipped.where(tclipped != tclipped.tmp.rio.nodata)

pclipped = prcp.rio.clip(gland.geometry.values, drop=True)
pclean = pclipped.where(pclipped != pclipped.pre.rio.nodata)

# select data for the period 1991-2020
t91_20 = tclean.sel(time=slice('1991-01-01', '2020-12-31'))
p91_20 = pclean.sel(time=slice('1991-01-01', '2020-12-31'))

# resample to annual data
annualtmp = t91_20.resample(time='1YE').mean()
annualprcp = p91_20.resample(time='1YE').sum()

# calculate mean annual temperature and total annual precipitation
gtemp = annualtmp['tmp'].mean(dim='time')
gprcp = annualprcp['pre'].mean(dim='time')

# reproject to EPSG:3413
gtemp = gtemp.rio.reproject("EPSG:3413")
gprcp = gprcp.rio.reproject("EPSG:3413")
gprcp = gprcp.where(gprcp > 0)  # remove zero values for precipitation

# write greenland data
gtemp.rio.to_raster('data/rasters/greenland/climate/temperature/temperature.tif')
gprcp.rio.to_raster('data/rasters/greenland/climate/precipitation/precipitation.tif')

# clip the UK datasets to the Scotland boundary
stemp = s_temp.clip(sland)
sprcp = s_prcp.clip(sland)

# calculate mean temperature and total precipitation for each grid cell
stemp_values = stemp.select_dtypes(include=['float64', 'int64']).columns
stemp['mean'] = stemp[stemp_values].mean(axis=1)
sprcp_values = sprcp.select_dtypes(include=['float64', 'int64']).columns
sprcp['total'] = sprcp[sprcp_values].sum(axis=1)

# write scottish data to file
sprcp.to_file('data/vectors/scotland/precipitation.shp')
stemp.to_file('data/vectors/scotland/temperature.shp')