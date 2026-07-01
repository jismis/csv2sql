import pandas as pd
import math

df = pd.read_csv('extract3.csv')


n=1

# for i in range(n):
#     for row in df.itertuples():
#         print(row)

df.columns = df.columns.str.replace(r'\s+', '_', regex=True)
df.columns = df.columns.str.replace(r'\(', '_', regex=True)
df.columns = df.columns.str.replace(r'\)', '_', regex=True)
df.columns = df.columns.str.replace(r'\.', '', regex=True)

sample_data = next(df.itertuples())
print(list(df.columns))
print('NPI' in list(df.columns))

# for col, val in zip(df.columns, sample_data[1:]):
#     print(f"{col}: {val}")





#print(sample_data.Index)

#need to also know what position column it is in? 

# row_idx = sample_data.Index
#     # will have to associate column names with numbers
#     # Iterate through the DataFrame's column names to dynamically match the data

# column_names = {}
# i = 2 
# for colName in df.columns:
#     print(colName)
#     if hasattr(sample_data, colName):
#         column_names[colName] = colName
#         continue
#     entryName = "_" + str(i)
#     column_names[colName] = entryName

#     i = i+1


# for colName in df.columns:
#         # Use getattr to safely pull the value matching the column name string
#     value = getattr(sample_data, column_names[colName])
#     # if isinstance(column_names[col_name], int):
#     #     name = "_" + str(column_names[col_name])
#     #     value = getattr(sample_data, df.columns[name])
#     # else: 
#     #     value = getattr(sample_data, df.columns[col_name])
        
#     print(f"Index: {row_idx} | Column: {colName} | Value: {value}")

# for value in sample_data:
#     isNan = False
#     if isinstance(value, float):
#         isNan = math.isnan(value)
    
#     if not isNan: 
#         print(value)
#print(df)



#column_info = df.dtypes

