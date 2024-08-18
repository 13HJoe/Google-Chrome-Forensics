import os
import json

file = os.path.expandvars("%LOCALAPPDATA%/Google/Chrome/User Data/Default/Bookmarks")
fobj =  open(file,'rb')
data = fobj.read()
data = data.decode()
data = json.loads(data)
for key in data['roots'].keys():
    if data['roots'][key]['children']:
        for obj in data['roots'][key]['children']:
            print(obj)
            print("__"*100)
        #print(data['roots'][key])
        #print("__"*100)
