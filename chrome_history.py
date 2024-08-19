import os
import sqlite3
import datetime

db = os.path.expandvars('%LOCALAPPDATA%/Google/Chrome/User Data/Default/History')
connection = sqlite3.connect(db)
cursor = connection.cursor()

def get_tables():
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


def visited_links_ordered_by_count():
    q = "SELECT * FROM sqlite_schema WHERE name='visited_links';"
    cursor.execute(q)
    print(cursor.fetchall())
    q = "SELECT * FROM visited_links ORDER BY visit_count DESC;"
    cursor.execute(q)
    for line in cursor.fetchall():
        try:
            print(line)
        except:
            continue

connection.close()