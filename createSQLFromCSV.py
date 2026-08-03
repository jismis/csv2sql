import sqlite3
import pandas as pd
import os
import sys
from collections import defaultdict
import math
import re


from csvSchema import TableFactory 
from npiCSV import npiFileHelper

#opens csv, goes through each record, only adds column if there is a value recorded in the record
#need to check if we need an extra table to store certain repeating values to avoid adding a ton of columns

#open csv in chunks
#for row in csv, find values 
#if value, check if column exists and create record
#check column name to put it into appropriate table

class manageFile:

    def __init__(self, file_name, code, table_factory = TableFactory()):
        self.df = pd.read_csv(file_name)
        self.table_factory = table_factory
        self.col_dictionary = {}
        self.code = code
        self.id_ = 0

    def getId(self):
        return self.id_

    def incrementId(self):
        self.id_ = self.id_ + 1
        return self.id_
    
    def removeSpecCharFromCol(self):
        self.df.columns = self.df.columns.str.replace(r'\s+', '_', regex=True)
        self.df.columns = self.df.columns.str.replace(r'\(', '_', regex=True)
        self.df.columns = self.df.columns.str.replace(r'\)', '_', regex=True)
        self.df.columns = self.df.columns.str.replace(r'\.', '', regex=True)
        # add something here to say if there is a row that is not the name it needs to be then print the df.columns name and exit sys
    
    def makeTable(self, table_name, parent_table=""):
        return self.table_factory.make_table(table_name, parent_table)
    
    def getColumnDictionary(self):
        return self.col_dictionary
    
    def commit(self, table):
        return self.table_factory.commit(table)
    
    def parseRows(self):
        for row in self.df.itertuples():
            record = self.parseRow(row, self.code)
            self.publishRow(record, self.code)
            # want to add something here that says publish every x amount of rows
            for key in self.table_factory.getTableList():
                self.commit(key)

    def publishRow(self, record, code):
        if code == "TAX":
            self.publishRowTax(record)
        if code == "NPI":
            self.publishRowNPI(record)
        
    
# record is array of tuples 
# returns table it was published in 
    def publishRowNPI(self, record):
        #NPI is type array
        NPI = record["NPI"][0]
        npi = npiFileHelper()
        
        for field, entry in record.items(): 
            updatedRecord = {}
            if field == "NPI": 
                continue

            #IS THE ISSUE UPDATEDRECORD?
            updatedRecordList = npi.publishRowNPI(NPI, field, entry, updatedRecord)
            #print(f''' field {field} and entry {entry}''')
            #print(f'''updatedRecordList {updatedRecordList}''')

            for item in updatedRecordList:
                table_name = item[0]
                updated_record = item[1]

                if table_name == "Error":
                    print("There is an issue with the NPI table/column names")
                    break

                self.publishRowHelper(table_name, updated_record)

    def publishRowTax(self, record):
        rowID = record['_id'][0][0]
        for field, entry in record.items():
            print(f'''field {field}, entry {entry}''')
            updated_record = {}
            for item in entry:
                updated_record['_id'] = rowID
                updated_record[field] = item[0]

                self.publishRowHelper("Taxonomy_Codes", updated_record)
            ##### NEED TO FINISH THIS 


    def publishRowHelper(self, table, record):
        self.table_factory.update_record(table, record)
                    

# To get table from NPI table. Need to perhaps create a class NPI just to deal with the specific NPI case


    def parseRow(self, row, code):
        # if code == "":
        #     return self.parseRowNoCode(row)
        if code == "TAX":
            return self.parseRowTax(row)
        if code == "NPI":
            return self.parseRowNPI(row)

    def parseRowTax(self, row):
        col_dictionary = self.getColumnDictionary()
        row_values = defaultdict(list)
        row_values["_id"].append((self.getId(), None))
        self.incrementId()
        for old_field, new_field in col_dictionary.items():
            value = getattr(row, old_field)
            print(f'''field is {new_field} and value is {value}''')
            if self.isNaN(value):
                continue

            table = "Taxonomy_Codes"

            if not self.table_factory.doesColumnExist(table, new_field[0]):
                self.table_factory.make_column(table, new_field[0], value)
                self.commit(table)
                row_values[new_field[0]].append((value, new_field[1]))

            else:
                row_values[new_field[0]].append((value, new_field[1]))

        return row_values

    def parseRowNPI(self, row):
        col_dictionary = self.getColumnDictionary()
        row_values = defaultdict(list)
        npi = npiFileHelper()
        #new_field is [field name, integer]
        for old_field, new_field in col_dictionary.items():
            value = getattr(row, old_field)

            if self.isNaN(value):
                continue
            
            table = npi.getTable(new_field[0])

            if table == "Error":
                print("Error in columns for NPI file")
                break

            #print(new_field)

            if not self.table_factory.doesColumnExist(table, new_field[0]):
                #print("Column Does Not Exist")
                self.table_factory.make_column(table, new_field[0], value)
                self.commit(table)
                row_values[new_field[0]].append((value, new_field[1]))
            
            #if column exists and already has a value, make a new entry? 
            else: 
                #print("Column Does Exist")
                row_values[new_field[0]].append((value, new_field[1]))

        return row_values

    
    def isNaN(self, value):
        isNan = False

        if isinstance(value, float):
            isNan = math.isnan(value)
            return isNan
        
        return isNan

#checkdfColNames makes sure all special characters in database name have been found and addressed

    def checkdfColNames(self, sample_data):
        end = False

        for colName in self.df.columns:

            if not hasattr(sample_data, colName):
                print(f'''Invalid Column Name in Database: {colName}''')
        
        if end:
            sys.exit()

#checkUserColNames checks user columns against columns in the database after all of the columns of the database have been checked with checkdfColNames
#database_col and user_input must be lists

    def checkUserColNames(self, database_col, user_input):
        end = False

        for name in user_input:

            if not name in database_col:
                print(f'''{name} is not found in column names''')
                end = True
        
        if end:
            print(f'''database_col {database_col}''')
            sys.exit()

#need to check that the length replacement column names matches that of original names 
    def checkArrayLength(self, original_array, new_array):

        if len(original_array) == len(new_array):
            return True
        
        else: 
            print(f"Original ({len(original_array)}) and New Names({len(new_array)}) Array Lengths Do Not Match")
            sys.exit()

#making column names that my have other address_2

    def makeNPIColNames(self):
        self.removeSpecCharFromCol()
        for col_name in self.df.columns:
            newName, integer = self.makeNPIColNamesHelper(col_name)
            self.col_dictionary[col_name] = [newName, integer]
    
    def makeNPIColNamesHelper(self, field):
        match = re.search(r'_\d+$', field)
   
        if match:
            # Split the string at the start of the matched digits
            part1 = field[:match.start()]
            part2 = field[match.start()+1:]
            return part1, int(part2)
        return field, None
    

    def checkColNames(self, *args): 
        #call df.columns to fix all col names here         
        self.removeSpecCharFromCol()

        self.col_dictionary

        return True
    

    # def replaceColName(self, original, new):
    #     dict = {}
    #     dict[original] = new
    #     return dict

#table 1 ("NPI_Base_Table"): ["NPI", "Entity_Type_Code", "Replacement_NPI", "Employer_Identification_Number__EIN_"]
#table 2: ["NPI", "Provider_Organization_Name__Legal_Business_Name_", "Provider_Last_Name__Legal_Name_", 
                   #"Provider_First_Name", "Provider_Middle_Name", "Provider_Name_Prefix_Text", "Provider_Name_Suffix_Text", 
                   #"Provider_Credential_Text", "Provider_Other_Organization_Name", "Provider_Other_Organization_Name_Type_Code",
                   #"Provider_Other_Last_Name", "Provider_Other_First_Name", "Provider_Other_Middle_Name", 
                  # "Provider_Other_Name_Prefix_Text", "Provider_Other_Name_Suffix_Text", "Provider_Other_Credential_Text",
                   #"Provider_Other_Last_Name_Type_Code"]

            #table 2: want to add type legal and type other       

              
if __name__ == "__main__":
    #file = sys.stderr
    #print(file)
    File = manageFile("nucc_taxonomy_261.csv", "TAX")
    #File.makeTable("NPI_Table", "NPI")
    #File.makeTable("Taxonomy_and_License_Information", "NPI")
    #File.makeTable("Provider_Name", "NPI")
    # File.makeTable("Taxonomy_Table", "NPI")
    # File.makeTable("Other_Provider_Name", "NPI")
    # File.makeTable("Address_Information", "NPI")
    # File.makeTable("Healthcare_Provider_Taxonomy_Group", "NPI")
    # File.makeTable("Enumeration_Deactivation_Reactivation_Dates", "NPI")
    # File.makeTable("Parent_Organizations", "NPI")
    # File.makeTable("Official_Name_And_Sex", "NPI")
    File.makeTable("Taxonomy_Codes")
    File.makeNPIColNames()
    


    File.parseRows()

