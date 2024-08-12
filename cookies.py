import sqlite3
import json
from base64 import b64decode
from win32.win32crypt import CryptUnprotectData
from Cryptodome.Cipher.AES import new, MODE_GCM
from Crypto.Cipher import AES

def get_key(data):
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


def get_chrome(db=None):
    if db is None:
        from os.path import expandvars
        # Return the argument with environment variables expanded
        db = expandvars('%LOCALAPPDATA%/Google/Chrome/User Data/Default/Network/Cookies')
        f_obj = open(db+'/../../../Local State', 'rb')
        data = f_obj.read()
        data = data.decode('utf-8')
        # Deserialize s (a str, bytes or bytearray instance containing a JSON document) 
        # to a Python object using this conversion table.
        data = json.loads(data)
        key = get_key(data)

        connection = sqlite3.connect(db)
        # create user-defined SQL function
        # create_function(name_of_new_func, no_of_args, callback_func)
        def decrypt(v):
            iv = v[3:15]
            payload = v[15:]
            cipher = new(key, AES.MODE_GCM, iv)
            value = cipher.decrypt(payload)[:-16]
            return value.decode()

        connection.create_function('decrypt',1,decrypt)
        #result = connection.execute("SELECT * from sqlite_master where type='table'")
        cursor = connection.cursor()
        c = 0
        for row in cursor.execute("SELECT name, encrypted_value FROM cookies"):
            #print(row)
            print(decrypt(row[1]))
            break
        connection.close()


        
get_chrome()