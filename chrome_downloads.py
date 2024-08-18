import os
import sqlite3


db = os.path.expandvars('%LOCALAPPDATA%/Google/Chrome/User Data/Default/HIstory')
connection = sqlite3.connect(db)
cursor = connection.cursor()
cursor.execute("select sql from sqlite_schema where name = 'downloads';")
data = cursor.fetchall()
data = str(data)
data = data.split(",")
for line in data:
    print(line)

with open("test/chrome_download_history.txt",'w') as fobj:
    cursor.execute("SELECT * FROM downloads;")
    data = cursor.fetchall()
    data = str(data)
    data = data.split(')')
    for line in data:
        fobj.write(line+"\n")
        fobj.write("-"*200)
        fobj.write("\n")