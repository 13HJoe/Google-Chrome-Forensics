import os
from struct import unpack
import datetime
import copy
import re



class Block():
    INDEX_MAGIC = 0xC103CAC3
    BLOCK_MAGIC = 0xc104cac3
    INDEX = 0
    BLOCK = 1

    def __init__(self, filename):
        with open(filename,'rb') as header:
            m = unpack('I',header.read(4))[0]
            # unpack("unsigned integer")
            if m == Block.BLOCK_MAGIC:
                header.seek(2,1)
                self.block_type = Block.BLOCK
                self.version = unpack('h', header.read(2))[0] # unpack('short')
                self.this_file = unpack('h', header.read(2))[0]
                # Index of this file
                self.next_file = unpack('h', header.read(2))[0]
                # Next file when this one is full
                self.entry_size = unpack('I',header.read(4))[0] 
                self.num_entries = unpack('I',header.read(4))[0]
                self.max_entries = unpack('I', header.read(4))[0]
                self.empty = [unpack('I',header.read(4))[0] for _ in range(4)]
                self.hints = [unpack('I',header.read(4))[0] for _ in range(4)]
            elif m == Block.INDEX_MAGIC:
                header.seek(2,1)
                self.block_type = Block.INDEX
                self.version = unpack('h', header.read(2))[0]
                self.num_entries = unpack('I', header.read(4))[0]
                self.num_bytes = unpack('I', header.read(4))[0]
                self.last_file = 'f_{:06x}'.format(unpack('I',header.read(4))[0])
                header.seek(8, 1)
                self.table_len = unpack('I', header.read(4))[0] # size of entry table
            else:
                 raise Exception("Not a valid index")

class Address():
    SEPERATE_FILE = 0
    RANKING_BLOCK = 1
    BLOCK_256 = 2
    BLOCK_1024 = 3
    BLOCK_4096 = 4

    type_sizes = [0, 36, 256, 1024, 4096]

    def __init__(self, addr, path):
        if addr == 0:
            raise Exception("Null Pointer")
        
        self.addr = addr
        self.path = path

        self.block_type = int(bin(addr)[3:6], 2)

        if self.block_type == Address.SEPERATE_FILE:
            self.file_name = 'f_{:06x}'.format(int(bin(addr)[6:], 2))
        elif self.block_type == Address.RANKING_BLOCK:
            self.file_name = 'data_'+str(int(bin(addr)[10:18],2))
        else:
            self.entry_size = Address.type_sizes[self.block_type]
            self.contiguous_block = str(int(bin(addr)[10:18], 2))
            self.file_name = 'data_' + str(int(bin(addr)[10:18], 2))
            self.block_num = int(bin(addr)[18:], 2)

class Data():
    HTTP_HEADER = 0
    OTHER = 1

    def __init__(self, address, size, ishttpheader=False):
        self.size = size
        self.address = address
        self.data_type = Data.OTHER

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
                data_copy = data_copy[:end.end() - 2]

            self.data_type = Data.HTTP_HEADER
            self.headers = {}
            for line in data.copy.split(b'\x00')[1:]:
                strip = line.split(b':')
                v = b':'.join(strip[1:])
                v = v.decode(encoding='utf-8')
                k = strip[0].decode(encoding='utf-8').lower()
                self.headers[k] = v

class Entry():
    def __init__(self, address):
        with open(os.path.join(address.path, address.file_name), 'rb') as block:
            block.seek(8192 + address.block_num * address.entry_size)

            self.hash = unpack("I",block.read(4))[0] # full hash of the key
            self.next = unpack("I", block.read(4))[0] # next entry with the same hash
            self.rankings_node = unpack("I",block.read(4))[0]
            self.reuse_count = unpack("I",block.read(4))[0]
            self.refetch_count = unpack("I", block.read(4))[0]
            self.state = unpack("I",block.read(4))[0]
            self.creationTime = datetime.datetime(1601,1,1) + datetime.timedelta(microseconds=unpack('Q', block.read(8))[0])
            self.key_len = unpack('I',block.read(4))[0]
            self.long_key = unpack('I',block.read(4))[0]
            self.data_size = [unpack('I',block.read(4))[0] for _ in range(4)]
            self.data = []

            for i in range(4):
                a = unpack('I', block.read(4))[0]
                try:
                    addr = Address(a, address.path)
                    self.data.append(Data(addr, self.data_size[i], True))
                except:
                    pass
            
            self.httpHeader = None
            for data in self.data:
                if data.data_type == Data.HTTP_HEADER:
                    self.httpHeader = data
                    break
            
            self.flags = unpack('I', block.read(4))[0]

            block.seek(5*4, 1)

            if self.long_key == 0:
                self.key = block.read(self.key_len).decode('ascii')
            else:
                self.key = Data(Address(self.long_key, address.path), self.key_len, True)

if __name__ == "__main__":
    chrome_cache_path = os.path.expandvars("%LOCALAPPDATA%/Google/Chrome/User Data/Default/Cache/Cache_Data/")

    index_path = os.path.join(chrome_cache_path,"index")
    index_cache_block = Block(index_path)
    
    if index_cache_block.block_type != Block.INDEX:
        raise Exception("Not a valid index")
    
    with open(index_path, 'rb') as index:
        index.seek(92*4) # skip the metadata section
        cache = []
        for key in range(index_cache_block.table_len): # for size of entry table
            raw = unpack('I', index.read(4))[0]
            if raw != 0:
                entry = Entry(Address(raw, chrome_cache_path))
                cache.append(entry)
                while entry.next != 0:
                    entry = Entry(Address(entry.next, chrome_cache_path))
                    cache.append(entry)
    
    for entry in cache:
        print(entry)