# import required libraries
from osgeo import gdal
from pathlib import Path

asc_folder = Path('data/rasters/scotland/ascs')
dem_folder = Path('data/rasters/scotland/dems')
dem_folder.mkdir(parents=True, exist_ok=True)

for asc in asc_folder.iterdir():


def convert_asc_to_tif(src_folder, dest_folder):
    # Create destination folder if it doesn't exist
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    
    # Find all .asc files in the source folder
    raster_files = glob.glob(os.path.join(src_folder, '*.asc'))
    
    # Iterate through all files
    for raster_path in raster_files:
        filename = os.path.basename(raster_path)
        
        # Define the output path in the single output folder
        tif_filename = filename.replace('.asc', '.tif')
        dest_path = os.path.join(dest_folder, tif_filename)
        
        # Check if the output file already exists
        if not os.path.exists(dest_path):
            # Open the .asc file using GDAL
            asc_dataset = gdal.Open(raster_path)
            
            # Create the output .tif file
            driver = gdal.GetDriverByName('GTiff')
            tif_dataset = driver.CreateCopy(dest_path, asc_dataset, 0)
            
            # Close the datasets
            asc_dataset = None
            tif_dataset = None
            
            print(f"Converted: {raster_path} -> {dest_path}")
        else:
            print(f"File {dest_path} already exists. Skipping.")
    
    print("Conversion complete.")

# Example usage:
source_directory = r"F:\PhD\Data\Scotland\rasters\dem_asc"
destination_directory = r"F:\PhD\Data\Scotland\rasters\dem"
convert_asc_to_tif(source_directory, destination_directory)
