import sqlite3


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
    
    def updateRecord(self, table_name, record):
        fieldnames_query_entry = []
        questionMarks = []
        values = []

        for field in record.keys():

            entry = f'''{self.getSqlColName(field)}'''
            questionMarks.append("?")
            fieldnames_query_entry.append(entry)
            values.append(record[field])

        valueQuestionMarks = ', '.join(questionMarks)
        fieldnames_string = ', '.join(fieldnames_query_entry)
    
        query = f'''INSERT INTO {table_name} ({fieldnames_string}) VALUES ({valueQuestionMarks})'''
        
        print(query)

        self.execute_query(query, values)
    
    def commit(self):
        if self.con:
            self.con.commit()
            return True
        return False

class TableFactory:
    
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
    
    def doesColumnExist(self, table, current_column):
        table_name = table.getName()
        current_column = table.getSqlColName(current_column)
        column_names = table.doesColumnExist(table_name)
        if current_column not in column_names:
            print(current_column)
            return False #return false to say that the column was not originally in the list
        return True #return true to say that column was originally in the list
    
    def make_column(self, table, current_column, field_value):
        #table = self.get_table(path)
        table_name = table.getName()
        sql_column_name = current_column.replace(" ", "_")
        sql_column_name = sql_column_name.replace("(", "_")
        sql_column_name = sql_column_name.replace(")", "_")
        sql_column_name = sql_column_name.replace(".", "")
        #column appended to table list and column created
        if not self.doesColumnExist(table, sql_column_name):
            print(f"TABLE {table_name}  column  {sql_column_name}")
            value_type = self.value_type(field_value)
            query = f'''ALTER TABLE {table_name} ADD COLUMN {sql_column_name} {value_type}'''
            table.execute_query(query)
    
    def make_table(self, table_name, parent_table=None):
        if parent_table:
            query = f'''CREATE TABLE IF NOT EXISTS {table_name} (_id INTEGER PRIMARY KEY AUTOINCREMENT, parent_id INTEGER NOT NULL, 
            FOREIGN KEY (parent_id) REFERENCES {parent_table.name()}(_id))'''
        else:
            query = f'''CREATE TABLE IF NOT EXISTS {table_name} (_id INTEGER PRIMARY KEY AUTOINCREMENT)'''

        table = sqlTable(table_name, parent_table)
        table.execute_query(query)

        return table
    
    def update_record(self, table, record):
        table.updateRecord(table.getName(), record)

    def commit(self, table):
        return table.commit()
    

    
    
    


