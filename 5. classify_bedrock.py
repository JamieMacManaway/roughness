# load required libraries
import geopandas as gpd
import pandas as pd

# read in datasets
scotland = gpd.read_file('data/vectors/scotland/scotland.shp').to_crs(epsg=27700)
geology_uk = gpd.read_file('data/vectors/scotland/gb_625k_v5_bedrock_geology_polygons.shp', columns=['RCS_D']).to_crs(epsg=27700)
geology_greenland = gpd.read_file('data/vectors/greenland/G500_24_06_2024.gpkg', layer='g500_geology_polygon', 
columns=['Header', 'Long_description']).to_crs(epsg=3413)

# clip uk dataset to outline of scotland
geology_scotland = geology_uk.clip(scotland)

# classify bedrock for scotland
scottish_igneous_bedrock = [
    "ANORTHOSITE", "DOLERITE AND THOLEIITIC BASALT", "FELSIC LAVA AND FELSIC TUFF",
    "FELSIC-ROCK", "MAFIC IGNEOUS-ROCK", "MAFIC LAVA AND MAFIC TUFF", "MAFITE",
    "SYENITIC-ROCK", "ULTRAMAFITITE", "PYROCLASTIC-ROCK",
    "LAVA, TUFF, VOLCANICLASTIC ROCK AND SEDIMENTARY ROCK"  # Mixed classification, but predominantly igneous
]

scottish_metamorphic_bedrock = [
    "GNEISS", "MAFIC GNEISS", "GNEISSOSE PSAMMITE AND GNEISSOSE SEMIPELITE",
    "GNEISSOSE SEMIPELITE AND GNEISSOSE PSAMMITE", "GRAPHITIC PELITE, CALCAREOUS PELITE, CALCSILICATE-ROCK AND PSAMMITE",
    "METALIMESTONE", "METASEDIMENTARY ROCK", "MIGMATITIC ROCK", "MYLONITIC-ROCK AND FAULT-BRECCIA",
    "SCHIST", "SERPENTINITE, METABASALT, METALIMESTONE AND PSAMMITE",
    "SEMIPELITE", "SEMIPELITE AND PELITE",
    "PSAMMITE", "PSAMMITE AND PELITE", "PSAMMITE AND SEMIPELITE", 
    "PSAMMITE, PELITE, SEMIPELITE AND CALCSILICATE-ROCK", "PSAMMITE, SEMIPELITE AND PELITE", "QUARTZITE"
]

scottish_sedimentary_bedrock = [
    "BRECCIA, CONGLOMERATE AND SANDSTONE", "CONGLOMERATE AND [SUBEQUAL/SUBORDINATE] SANDSTONE, INTERBEDDED",
    "CONGLOMERATE, SANDSTONE, SILTSTONE AND MUDSTONE", "LIMESTONE, ARGILLACEOUS ROCKS AND SUBORDINATE SANDSTONE, INTERBEDDED",
    "SANDSTONE AND CONGLOMERATE, INTERBEDDED", "SANDSTONE, MUDSTONE, SILTSTONE AND CONGLOMERATE",
    "QUARTZ-ARENITE", "MUDSTONE, SILTSTONE AND SANDSTONE", "MUDSTONE, CHERT AND SMECTITE-CLAYSTONE",
    "MUDSTONE, SANDSTONE AND LIMESTONE", "MUDSTONE, SILTSTONE, LIMESTONE AND SANDSTONE",
    "SANDSTONE, SILTSTONE AND MUDSTONE", "SANDSTONE WITH SUBORDINATE ARGILLACEOUS ROCKS",
    "SANDSTONE, BRECCIA AND CONGLOMERATE", "WACKE", "LIMESTONE, SANDSTONE, SILTSTONE AND MUDSTONE", "PELITE",
    "DOLOSTONE", "DIAMICTITE", "SEDIMENTARY ROCK CYCLES, CLACKMANNAN GROUP TYPE", "SEDIMENTARY ROCK CYCLES, STRATHCLYDE GROUP TYPE",
    "MUDSTONE, SANDSTONE AND CONGLOMERATE", "MUDSTONE, SILTSTONE, SANDSTONE, COAL, IRONSTONE AND FERRICRETE",
    "SANDSTONE WITH SUBORDINATE ARGILLACEOUS ROCKS AND LIMESTONE", "SANDSTONE WITH SUBORDINATE CONGLOMERATE AND SILTSTONE",
    "SANDSTONE WITH SUBORDINATE CONGLOMERATE, SILTSTONE AND MUDSTONE", "GRAVEL, SAND, SILT AND CLAY", "LIMESTONE WITH SUBORDINATE SANDSTONE AND ARGILLACEOUS ROCKS",
    "SANDSTONE AND MUDSTONE"
]

geology_scotland['bedrock'] = ['igneous' if x in scottish_igneous_bedrock 
                                else 'metamorphic' if x in scottish_metamorphic_bedrock 
                                else 'sedimentary' if x in scottish_sedimentary_bedrock 
                                else 'unclassified' for x in geology_scotland['RCS_D']]

bedrock_scotland = geology_scotland.drop('RCS_D', axis=1).dissolve(by='bedrock', as_index=False)

# classify bedrock for greenland
igneous_terms = ["basalt", "syenite", "gabbro", "granite", "lava", "tuff", "nepheline", "volcanic", "dolerite", "ultramafic", "intrusive suite", "hydrothermally altered", "pillow breccias",
    "hyloclastites", "North Atlantic Igneous Province", "carbonatite", "diorite", "monzonite", "granodiorite", "quartz diorite",
    "sill", "dyke", "intrusive", "Igdlerfigssalik", "dunite", "trachyte", "effusive", "Gardar Province", "granitoid", "post-migmatitic"]
metamorphic_terms = ["gneiss", "schist", "quartzite", "migmatite", "mylonite", "amphibolite", "Supergroup", "undivided", "tectonically interleaved", "Proterozoic metamorphism", "marble", "metasedimentary", "foliated", "metagranitoid",
    "quartzofeldspathic", "greenstones", "migmatitic", "metasediments", "siliceous", "tectonised"
]
sedimentary_terms = ["sandstone", "mudstone", "limestone", "siltstone", "conglomerate", "shale", "clastic", "basin", "shelf", "deltaic deposits", "intercratonic sediments", "continental sediments", "glaciofluvial", "marine deposits", "moraine", "colluvium", "unconsolidated sand",
    "Kap København Formation", "greywacke", "marine silt", "dolomites", "Store Koldewey Formation", "Slottet Formation"
]

# merge description and header for better classification
geology_greenland["combined_text"] = geology_greenland["Long_description"].fillna("") + " " + geology_greenland["Header"].fillna("")

# classify formations
greenland_igneous = geology_greenland[geology_greenland["combined_text"].str.contains('|'.join(igneous_terms), case=False, na=False)]
greenland_metamorphic = geology_greenland[geology_greenland["combined_text"].str.contains('|'.join(metamorphic_terms), case=False, na=False)]
greenland_sedimentary = geology_greenland[geology_greenland["combined_text"].str.contains('|'.join(sedimentary_terms), case=False, na=False)]

greenland_igneous = greenland_igneous.dissolve()
greenland_metamorphic = greenland_metamorphic.dissolve()
greenland_sedimentary = greenland_sedimentary.dissolve()

greenland_igneous['bedrock'] = 'igneous'
greenland_metamorphic['bedrock'] = 'metamorphic'
greenland_sedimentary['bedrock'] = 'sedimentary'

bedrock_greenland = pd.concat([greenland_igneous, greenland_metamorphic, greenland_sedimentary])

bedrock_greenland.drop(['Header', 'Long_description', 'combined_text'], axis=1, inplace=True)

# save datasets to file
bedrock_scotland.to_file('data/vectors/scotland/bedrock.shp')
bedrock_greenland.to_file('data/vectors/greenland/bedrock.shp')