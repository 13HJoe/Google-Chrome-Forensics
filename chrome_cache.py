import os
from struct import unpack



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
            self.entry_size = Address.type_sizes(self.block_type)
            self.contiguous_block = str(int(bin(addr)[10:18], 2))
            self.file_name = 'data_' + str(int(bin(addr)[10:18], 2))
            self.block_num = int(bin(addr)[18:], 2)

        

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
            raw = unpack('I', index.read(4)[0])
            if raw != 0:

