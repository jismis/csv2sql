import zipfile
import pandas as pd  # Example data processing library

# 1. Define paths and the specific internal filename needed
zip_archive_path = "extract3.zip"
internal_file_name = "extract3.csv"

# 2. Open the zip archive without decompressing to disk
with zipfile.ZipFile(zip_archive_path, "r") as archive:
    # 3. Read the specific file into memory
    with archive.open(internal_file_name) as file_stream:
        # 4. Pass the stream directly into your Python function
        chunk_size = 100

        for chunk in pd.read_csv(file_stream, chunksize = chunk_size):

            chunk.columns = chunk.columns.str.replace(r'\s+', '_', regex=True)
            chunk.columns = chunk.columns.str.replace(r'\(', '_', regex=True)
            chunk.columns = chunk.columns.str.replace(r'\)', '_', regex=True)
            chunk.columns = chunk.columns.str.replace(r'\.', '', regex=True)
            for row in chunk.itertuples():
                print (getattr(row,"Provider_License_Number_State_Code_1"))
            

# Continue your Python program using the data


