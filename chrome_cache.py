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
                self.table_len = unpack('I', header.read(4))[0]
            else:
                 raise Exception("Not a valid index")

if __name__ == "__main__":
    chrome_cache_path = os.path.expandvars("%LOCALAPPDATA%/Google/Chrome/User Data/Default/Cache/Cache_Data/")

    index_path = chrome_cache_path+"index"
    index_cache_block = Block(index_path)

