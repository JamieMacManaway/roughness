import subprocess
from pathlib import Path
import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.srtm as tile
import matplotlib.pyplot as plt
import cartopy.io.shapereader as shpreader
import geopandas as gpd
import rasterio as rio
from rasterio.plot import show
from rasterio.vrt import WarpedVRT
import numpy as np

f15 = rio.open('data/rasters/greenland/ssdn/15/33_43_1_1_2m_v4.1_dem.tif')
f150 = rio.open('data/rasters/greenland/ssdn/150/33_43_1_1_2m_v4.1_dem.tif')
f1500 = rio.open('data/rasters/greenland/ssdn/1500/33_43_1_1_2m_v4.1_dem.tif')
f3000 = rio.open('data/rasters/greenland/ssdn/3000/33_43_1_1_2m_v4.1_dem.tif')

elevation = rio.open('data/rasters/greenland/dems/33_43_1_1_2m_v4.1_dem.tif')
hillshade = rio.open('data/rasters/greenland/dems/33_43_1_1_2m_v4.1_hillshade.tif')

outline = 'data/vectors/greenland/GRL_adm0.shp'
ice = 'data/vectors/greenland/RGI2000-v7.0-G-05_greenland_periphery.shp'
lakes = 'data/vectors/greenland/lakes.shp'
aoi = 'data/vectors/greenland/aoi.shp"

# Define native and target CRS
native_crs = ccrs.Stereographic(central_latitude=75, true_scale_latitude=-40)
target_crs = ccrs.PlateCarree()  # For lat/lon grid

bounds = f15.bounds

# Plot raster
extent = [bounds.left, bounds.right, bounds.bottom, bounds.top]

vectors = [outline, ice, lakes, aoi]
shapes = []

for vector in vectors:
    crs = ccrs.Stereographic(central_latitude=75, central_longitude=-40)
    crs_proj4 = crs.proj4_init
    shape = gpd.read_file(vector)
    country = shape.to_crs(crs_proj4)
    shapes.append(country)

fig, ((ax1, ax2), (ax3, ax4), (ax5, ax6)) = plt.subplots(3,2, figsize=(14,21), subplot_kw={'projection': native_crs}, layout='constrained')

show((f15), ax=ax3)
show((f150), ax=ax4)
show((f1500), ax=ax5)
show((f3000), ax=ax6)
show((hillshade), cmap='gray', ax=ax2)
show(elevation, cmap='terrain', ax=ax2, alpha=0.5)

shapes[0].plot(ax=ax1, facecolor='yellowgreen', edgecolor='k', lw=0.1, alpha=0.25)
shapes[1].plot(ax=ax1, facecolor='whitesmoke')
shapes[2].plot(ax=ax1, facecolor='blue', zorder=5)
shapes[3].plot(ax=ax1, facecolor='none', edgecolor='fuchsia')

axes = {'a': ax1, 'b': ax2, 'c': ax3, 'd': ax4, 'e': ax5, 'f': ax6}

for key, item in axes.items():
    if item == ax1:
        item.text(0.1, 0.95, key, transform=item.transAxes,
                fontsize=16, fontweight='bold', va='top', ha='right', bbox=dict(facecolor='white', alpha=0.5, edgecolor='black', boxstyle='round,pad=0.5'))
        item.legend(['land', 'ice', 'lakes', 'aoi'])
        item.set_facecolor('aliceblue')
    else:
        if item == ax2:
            plt.colorbar(item.images[1], ax=item, location='right', shrink=0.6, label='Elevation (masl)')
        else:
            plt.colorbar(item.images[0], ax=item, location='right', shrink=0.6, label='Roughness')
        item.text(0.08, 0.95, key, transform=item.transAxes,
                fontsize=16, fontweight='bold', va='top', ha='right', bbox=dict(facecolor='white', alpha=0.5, edgecolor='black', boxstyle='round,pad=0.5'))
    gl = item.gridlines(crs=target_crs, draw_labels=True, x_inline=False, y_inline=False,
                        linewidth=0.5, color='gray', alpha=0.7, linestyle='--')
    

    gl.bottom_labels = False

    gl.right_labels = False

def add_legends(ax):

    import matplotlib.patches as mpatches

    ice = mpatches.Patch(facecolor='whitesmoke', edgecolor='k', lw=0.1, label='Ice')

    lakes = mpatches.Patch(color='blue', label='Lakes')

    exposed_land = mpatches.Patch(facecolor='yellowgreen', alpha=0.25, edgecolor='k', lw=0.1, label='Exposed Land')

    aoi = mpatches.Patch(facecolor='none', edgecolor='fuchsia', label='AOI')

    ax.legend(handles=[ice, lakes, exposed_land, aoi], loc='lower right', title='Key', 
              #title_fontsize=18, 
              edgecolor='k' 
              #prop={'size': 15}
              )

add_legends(ax1)

plt.savefig('figures/aoi.png', dpi=300)

scot_outline = 'data/vectors/scotland/scotland.shp'
scot_deglaciation = 'data/vectors/scotland/time since deglaciation.shp'

gland_outline = 'data/vectors/greenland/GRL_adm0.shp'
gland_deglaciation = 'data/vectors/greenland/time since deglaciation.shp'

scot_dem = rio.open('data/rasters/scotland/dsm.tif')
scot_shade = rio.open('data/rasters/scotland/hillshade.tif')

elevation = rio.open('data/rasters/greenland/dem.tif')
hillshade = rio.open('data/rasters/greenland/hillshade.tif')

scot_elevation = scot_dem.read(1)
scot_hillshade = scot_shade.read(1)

gland_elevation = elevation.read(1)
gland_hillshade = hillshade.read(1)

scotbounds = scot_dem.bounds
scotextent = [scotbounds.left, scotbounds.right, scotbounds.bottom, scotbounds.top]

gbounds = elevation.bounds
gextent = [gbounds.left, gbounds.right, gbounds.bottom, gbounds.top]

greenland_bbox = [-55, -27, 58, 84]

scotland_bbox = [-8, -0.5, 54.5, 61]

def make_a_map(ax, bbox, grid=True, background=True, inset=None, clat=None, clon=None, position=None, fname=None, zoom=1):
    """
    This function creates a map with bounding box (bbox) in format [west, east, south, north] (you can use http://bboxfinder.com to find coordinates)
    Projection can be any of the standard cartopy projections found at https://scitools.org.uk/cartopy/docs/v0.15/crs/projections.html
    A lon, lat grid is overlaid (and background imagery included) as standard
    An optional inset map can also be included. If an inset is included:
        - the central lat and lon positions can be specified (if the projection supports this)
        - the position (and size) of the inset can be set with format (x, y, width, height) in fractions of the axes
        - a country outline (fname in shapefile format) can be highlighted
        - the level of zoom can also be specified
    """

    ax.set_extent(bbox, crs=ccrs.PlateCarree())

    if grid == True:
        gl = ax.gridlines(draw_labels=True, x_inline=False, y_inline=False, linewidth=0.5, color='gray', alpha=0.7, linestyle='--')
        gl.bottom_labels = False
        gl.left_labels = False

    if background == True:
        url = 'https://services.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/WMTS'
        layer = 'World_Imagery'
        ax.add_wmts(url, layer)
        ax.annotate('Tiles \u00A9 Esri -- Source Esri, Maxar, Earthstar Geographics, and the GIS User Community', (0.01, 0.01), xycoords='axes fraction', c='w', weight='bold',
                    fontsize='small', alpha=0.7)

    if inset:
        fname = fname

        #add inset map
        satellite_height = 35785831 / zoom

        if position:
            ax2 = ax.inset_axes(position, projection=ccrs.NearsidePerspective(central_latitude=clat,
                                    central_longitude=clon, satellite_height=satellite_height))
        else:
            ax2 = ax.inset_axes((0.1, 0.79, 0.2, 0.2), projection=ccrs.NearsidePerspective(central_latitude=clat,
                                    central_longitude=clon, satellite_height=satellite_height))

        #add coastlines and borders to inset map

        ax2.coastlines(linewidth=0.1) 

        #ax2.add_feature(borders)

        #add land and ocean to inset map

        land = cfeature.LAND
        ax2.add_feature(land)

        oceans = cfeature.OCEAN
        ax2.add_feature(oceans)

        countries = cfeature.BORDERS
        ax2.add_feature(countries, linewidth=0.1)

        #highlight country on inset map

        if fname:
            crs = ccrs.PlateCarree()
            crs_proj4 = crs.proj4_init
            shape = gpd.read_file(fname)
            country = shape.to_crs(crs_proj4)

            ax2.add_geometries(country['geometry'], crs, edgecolor='black', linewidth=0.000001, facecolor='lime', alpha=1, zorder=10) # Add linewidth=0.1 for a larger map - this is just for the teeny weeny ones

files = [scot_deglaciation, scot_outline]
gfiles = [gland_deglaciation, gland_outline]

def reproject_files(files, projection):
    shapes = []
    for i in range(len(files)):
        crs = projection
        crs_proj4 = crs.proj4_init
        shape = gpd.read_file(files[i])
        country = shape.to_crs(crs_proj4)
        shapes.append(country)
    return shapes

shapes = reproject_files(files, ccrs.OSGB())
gshapes = reproject_files(gfiles, ccrs.Stereographic(central_latitude=75, central_longitude=-40))

gshapes[0].layer = gshapes[0].layer.astype(float)
gshapes[0].sort_values(by='layer', inplace=True)
gshapes[0].reset_index(drop=True, inplace=True)
gshapes[0].layer = gshapes[0].layer.astype(str)
gshapes[0]['index_col'] = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm']
glabels = list(gshapes[0].layer)

# Define colormaps for figures:

import cmasher as cmr

cmap1 = cmr.get_sub_cmap('cmr.infinity', 0.15, 0.4)

cmap2 = cmr.get_sub_cmap('cmr.infinity', 0.4, 0.85)

fig = plt.figure(figsize=(21, 21), layout='compressed')

ax1 = fig.add_subplot(3, 2, 1, projection=ccrs.Stereographic(central_latitude=75, central_longitude=-40))
ax2 = fig.add_subplot(3, 2, 2, projection=ccrs.OSGB())

ax1.set_extent([-56.2, -24.6, 58, 84], crs=ccrs.PlateCarree())
gshapes[1].plot(ax=ax1, facecolor='none', edgecolor='k', lw=0.1)

ax2.set_extent(scotland_bbox, crs=ccrs.PlateCarree())
shapes[1].plot(ax=ax2, facecolor='none', edgecolor='k', lw=0.1)

for ax in [ax1, ax2]:
    gl = ax.gridlines(draw_labels=True, x_inline=False, y_inline=False, linewidth=0.5, color='gray', alpha=0.7, linestyle='--')
    gl.right_labels = False
    gl.bottom_labels = False

gshapes[0].plot(ax=ax1, column='index_col', cmap=cmap1, legend=True,
               legend_kwds={'title': 'Time since \ndeglaciation \n(thousand years)'
                            ,'loc': (1.04, 0.25)
                            ,'labels': glabels
                            })

shapes[0].plot(ax=ax2, column='time since', cmap=cmap2, legend=True,
               legend_kwds={'title': 'Time since \ndeglaciation \n(thousand years)'
                            ,'loc': (1.04, 0.2)
                            })

#add inset maps

ax7, ax8 = ax1.inset_axes((0.7, 0.025, 0.2, 0.2), projection=ccrs.NearsidePerspective(central_latitude=75,
                          central_longitude=-40, satellite_height = 35785831 / 5)), ax2.inset_axes((0.1, 0.79, 0.2, 0.2), projection=ccrs.NearsidePerspective(central_latitude=55,
                            central_longitude=-4, satellite_height = 35785831 / 100))

for ax in [ax7, ax8]:

    #add coastlines and borders to inset map

    ax.coastlines(linewidth=0.1) 

    #add land and ocean to inset map

    land = cfeature.LAND
    ax.add_feature(land)

    oceans = cfeature.OCEAN
    ax.add_feature(oceans)

    countries = cfeature.BORDERS
    ax.add_feature(countries, linewidth=0.1)

#highlight country on inset map

ax7.add_geometries(gshapes[1]['geometry'], crs=ccrs.Stereographic(central_latitude=75, central_longitude=-40), edgecolor='black', linewidth=0.000001, facecolor='lime', alpha=1, zorder=10)

ax8.add_geometries(shapes[1]['geometry'], crs=ccrs.OSGB(), edgecolor='black', linewidth=0.000001, facecolor='lime', alpha=1, zorder=10)

# annotate

ax1.text(0.1, 0.075, 'a', transform=ax1.transAxes,
            fontsize=16, fontweight='bold', va='top', ha='right', bbox=dict(facecolor='white', alpha=0.5, edgecolor='black', boxstyle='round,pad=0.5'))
ax2.text(0.1, 0.075, 'b', transform=ax2.transAxes,
            fontsize=16, fontweight='bold', va='top', ha='right', bbox=dict(facecolor='white', alpha=0.5, edgecolor='black', boxstyle='round,pad=0.5'))

plt.savefig('figures/study_sites.jpg', dpi=300)

scot_deglaciation = 'data/vectors/scotland/time since deglaciation.shp'
scot_geology = 'data/vectors/scotland/bedrock.shp'
scot_classification = 'data/vectors/scotland/landscape classification.shp'
scot_temperature = 'data/vectors/scotland/temperature.shp'
scot_precipitation = 'data/vectors/scotland/precipitation.shp'
scot_outline = 'data/vectors/scotland/scotland.shp'

scot_dem = rio.open('data/rasters/scotland/dsm.tif')
scot_shade = rio.open('data/rasters/scotland/hillshade.tif')
elevation = scot_dem.read(1)
hillshade = scot_shade.read(1)

bounds = scot_dem.bounds
extent = [bounds.left, bounds.right, bounds.bottom, bounds.top]

files = [scot_deglaciation, scot_geology, scot_classification, scot_temperature, scot_precipitation, scot_outline]
shapes = []

for i in range(len(files)):
    crs = ccrs.OSGB()
    crs_proj4 = crs.proj4_init
    shape = gpd.read_file(files[i])
    country = shape.to_crs(crs_proj4)
    shapes.append(country)

fig, axs = plt.subplots(3, 2, layout='compressed', subplot_kw={'projection': ccrs.OSGB()}, figsize=(17, 17))

ax1 = axs[0, 0]
ax2 = axs[0, 1]
ax3 = axs[1, 0]
ax4 = axs[1, 1]
ax5 = axs[2, 0]
ax6 = axs[2, 1]

axes = [ax1, ax2, ax3, ax4, ax5, ax6]

for ax in axes:
    ax.set_extent(extent, crs=ccrs.OSGB())

shapes[0].plot(ax=ax1, column='time since', cmap='Spectral_r', legend=True,
               legend_kwds={'title': 'Years \n(thousand)',
                            'loc': (-0.288, 0.2)})

shapes[1].plot(ax=ax3, column='bedrock', cmap='viridis_r', legend=True,
               legend_kwds={'title': 'Bedrock',
                            'loc': (-0.44, 0.4)})

shapes[2].plot(ax=ax5, column='classifica', cmap='turbo', legend=True,
               legend_kwds={'title': 'Landscape \nClassification',
                            'loc': (-0.492, 0.38)})

shapes[3].plot(ax=ax4, column='mean', cmap='coolwarm', legend=True,
               legend_kwds={'label': 'Mean Annual Temperature (\N{DEGREE SIGN}C)',
                            'shrink': 0.6,
                            'location': 'right'
                            })

shapes[4].plot(ax=ax2, column='total', cmap='Blues', legend=True,
               legend_kwds={'label': 'Total Annual Precipitation (mm)',
                            'shrink': 0.6,
                            'location': 'right'
                            })

#ax6.imshow(hillshade, origin='upper', extent=extent, transform=ccrs.)
img = ax6.imshow(elevation, origin='upper', cmap='terrain')
show(scot_shade, transform=scot_shade.transform, extent=extent, ax=ax6, cmap='gray')
show(scot_dem, transform=scot_dem.transform, extent=extent, ax=ax6, cmap='terrain', alpha=0.5)
plt.colorbar(img, ax=ax6, location='right', shrink=0.6, label='Elevation (masl)')

for ax in axes:
    shapes[5].plot(ax=ax, facecolor='none', edgecolor='k', lw=0.1)

gl = ax1.gridlines(draw_labels=True, x_inline=False, y_inline=False, linewidth=0.5, color='gray', alpha=0.7, linestyle='--')
gl.bottom_labels = False
gl.left_labels = False
#gl.right_labels = False

g2 = ax2.gridlines(draw_labels=True, x_inline=False, y_inline=False, linewidth=0.5, color='gray', alpha=0.7, linestyle='--')
g2.bottom_labels = False
g2.left_labels = False
g2.right_labels = False

g3 = ax3.gridlines(draw_labels=True, x_inline=False, y_inline=False, linewidth=0.5, color='gray', alpha=0.7, linestyle='--')
g3.bottom_labels = False
g3.left_labels = False
g3.top_labels = False
#g3.right_labels = False

g4 = ax4.gridlines(draw_labels=True, x_inline=False, y_inline=False, linewidth=0.5, color='gray', alpha=0.7, linestyle='--')
g4.bottom_labels = False
g4.left_labels = False
g4.right_labels = False
g4.top_labels = False

g5 = ax5.gridlines(draw_labels=True, x_inline=False, y_inline=False, linewidth=0.5, color='gray', alpha=0.7, linestyle='--')
#g5.bottom_labels = False
g5.left_labels = False
g5.top_labels = False

g6 = ax6.gridlines(draw_labels=True, x_inline=False, y_inline=False, linewidth=0.5, color='gray', alpha=0.7, linestyle='--')
g6.left_labels = False
#g6.bottom_labels = False
g6.right_labels = False
g6.top_labels = False

ax1.text(0.1, 0.96, 'a', transform=ax1.transAxes,
            fontsize=16, fontweight='bold', va='top', ha='right', bbox=dict(facecolor='white', alpha=0.5, edgecolor='black', boxstyle='round,pad=0.5'))
ax2.text(0.1, 0.96, 'b', transform=ax2.transAxes,
            fontsize=16, fontweight='bold', va='top', ha='right', bbox=dict(facecolor='white', alpha=0.5, edgecolor='black', boxstyle='round,pad=0.5'))
ax3.text(0.1, 0.96, 'c', transform=ax3.transAxes,
            fontsize=16, fontweight='bold', va='top', ha='right', bbox=dict(facecolor='white', alpha=0.5, edgecolor='black', boxstyle='round,pad=0.5'))
ax4.text(0.1, 0.96, 'd', transform=ax4.transAxes,
            fontsize=16, fontweight='bold', va='top', ha='right', bbox=dict(facecolor='white', alpha=0.5, edgecolor='black', boxstyle='round,pad=0.5'))
ax5.text(0.1, 0.96, 'e', transform=ax5.transAxes,
            fontsize=16, fontweight='bold', va='top', ha='right', bbox=dict(facecolor='white', alpha=0.5, edgecolor='black', boxstyle='round,pad=0.5'))
ax6.text(0.08, 0.96, 'f', transform=ax6.transAxes,
            fontsize=16, fontweight='bold', va='top', ha='right', bbox=dict(facecolor='white', alpha=0.5, edgecolor='black', boxstyle='round,pad=0.5'))

plt.savefig('figures/scotland_variables.jpg', dpi=300)

deglaciation = 'data/vectors/greenland/time since deglaciation.shp'
bedrock = 'data/vectors/greenland/bedrock.shp'
classification = 'data/vectors/greenland/landscape classification.shp'
outline = 'data/vectors/greenland/GRL_adm0.shp'

prcp = rio.open('data/rasters/greenland/climate/precipitation/precipitation.tif')
temp = rio.open('data/rasters/greenland/climate/temperature/temperature.tif')
elevation = rio.open('data/rasters/greenland/dem.tif')
hillshade = rio.open('data/rasters/greenland/hillshade.tif')
dem = elevation.read(1)
bounds = elevation.bounds
demextent = [bounds.left, bounds.right, bounds.bottom, bounds.top]
extent = [-55, -27, 58, 84]

files = [deglaciation, bedrock, classification, outline]
shapes = []

for i in range(len(files)):
    crs = ccrs.Stereographic(central_latitude=75, central_longitude=-40)
    crs_proj4 = crs.proj4_init
    shape = gpd.read_file(files[i])
    country = shape.to_crs(crs_proj4)
    shapes.append(country)

shapes[0].layer = shapes[0].layer.astype(float)
shapes[0].sort_values(by='layer', inplace=True)
shapes[0].reset_index(drop=True, inplace=True)
shapes[0].layer = shapes[0].layer.astype(str)
shapes[0]['index_col'] = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm']
shapes[0]

labels = list(shapes[0].layer)

fig, axs = plt.subplots(3, 2, layout='compressed', subplot_kw={'projection': ccrs.Stereographic(central_latitude=75, central_longitude=-40)}, figsize=(17, 17))

ax1 = axs[0, 0]
ax2 = axs[0, 1]
ax3 = axs[1, 0]
ax4 = axs[1, 1]
ax5 = axs[2, 0]
ax6 = axs[2, 1]

axes = [ax1, ax2, ax3, ax4, ax5, ax6]

for ax in axes:
    ax.set_extent(extent, crs=ccrs.PlateCarree())

shapes[0].plot(ax=ax1, column='index_col', cmap='Spectral_r', legend=True,
               legend_kwds={'title': 'Years \n(thousand)',
                            'loc': (-0.345, 0.2),
                            'labels':labels})

shapes[1].plot(ax=ax3, column='bedrock', cmap='viridis_r', legend=True,
               legend_kwds={'title': 'Bedrock',
                            'loc': (-0.527, 0.4)})

shapes[2].plot(ax=ax5, column='classifica', cmap='turbo', legend=True,
               legend_kwds={'title': 'Landscape \nClassification',
                            'loc': (-0.588, 0.38)})

dst_crs = ax6.projection.proj4_init

with WarpedVRT(elevation, crs=dst_crs) as vrt_dem:
    with WarpedVRT(hillshade, crs=dst_crs) as vrt_hs:
        with WarpedVRT(prcp, crs=dst_crs) as vrt_prcp:
            with WarpedVRT(temp, crs=dst_crs) as vrt_temp:
                dem_arr = vrt_dem.read(1)
                dem_masked = np.ma.masked_equal(dem_arr, vrt_dem.nodata)        # mask nodata -> transparent
                show(dem_masked, transform=vrt_dem.transform, ax=ax6, cmap='terrain')

                hs_arr = vrt_hs.read(1)
                hs_masked = np.ma.masked_equal(hs_arr, vrt_hs.nodata)
                show(hs_masked, transform=vrt_hs.transform, ax=ax6, cmap='gray', alpha=0.5)

                temp_arr = vrt_temp.read(1)
                temp_masked = np.ma.masked_equal(temp_arr, vrt_temp.nodata)
                show(temp_masked, transform=vrt_temp.transform, ax=ax4, cmap='coolwarm')

                prcp_arr = vrt_prcp.read(1)
                prcp_masked = np.ma.masked_equal(prcp_arr, vrt_prcp.nodata)
                show(prcp_masked, transform=vrt_prcp.transform, ax=ax2, cmap='Blues')

plt.colorbar(ax6.images[0], ax=ax6, location='right', shrink=0.6, label='Elevation (masl)')
plt.colorbar(ax4.images[0], ax=ax4, location='right', shrink=0.6, label='Mean Annual Temperature (\N{DEGREE SIGN}C)')
plt.colorbar(ax2.images[0], ax=ax2, location='right', shrink=0.6, label='Total Annual Precipitation (mm)')

for ax in axes:
    shapes[3].plot(ax=ax, facecolor='none', edgecolor='k', lw=0.1)

gl = ax1.gridlines(draw_labels=True, x_inline=False, y_inline=False, linewidth=0.5, color='gray', alpha=0.7, linestyle='--')
gl.bottom_labels = False
gl.left_labels = False
#gl.right_labels = False

g2 = ax2.gridlines(draw_labels=True, x_inline=False, y_inline=False, linewidth=0.5, color='gray', alpha=0.7, linestyle='--')
g2.bottom_labels = False
g2.left_labels = False
g2.right_labels = False

g3 = ax3.gridlines(draw_labels=True, x_inline=False, y_inline=False, linewidth=0.5, color='gray', alpha=0.7, linestyle='--')
g3.bottom_labels = False
g3.left_labels = False
g3.top_labels = False
#g3.right_labels = False

g4 = ax4.gridlines(draw_labels=True, x_inline=False, y_inline=False, linewidth=0.5, color='gray', alpha=0.7, linestyle='--')
g4.bottom_labels = False
g4.left_labels = False
g4.right_labels = False
g4.top_labels = False

g5 = ax5.gridlines(draw_labels=True, x_inline=False, y_inline=False, linewidth=0.5, color='gray', alpha=0.7, linestyle='--')
#g5.bottom_labels = False
g5.left_labels = False
g5.top_labels = False

g6 = ax6.gridlines(draw_labels=True, x_inline=False, y_inline=False, linewidth=0.5, color='gray', alpha=0.7, linestyle='--')
g6.left_labels = False
#g6.bottom_labels = False
g6.right_labels = False
g6.top_labels = False

ax1.text(0.12, 0.96, 'a', transform=ax1.transAxes,
            fontsize=16, fontweight='bold', va='top', ha='right', bbox=dict(facecolor='white', alpha=0.5, edgecolor='black', boxstyle='round,pad=0.5'))
ax2.text(0.12, 0.96, 'b', transform=ax2.transAxes,
            fontsize=16, fontweight='bold', va='top', ha='right', bbox=dict(facecolor='white', alpha=0.5, edgecolor='black', boxstyle='round,pad=0.5'))
ax3.text(0.12, 0.96, 'c', transform=ax3.transAxes,
            fontsize=16, fontweight='bold', va='top', ha='right', bbox=dict(facecolor='white', alpha=0.5, edgecolor='black', boxstyle='round,pad=0.5'))
ax4.text(0.12, 0.96, 'd', transform=ax4.transAxes,
            fontsize=16, fontweight='bold', va='top', ha='right', bbox=dict(facecolor='white', alpha=0.5, edgecolor='black', boxstyle='round,pad=0.5'))
ax5.text(0.12, 0.96, 'e', transform=ax5.transAxes,
            fontsize=16, fontweight='bold', va='top', ha='right', bbox=dict(facecolor='white', alpha=0.5, edgecolor='black', boxstyle='round,pad=0.5'))
ax6.text(0.1, 0.96, 'f', transform=ax6.transAxes,
            fontsize=16, fontweight='bold', va='top', ha='right', bbox=dict(facecolor='white', alpha=0.5, edgecolor='black', boxstyle='round,pad=0.5'))

plt.savefig('figures/greenland_variables.jpg', dpi=300)

