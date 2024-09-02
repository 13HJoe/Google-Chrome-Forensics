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
            print(object['name'])
            recurse_children(object['children'])
        else:
            data = ('date_added -> ' + str(date_from_webkit(object['date_added']))
                    +' | date_last_used -> ' + str(date_from_webkit(object['date_added']))
                    +' | name -> '+ object['name']
                    +' | url -> '+ object['url'])
            print(data)
    print()
    return None


file = os.path.expandvars("%LOCALAPPDATA%/Google/Chrome/User Data/Default/Bookmarks")
fobj =  open(file,'rb')
data = fobj.read()
data = data.decode()
data = json.loads(data)
for key in data['roots'].keys():
    bookmark_type = data['roots'][key]['name']
    date_added = data['roots'][key]['date_added']
    print(bookmark_type," ",date_from_webkit(date_added),"\n")
    #print(data['roots'][key],'\n\n\n')
    if len(data['roots'][key]['children']) == 0:
        print('No Bookmarks')
        continue
    recurse_children(data['roots'][key]['children'])
