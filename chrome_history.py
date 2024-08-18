import os
import sqlite3

db = os.path.expandvars('%LOCALAPPDATA%/Google/Chrome/User Data/Default/History')
connection = sqlite3.connect(db)
cursor = connection.cursor()
"""
cursor.execute("SELECT * FROM sqlite_master WHERE type='table';")
for table in cursor.fetchall():
    print(table)
"""
cursor.execute("SELECT * FROM urls;")
for line in cursor.fetchall():
    print(line)
connection.close()