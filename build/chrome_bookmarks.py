import os
import json
import datetime


def date_from_webkit(timestamp):
    # convert webkit_timestamp to readable format
    epoch_start = datetime.datetime(1601,1,1)
    delta = datetime.timedelta(microseconds=int(timestamp))
    return epoch_start + delta

def recurse_bookmarks(data):
    for obj in data:
        if obj['children']:
            recurse_bookmarks()


file = os.path.expandvars("%LOCALAPPDATA%/Google/Chrome/User Data/Default/Bookmarks")
fobj =  open(file,'rb')
data = fobj.read()
data = data.decode()
data = json.loads(data)
for key in data['roots'].keys():
    if data['roots'][key]['children']:
        recurse_bookmarks(data['roots'][key]['children'])
        for obj in data['roots'][key]['children']:
            print(obj)
            print("__"*100)
        #print(data['roots'][key])
        #print("__"*100)
