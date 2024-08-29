import os
import json
import base64
import win32crypt
from Crypto.Cipher import AES
import sqlite3
import csv
import datetime

class Chrome_Forensics:
    def __init__(self, base_path=None):
        self.base_path = base_path
        if self.base_path == None:
            self.base_path = os.path.expandvars("%LOCALAPPDATA%/Google/Chrome/User Data/")
        self.history_db = os.path.expandvars('%LOCALAPPDATA%/Google/Chrome/User Data/Default/History')
        self.master_key = self.get_master_key()
    
    def get_db_info(self, db_path):
        query = "SELECT * FROM sqlite_master WHERE type='table';"
        tables = self.exec_query(query=query, db_path=db_path)
        if tables:
            for table in tables:
                print(table,"\n","-"*60)
        
    def get_table_info(self, table_name, db_path):
        query = "SELECT sql FROM sqlite_schema WHERE name='"+table_name+"';"
        data = self.exec_query(query=query, db_path=db_path)
        data = str(data)
        data = data.split(",")
        for line in data:
            print(line)

    def get_master_key(self):
        local_state_file_path = self.base_path+'Local State'
        file_object = open(local_state_file_path, 'rb')
        local_state_data = file_object.read()
        file_object.close()
        local_state_data = local_state_data.decode('utf-8')
        local_state_data = json.loads(local_state_data)

        os_crypt = local_state_data['os_crypt']
        key_data = os_crypt['encrypted_key']
        key_data  = base64.b64decode(key_data)

        protected_data = key_data[5:]
        # remove leading string -> b'DPAPI'
        unprotected_data = win32crypt.CryptUnprotectData(protected_data)
        # CryptUnprotectData function decrypts and does an integrity check of the data 
        # in a DATA_BLOB structure. Usually, the only user who can decrypt the data is 
        # a user with the same logon credentials as the user who encrypted the data.
        master_key = unprotected_data[1]
        # 2nd string ->  key
        return master_key

    def decrypt_data(self, buffer):
        try:
            iv = buffer[3:15]
            encrypted_data = buffer[15:]
            cipher = AES.new(self.master_key, AES.MODE_GCM, iv)
            decrypted_data = cipher.decrypt(encrypted_data)
            decrypted_data = decrypted_data[:-16]
            decrypted_data = decrypted_data.decode('utf-8')
            return decrypted_data
        except:
            return None
        
    def exec_query(self, query, db_path = None):
        if not db_path:
            db_path = self.history_db

        try:
            connection = sqlite3.connect(db_path)
            cursor = connection.cursor()
            cursor.execute(query)
            data = cursor.fetchall()
            connection.close()
            return data
        except:
            return "ERROR"
        
    def get_chrome_passwords(self):
        db_path = self.base_path + 'Default/Login Data'
        query = "SELECT action_url, origin_url, username_value, password_value FROM logins;"
        login_data = self.exec_query(query=query, db_path=db_path)

        for row in login_data:
            action_url = row[0]
            origin_url = row[1]
            url = action_url if action_url else origin_url
            username = row[2]
            encrypted_password_buffer = row[3]
            decrypted_password = self.decrypt_data(buffer=encrypted_password_buffer)
            if len(decrypted_password) != 0:
                print(url,"[+]",username,"[+]",decrypted_password)
            
    def get_chrome_cookies(self):
        db_path = self.base_path + "Default/Network/Cookies"
        query = "SELECT host_key, name, encrypted_value FROM cookies;"
        cookiedb_data = self.exec_query(query=query, db_path=db_path)

        result_data = {}
        for row in cookiedb_data:
            host_key = row[0]
            data = {
                'name' : row[1],
                'decrypted_value' : self.decrypt_data(row[2])
            }
            if host_key not in result_data:
                result_data[host_key] = []
            result_data[host_key].append(data)
        
        for host, cookies in result_data.items():
            print("-"*60)
            print(f"Host: {host}")
            for cookie in cookies:
                print()
                for key, val in cookie.items():
                    title = key.title().replace('_',' ')
                    print(f"{title}:{val}")
                print()
 
    def date_from_webkit(self, timestamp):
        # convert webkit_timestamp to readable format
        epoch_start = datetime.datetime(1601,1,1)
        delta = datetime.timedelta(microseconds=int(timestamp))
        return epoch_start + delta

    def get_navigation_history(self):
        query = "SELECT * FROM urls ORDER BY last_visit_time DESC;"
        query_oc_2 = "SELECT visits.visit_time, urls.url, urls.visit_count, urls.typed_count, urls.hidden FROM urls, visits WHERE urls.id = visits.url ORDER BY visits.visit_time DESC;"
        table_data = self.exec_query(query=query)
        for line in table_data:
            try:
                webkit_date = int(line[5])
                readable_date = self.date_from_webkit(webkit_date)
                print(line,"\n","-"*50)
            except:
                pass
    
    def get_download_history(self):
        query = "SELECT * FROM downloads;"
        table_data = self.exec_query(query=query)
        table_data = str(table_data)
        table_data = table_data.split(')')
        for line in table_data:
            print(line+"\n")
            print("-"*200)
            print("\n")

    def get_google_search_history(self):
        query = "SELECT visits.visit_time, urls.url, keyword_search_terms.term FROM urls, visits, keyword_search_terms WHERE urls.id = keyword_search_terms.url_id AND urls.id = visits.url ORDER BY visits.visit_time DESC;"
        table_data = self.exec_query(query=query)
        for line in table_data:
            try:
                readable_date = self.date_from_webkit(int(line[0]))
                print(readable_date, end="==>")
                print(line[1:])
            except:
                pass

    def get_bookmarks(self):
        return None

    def write_to_csv(self, table_name, table_data):
        table_name = table_name + ".csv"
        with open(table_name, 'w', newline='') as csv_obj:
            csv_writer = csv.write(csv_obj, delimiter=',')
            for line in table_data:
                try:
                    csv_writer.writerow(line)
                except:
                    pass
        return None
    
    def run_class(self):
        self.get_chrome_passwords()
        self.get_chrome_cookies()
        self.get_download_history()
        self.get_navigation_history()
        self.get_google_search_history()


enc_data_obj = Chrome_Forensics()
enc_data_obj.run_class()