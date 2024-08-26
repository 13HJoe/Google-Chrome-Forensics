import os
import sqlite3
import datetime


class Parse_History():
    def __init__(self, db=None):
        self.db = db
        if db == None:
            self.db = os.path.expandvars('%LOCALAPPDATA%/Google/Chrome/User Data/Default/History')
            
    def exec_query(self, query):
        try:
            connection = sqlite3.connect(self.db)
            cursor = connection.cursor()
            cursor.execute(query)
            data = cursor.fetchall()
            connection.close()
            return data
        except:
            return None

    def get_db_info(self):
        query = "SELECT * FROM sqlite_master WHERE type='table';"
        tables = self.exec_query(query=query)
        if tables:
            for table in tables:
                print(table,"\n","-"*60)
        
    def get_table_info(self, table_name):
        query = "SELECT sql FROM sqlite_schema WHERE name='"+table_name+"';"
        data = self.exec_query(quer=query)
        data = str(data)
        data = data.split(",")
        for line in data:
            print(line)


    def date_from_webkit(self, timestamp):
        # convert webkit_timestamp to readable format
        epoch_start = datetime.datetime(1601,1,1)
        delta = datetime.timedelta(microseconds=int(timestamp))
        return epoch_start+delta
    
    def navigation_history(self):
        query = "SELECT * FROM urls ORDER BY last_visit_time DESC;"
        table_data = self.exec_query(query=query)
        for line in table_data:
            try:
                readable_date = self.date_from_webkit(int(line[5]))
                print(line,"\n","-"*50)
            except:
                pass
    
    def download_history(self):
        query = "SELECT * FROM downloads;"
        data = self.exec_query(query=query)
        data = str(data)
        data = data.split(')')
        for line in data:
            print(line+"\n")
            print("-"*200)
            print("\n")
    
    def run_class(self):
        self.navigation_history()
        self.download_history()

    
obj = Parse_History()
query = "SELECT visits.visit_time, urls.url, urls.visit_count, urls.typed_count, urls.hidden FROM urls, visits WHERE urls.id = visits.url ORDER BY visits.visit_time DESC;"
data = obj.exec_query(query=query)
for line in data:
    print(obj.date_from_webkit(int(line[0])))
    print(line[1:])