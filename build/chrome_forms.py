import os
import json
import sqlite3
import base64
import win32crypt
from Crypto.Cipher import AES

db_top_sites = os.path.expandvars("%LOCALAPPDATA%/Google/Chrome/User Data/Default/Top Sites")

db = db_top_sites
# db = os.path.expandvars("%LOCALAPPDATA%/Google/Chrome/User Data/Default/Web Data")
        
def exec_query(query):
    try:
        connection = sqlite3.connect(db)
        cursor = connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        connection.close()
        return data
    except:
        return None

query = "SELECT * FROM sqlite_master WHERE type = 'table'; "
data = exec_query(query=query)
for line in data:
    table_name = line[1]
    subquery = "SELECT * FROM "+table_name
    print(line)
    table_data = exec_query(query=subquery)
    if table_data:
        for line in table_data:
            print(line)
    
    print("-"*50)





