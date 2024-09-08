import os
import sqlite3
import re


db = os.path.expandvars('%LOCALAPPDATA%/Google/Chrome/User Data/Default/History')
connection = sqlite3.connect(db)
cursor = connection.cursor()
cursor.execute("select sql from sqlite_schema where name = 'downloads';")
data = cursor.fetchall()
data = str(data)
data = data.split(",")
for line in data:
    print(line)

with open("../test/chrome_download_history.txt",'w') as fobj:
    cursor.execute("SELECT * FROM downloads;")
    for line in cursor.fetchall():
        fobj.write(str(line))
        fobj.write("\n")

connection.close()