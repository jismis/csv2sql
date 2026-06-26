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
        self.column_names = {}
    
    def makeTable(self, table_name):
        return self.table_factory.make_table(table_name)
    
    def getColumnDictionary(self):
        return self.column_names
    
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
        for colName in self.df.columns:
            value = getattr(row, column_dictionary[colName])
            if self.isNaN(value):
                continue

            if not self.table_factory.doesColumnExist(table, colName):
                print("Column Does Not Exist")
                self.table_factory.make_column(table, colName, value)
                self.commit(table)
                row_values[colName] = value

            else: 
                print("Column Does Exist")
                row_values[colName] = value
        return row_values
    
    def isNaN(self, value):
        isNan = False
        if isinstance(value, float):
            isNan = math.isnan(value)
            return isNan
        return isNan
    
    def colNamesToIndex(self):
        sample_data = next(self.df.itertuples())
        i = 2 
        for colName in self.df.columns:
            if hasattr(sample_data, colName):
                self.column_names[colName] = colName
                continue
            entryName = "_" + str(i)
            self.column_names[colName] = entryName

            i = i+1

if __name__ == "__main__":
    #file = sys.stderr
    #print(file)
    File = manageFile("extract3.csv")
    table = File.makeTable("test")
    File.colNamesToIndex()
    File.parseRows(table)
