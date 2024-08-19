import os
import sqlite3
import datetime

def get_tables():
    db = os.path.expandvars('%LOCALAPPDATA%/Google/Chrome/User Data/Default/History')
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM sqlite_master WHERE type='table';")
    for table in cursor.fetchall():
        try:
            print(table)
        except:
            continue
    connection.close()

def date_from_webkit(timestamp):
    epoch_start = datetime.datetime(1601,1,1)
    delta = datetime.timedelta(microseconds=int(timestamp))
    print(epoch_start+delta)

def ordered_url_history():
    q = "SELECT * FROM urls ORDER BY last_visit_time DESC;"
    db = os.path.expandvars('%LOCALAPPDATA%/Google/Chrome/User Data/Default/History')
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    cursor.execute("SELECT sql from sqlite_schema where name='urls';")
    print(cursor.fetchall())
    cursor.execute(q)
    data =  cursor.fetchall()
    for line in data:
        try:
            date_from_webkit(int(line[5]))
            print(line,"\n","--"*50)
        except:
            continue

    connection.close()

get_tables()