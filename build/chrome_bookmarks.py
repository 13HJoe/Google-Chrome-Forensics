import os
import json
import datetime


def date_from_webkit(timestamp):
    # convert webkit_timestamp to readable format
    epoch_start = datetime.datetime(1601,1,1)
    delta = datetime.timedelta(microseconds=int(timestamp))
    return epoch_start + delta

def recurse_children(child):
    for object in child:
        if 'children' in object.keys():
            recurse_children(object['children'])
        else:
            print(object)
    return None


file = os.path.expandvars("%LOCALAPPDATA%/Google/Chrome/User Data/Default/Bookmarks")
fobj =  open(file,'rb')
data = fobj.read()
data = data.decode()
data = json.loads(data)
for key in data['roots'].keys():
    bookmark_type = data['roots'][key]['name']
    date_added = data['roots'][key]['date_added']
    print(bookmark_type," ",date_from_webkit(date_added))
    #print(data['roots'][key],'\n\n\n')
    recurse_children(data['roots'][key]['children'])
