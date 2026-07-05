import sqlite3
import sys

class LimitExceeded: 
    pass



class Schema:
    def __init__(self):
        self.columns = {}
    
    def openFile(self, fileName):
        file = pd.read_csv(fileName, chunksize=1000)
        return file
    

class sqlTable:
    def __init__(self, table_name, parent_table = None, con = sqlite3.connect("librarytest.db")):
        self.table_name = table_name
        self.parent_table = parent_table
        self.con = con
        self.cur = con.cursor()
    
    def getName(self):
        return self.table_name
    
    def getParentTable(self):
        return self.parent_table

    def addSqlColumn(self, column_name, data_type):
        #sql statement 
        return column_name
    
    def execute_query(self, *args):
        if len(args) == 1:
            query = args[0]
            self.cur.execute(query)
        if len(args) == 2:
            query = args[0]
            values = args[1]
            self.cur.execute(query, values)

    def doesColumnExist(self, table_name):
        self.cur.execute(f'''SELECT * FROM {table_name} LIMIT 0''')
        column_names = [description[0] for description in self.cur.description]
        return column_names
    
    def getSqlColName(self, colName):
        name = colName.replace(" ", "_")
        name = name.replace("(", "_")
        name = name.replace(")", "_")
        name = name.replace(".", "")
        return name
    

    def id_exists(self, table_name, record_id, primary_key_name):

        # Use standard parameterized query (?) to prevent SQL injection
        query = f"SELECT EXISTS(SELECT 1 FROM {table_name} WHERE {primary_key_name} = ?)"

        self.cur.execute(query, (record_id,))

        # fetchone() returns a tuple like (1,) if found, or (0,) if not found
        result = self.cur.fetchone()[0]

        return bool(result)
    
    # record is a dictionary, primary_exists boolean
    def createQuery(self, record, primary_exists, primary_name):
        fieldnames_query_entry = []
        questionMarks = []
        values = []
        primary_key = 0
        if primary_exists: 
            for field in record.keys():

                if field != primary_name:
                    entry = f'''{self.getSqlColName(field)}'''
                    questionMarks.append("?")
                    fieldnames_query_entry.append(entry)
                    values.append(record[field])
                else: 
                    primary_key_name = f'''{self.getSqlColName(field)}'''
                    primary_key = record[field]
            
            values.append(primary_key)
            return (fieldnames_query_entry, questionMarks, values)
        
        else:

            for field in record.keys():
                entry = f'''{self.getSqlColName(field)}'''
                questionMarks.append("?")
                fieldnames_query_entry.append(entry)
                values.append(record[field])
            
            #print(values)
            return (fieldnames_query_entry, questionMarks, values)

#updates record
    def updateRecord(self, table_name, record):
        fieldnames_query_entry = []
        questionMarks = []
        values = []
    
        #if _id exists as field in record then consider it primary key

        if "_id" in record:
        #if entry for primary exists, do this
            if self.id_exists(table_name, record["_id"], "_id"):
                queryTuple = self.createQuery(record, True, "_id")
                fieldnames_query_entry = queryTuple[0]
                questionMarks = queryTuple[1]
                values = queryTuple[2]

                for i in range(len(fieldnames_query_entry)):
                    fieldnames_query_entry[i] = fieldnames_query_entry[i] + ' = ?'

                fieldnames_string = ', '.join(fieldnames_query_entry) 

                query = f''' UPDATE {table_name} SET {fieldnames_string} WHERE _id = ?'''
            
            else: 
                queryTuple = self.createQuery(record, False, "_id")
                fieldnames_query_entry = queryTuple[0]
                questionMarks = queryTuple[1]
                values = queryTuple[2]

                valueQuestionMarks = ', '.join(questionMarks)
                fieldnames_string = ', '.join(fieldnames_query_entry)
    
                query = f'''INSERT INTO {table_name} ({fieldnames_string}) VALUES ({valueQuestionMarks})'''
        
            print(query)
            print(values)

            self.execute_query(query, values)
            
            return True

        #if _id does not exist then consider NPI primary key
        if "NPI" in record:
            #if entry for primary exists, do this
            if self.id_exists(table_name, record["NPI"], "NPI"):
                #update record
                queryTuple = self.createQuery(record, True, "NPI")
                fieldnames_query_entry = queryTuple[0]
                questionMarks = queryTuple[1]
                values = queryTuple[2]

                for i in range(len(fieldnames_query_entry)):
                    fieldnames_query_entry[i] = fieldnames_query_entry[i] + ' = ?'
    
                fieldnames_string = ', '.join(fieldnames_query_entry) 

                query = f''' UPDATE {table_name} SET {fieldnames_string} WHERE NPI = ?'''
            
            #if not do this

            else: 

                queryTuple = self.createQuery(record, False, "NPI")
                fieldnames_query_entry = queryTuple[0]
                questionMarks = queryTuple[1]
                values = queryTuple[2]

                valueQuestionMarks = ', '.join(questionMarks)
                fieldnames_string = ', '.join(fieldnames_query_entry)
    
                query = f'''INSERT INTO {table_name} ({fieldnames_string}) VALUES ({valueQuestionMarks})'''

            print(query)
            print(values)
            self.execute_query(query, values)
            
            return True

        print("Something wrong here")

        return False

    
    def commit(self):
        if self.con:
            self.con.commit()
            return True
        return False

class TableFactory:

    def __init__(self):
        self.tableList = {}
    
    def getTableList(self):
        return self.tableList
    
    def value_type(self, field_value):
        if (type(field_value)==int):
            return "INTEGER"
        if (type(field_value)==str):
            return "TEXT"
        if (isinstance(field_value, float)):
            return "FLOAT"
        if not field_value:
            field_value = "ATOMIC"
            return "TEXT"
        return "?"
    
    def getTable(self, table_name):
        table = self.tableList.get(table_name)

        if table is None:
            print(f"Warning: Table '{table_name}' not found in tableList!")
            sys.exit()
        
        return table
    
    def doesColumnExist(self, table_name, current_column):
        table = self.getTable(table_name)
        current_column = table.getSqlColName(current_column)
        column_names = table.doesColumnExist(table_name)
        if current_column not in column_names:
            #print(current_column)
            return False #return false to say that the column was not originally in the list
        return True #return true to say that column was originally in the list
    
    def make_column(self, table_name, current_column, field_value):

        table = self.getTable(table_name)

        sql_column_name = current_column.replace(" ", "_")
        sql_column_name = sql_column_name.replace("(", "_")
        sql_column_name = sql_column_name.replace(")", "_")
        sql_column_name = sql_column_name.replace(".", "")
        #column appended to table list and column created
        if not self.doesColumnExist(table_name, sql_column_name):
            print(f"TABLE {table_name}  column  {sql_column_name}")
            value_type = self.value_type(field_value)
            print(value_type)
            query = f'''ALTER TABLE {table_name} ADD COLUMN {sql_column_name} {value_type}'''
            table.execute_query(query)
    
    def make_table(self, table_name, parent_table=""):

        if parent_table:
            query = f'''CREATE TABLE IF NOT EXISTS {table_name} (_id TEXT PRIMARY KEY, NPI INTEGER NOT NULL, 
            FOREIGN KEY (NPI) REFERENCES {parent_table}(NPI))'''
        else:
            query = f'''CREATE TABLE IF NOT EXISTS {table_name} (NPI INTEGER PRIMARY KEY)'''

        table = sqlTable(table_name, parent_table)

        self.tableList[table_name] = table

        table.execute_query(query)

        return table
    
    def update_record(self, table_name, record):
        table = self.getTable(table_name)
        table.updateRecord(table_name, record)

    def commit(self, table_name):
        table = self.getTable(table_name)
        return table.commit()
    

    
    
    


