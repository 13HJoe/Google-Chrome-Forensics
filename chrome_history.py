import os
import sqlite3
import datetime


class Parse_History():
    def __init__(self, db=None):
        self.db = db
        if db == None:
            self.db = os.path.expandvars('%LOCALAPPDATA%/Google/Chrome/User Data/Default/History')
            
    def exec_query(self, query):
        connection = sqlite3.connect(self.db)
        cursor = connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        connection.close()
        return data

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

parse_obj = Parse_History()
parse_obj.run_class()

    
