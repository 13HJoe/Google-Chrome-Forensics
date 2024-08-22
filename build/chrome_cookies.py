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
                return value.decode()
            except:
                return None

        connection.create_function('decrypt',1,decrypt)
        #result = connection.execute("SELECT * from sqlite_master where type='table'")
        cursor = connection.cursor()
        c = 0

        result_data = {}
        for row in cursor.execute("SELECT host_key, name, encrypted_value FROM cookies"):
            host_key = row[0]
            data = {
                'name' : row[1],
                'decrypted_value': decrypt(row[2])
            }
            if host_key not in result_data:
                result_data[host_key] = []
            result_data[host_key].append(data)
        
        print(len(result_data))
        result_data = result_data
        c = 0
        for host, cookies in result_data.items():
            print("-"*60)
            print(f"Host: {host}")
            for cookies in cookies:
                print()
                for key, val in cookies.items():
                    title = key.title().replace('_',' ')
                    print(f"{title}:{val}")
                print()
        connection.close()



get_chrome_cookies()