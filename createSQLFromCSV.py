import sqlite3
import pandas as pd
import os
import sys
from collections import defaultdict
import math
import re


from csvSchema import TableFactory 

#opens csv, goes through each record, only adds column if there is a value recorded in the record
#need to check if we need an extra table to store certain repeating values to avoid adding a ton of columns

#open csv in chunks
#for row in csv, find values 
#if value, check if column exists and create record
#check column name to put it into appropriate table

class manageFile:

    def __init__(self, file_name, table_factory = TableFactory()):
        self.df = pd.read_csv(file_name)
        self.table_factory = table_factory
        self.col_dictionary = {}

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
            record = self.parseRow(row)
            self.publishRow(record, "NPI")
            # want to add something here that says publish every x amount of rows
            for key in self.table_factory.getTableList():
                print(key)
                self.commit(key)

    def publishRow(self, record, code):
        if code == "NPI":
            table = self.publishRowNPI(record)
        
        return table 

    def publishRowHelper(self, table, record):
        self.table_factory.update_record(table, record)
    
# record is array of tuples 
# returns table it was published in 
    def publishRowNPI(self, record):
        #NPI is type array
        NPI = record["NPI"][0]
        
        for field, entry in record.items(): 
            updatedRecord = {}
            print(field)
            if field == "NPI": 
                continue
            if field == "Healthcare_Provider_Taxonomy_Code" or field == "Provider_License_Number" or field == "Provider_License_Number_State_Code" or field == "Healthcare_Provider_Primary_Taxonomy_Switch":
                for item in entry:
                    updatedRecord[field] = item[0]
                    updatedRecord["_id"] = str(NPI[0]) + "." + str(item[1])
                    updatedRecord["NPI"] = NPI[0]
                    self.publishRowHelper("Taxonomy_and_License_Information", updatedRecord)
                continue
                    
            if field == "Other_Provider_Identifier_Issuer":
                for item in entry:
                    updatedRecord[field] = item[0]
                    updatedRecord["_id"] = str(NPI[0]) + "." + str(item[1])
                    updatedRecord["NPI"] = NPI[0]
                    self.publishRowHelper("Other_Provider_Identifier_Issuer", updatedRecord)
                continue

            if field == "Healthcare_Provider_Taxonomy_Group":
                for item in entry: 
                    updatedRecord[field] = item[0]
                    updatedRecord["_id"] = str(NPI[0]) + "." + str(item[1])
                    updatedRecord["NPI"] = NPI[0]
                    self.publishRowHelper("Healthcare_Provider_Taxonomy_Group", updatedRecord)
                continue


            for item in entry:
                updatedRecord[field] = item[0]
                updatedRecord["NPI"] = NPI[0]
                self.publishRowHelper("NPI_Table", updatedRecord)
                    

# To get table from NPI table. Need to perhaps create a class NPI just to deal with the specific NPI case
    def getTable(self, field):
        if field == "Healthcare_Provider_Taxonomy_Code" or field == "Provider_License_Number" or field == "Provider_License_Number_State_Code" or field == "Healthcare_Provider_Primary_Taxonomy_Switch":
            return "Taxonomy_and_License_Information"

        if field == "Other_Provider_Identifier_Issuer":
            return "Other_Provider_Identifier_Issuer"
  
        if field == "Healthcare_Provider_Taxonomy_Group":
            return "Healthcare_Provider_Taxonomy_Group"
        
        return "NPI_Table"

    def parseRow(self, row):
        col_dictionary = self.getColumnDictionary()
        row_values = defaultdict(list)
        #new_field is [field name, integer]
        for old_field, new_field in col_dictionary.items():
            value = getattr(row, old_field)

            if self.isNaN(value):
                continue
            
            table = self.getTable(new_field[0])

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
            print(database_col)
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

        # if len(args)==0:
        #     self.checkdfColNames(sample_data)

        #     #if names pass tests, then can set col_dictionary to df.columns

        #     for name in list(self.df.columns):
        #         self.col_dictionary[name] = name

        # #if column names are known and certain columns want to be made to make a specific table

        # if len(args) == 1: 
        #     self.checkdfColNames(sample_data)
        #     self.checkUserColNames(list(self.df.columns), args[0])

        #     #if names pass tests, then can set col_dictionary to user entered col_dictionary

        #     for name in args[0]:
        #         newName, integer = self.makeNPIColNames(name)
        #         self.col_dictionary[name] = [newName, integer]

        # if len(args) == 2: 
        #     self.checkdfColNames(sample_data)
        #     self.checkUserColNames(list(self.df.columns), args[0])
        #     original_array = args[0]
        #     new_array = args[1]
        #     self.checkArrayLength(original_array, new_array)

        #     for i in range(len(original_array)):
        #         self.col_dictionary[original_array[i]] = new_array[i]


        # #for now, columns entered must be part of an array
        # if len(args)>1:
        #     print("Too many arguments entered")
        #     sys.exit()

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
    File = manageFile("extract3.csv")
    File.makeTable("NPI_Table", "NPI")
    File.makeTable("Taxonomy_and_License_Information", "NPI")
    File.makeTable("Other_Provider_Identifier_Issuer", "NPI")
    File.makeTable("Healthcare_Provider_Taxonomy_Group", "NPI")


    File.makeNPIColNames()
    


    File.parseRows()

