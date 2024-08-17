import os
import base64
import asn1
import json

def get_firefox_pass():
    login_data = None
    key_data = None

    app_data = os.getenv('APPDATA')
    profile_dir = os.path.join(app_data,"Mozilla","Firefox","Profiles")
    profile = os.listdir(profile_dir)[0]
    login_data_path = os.path.join(profile_dir, profile, "logins.json")
    key_data_path = os.path.join(profile_dir, profile, "key4.db")


    fobj = open(login_data_path,'rb')
    decoder = asn1.Decoder()
    data = fobj.read().decode()
    data = json.loads(data)
    data = [line for line in data["logins"]]
    for x in data:
        print(x)
        '''
        print(x["hostname"])
        print(x["encryptedUsername"])
        print(x["encryptedPassword"])
        '''
    exit(0)
    log = (base64.b64decode(fobj.read()))
    decoder.start(log)
    tag, value = decoder.read()
    print(tag,"\n",value)

get_firefox_pass()