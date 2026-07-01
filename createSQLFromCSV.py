import sqlite3
import pandas as pd
import os
import sys
from collections import defaultdict
import math
 
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

        self.col_names = []

    def removeSpecCharFromCol(self):

        self.df.columns = self.df.columns.str.replace(r'\s+', '_', regex=True)

        self.df.columns = self.df.columns.str.replace(r'\(', '_', regex=True)

        self.df.columns = self.df.columns.str.replace(r'\)', '_', regex=True)

        self.df.columns = self.df.columns.str.replace(r'\.', '', regex=True)
        # add something here to say if there is a row that is not the name it needs to be then print the df.columns name and exit sys
    
    def makeTable(self, table_name):

        return self.table_factory.make_table(table_name)
    
    def getColumnDictionary(self):

        return self.col_names
    
    def commit(self, table):

        return self.table_factory.commit(table)
    
    def parseRows(self, table):

        for row in self.df.itertuples():

            record = self.parseRow(table, row)

            self.publishRow(table, record)

            # want to add something here that says publish every x amount of rows

            self.commit(table)

    def publishRow(self, table, record):

        self.table_factory.update_record(table, record)
    
    def parseRow(self, table, row):

        column_dictionary = self.getColumnDictionary()

        row_values = {}

        for colName in column_dictionary:

            value = getattr(row, colName)

            if self.isNaN(value):

                continue

            if not self.table_factory.doesColumnExist(table, colName):

                #print("Column Does Not Exist")

                self.table_factory.make_column(table, colName, value)

                self.commit(table)

                row_values[colName] = value

            else: 

                #print("Column Does Exist")

                row_values[colName] = value

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

    def checkColNames(self, *args):

        #call df.columns to fix all col names here 
        
        self.removeSpecCharFromCol()

        #sample data gives numbers for some columns, whereas df.columns retrieves the actual col names

        sample_data = next(self.df.itertuples())

        i = 2 

        if len(args)==0:

            self.checkdfColNames(sample_data)

            #if names pass tests, then can set col_names to df.columns

            self.col_names = list(self.df.columns)

        #if column names are known and certain columns want to be made to make a specific table

        if len(args)==1:
            
            self.checkdfColNames(sample_data)

            self.checkUserColNames(list(self.df.columns), args[0])

            #if names pass tests, then can set col_names to user entered col_names

            self.col_names = args[0]

        #for now, columns entered must be part of an array
        if len(args)>1:

            print("Too many arguments entered")

            sys.exit()
        
        return True



if __name__ == "__main__":
    #file = sys.stderr
    #print(file)
    File = manageFile("extract3.csv")
    table = File.makeTable("testNPIRow")
    File.checkColNames(["NPI"])
    File.parseRows(table)
