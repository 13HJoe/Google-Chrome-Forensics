import sqlite3
import os
from base64 import b64decode
from win32.win32crypt import CryptUnprotectData
from Cryptodome.Cipher.AES import new, MODE_GCM
from Crypto.Cipher import AES
import json
import codecs
import base64

def decrypt(v, key):
    iv = v[3:15]
    payload = v[15:]
    cipher = new(key, AES.MODE_GCM, iv)
    value = cipher.decrypt(payload)
    print("value->",value)
    return value



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








db = os.path.expandvars('%LOCALAPPDATA%/Google/Chrome/User Data/Default/Network/Cookies')

f_obj = open(db+'/../../../Local State', 'rb')
data = f_obj.read()
f_obj.close()
data = data.decode('utf-8')
# Deserialize s (a str, bytes or bytearray instance containing a JSON document) 
# to a Python object using this conversion table.
data = json.loads(data)
key = get_chrome_cookies_master_key(data)

def try_encodings(byte_text: bytes):

    encodings = ['ascii', 'big5', 'big5hkscs', 'cp037', 'cp273', 'cp424', 'cp437', 'cp500', 'cp720', 'cp737', 'cp775', 'cp850', 'cp852', 'cp855', 'cp856', 'cp857', 'cp858', 'cp860', 'cp861', 'cp862', 'cp863', 'cp864', 'cp865', 'cp866', 'cp869', 'cp874', 'cp875', 'cp932', 'cp949', 'cp950', 'cp1006', 'cp1026', 'cp1125', 'cp1140', 'cp1250', 'cp1251', 'cp1252', 'cp1253', 'cp1254', 'cp1255', 'cp1256', 'cp1257', 'cp1258', 'euc_jp', 'euc_jis_2004', 'euc_jisx0213', 'euc_kr', 'gb2312', 'gbk', 'gb18030', 'hz', 'iso2022_jp', 'iso2022_jp_1', 'iso2022_jp_2', 'iso2022_jp_2004', 'iso2022_jp_3', 'iso2022_jp_ext', 'iso2022_kr', 'latin_1', 'iso8859_2', 'iso8859_3', 'iso8859_4', 'iso8859_5', 'iso8859_6', 'iso8859_7', 'iso8859_8', 'iso8859_9', 'iso8859_10', 'iso8859_11', 'iso8859_13', 'iso8859_14', 'iso8859_15', 'iso8859_16', 'johab', 'koi8_r', 'koi8_t', 'koi8_u', 'kz1048', 'mac_cyrillic', 'mac_greek', 'mac_iceland', 'mac_latin2', 'mac_roman', 'mac_turkish', 'ptcp154', 'shift_jis', 'shift_jis_2004', 'shift_jisx0213', 'utf_32', 'utf_32_be', 'utf_32_le', 'utf_16', 'utf_16_be', 'utf_16_le', 'utf_7', 'utf_8', 'utf_8_sig']


    for encoding in encodings:
        try:
            print(f'Encoding {encoding}')
            print(decrypt(byte_text.decode(encoding), key))
        except:
            pass




conn = sqlite3.connect(db)

cursor = conn.cursor()
conn.text_factory = lambda b: b.decode(errors='ignore')
cursor.execute('SELECT name, encrypted_value FROM cookies;')

col_ix = 0
res = []
row = cursor.fetchone()
print(row[0])
print(row[1])
val = decrypt(row[1].encode('utf-8'), key)
print(val.decode('utf-8'))