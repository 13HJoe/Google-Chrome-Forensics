import os
import base64
import asn1
import json
import sqlite3
from binascii import hexlify

def get_firefox_pass():
    login_data = None
    key_data = None

    app_data = os.getenv('APPDATA')
    profile_dir = os.path.join(app_data,"Mozilla","Firefox","Profiles")
    profile = os.listdir(profile_dir)[0]
    login_data_path = os.path.join(profile_dir, profile, "logins.json")
    key_data_path = os.path.join(profile_dir, profile, "key4.db")



    connection = sqlite3.connect(key_data_path)
    cursor = connection.cursor()
    data_row = None
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print(cursor.fetchall())
    cursor.execute("SELECT * FROM nssPrivate;")
    print(cursor.fetchall())
    cursor.execute("SELECT * FROM metaData")
    for record in cursor.fetchall():
        for sub_record in record:
            print(sub_record)
        
#---------------------------------------------------------------------------------#
"""
    fobj = open(login_data_path,'rb')
    decoder = asn1.Decoder()
    data = fobj.read().decode()
    fobj.close()
    data = json.loads(data)
    data = [line for line in data["logins"]]
    for x in data:
        d = base64.b64decode(x["encryptedUsername"])
        decoder.start(d)
        tag, value = decoder.read()
        print(value)
        
    log = (base64.b64decode(fobj.read()))
    decoder.start(log)
    tag, value = decoder.read()
    print(tag,"\n",value)
    """

get_firefox_pass()