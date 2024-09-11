import os
import sqlite3
from customtkinter import *
import re
# CTkTable Widget by Akascape
# License: MIT
# Author: Akash Bora

import customtkinter
import copy

import re

def get_top_sites():
    db_top_sites = os.path.expandvars("%LOCALAPPDATA%/Google/Chrome/User Data/Default/Top Sites")

    def exec_query(query):
        try:
            connection = sqlite3.connect(db_top_sites)
            cursor = connection.cursor()
            cursor.execute(query)
            data = cursor.fetchall()
            connection.close()
            return data
        except:
            return None

    data = exec_query("SELECT * FROM top_sites ORDER BY url_rank ASC;")
    ret_data = [["URL","RANK","TITLE"]]
    for line in data:
        temp = []
        for obj in line:
            temp.append(obj)
        ret_data.append(temp)
    return ret_data

app = CTk()
app.geometry("800x500")

tabview = CTkTabview(master=app)
tabview.pack(padx=10, pady=10)

tabview.add("Top Sites")
tabview.add("Autofill Address")

ret_list = get_top_sites()

def search(val):
    print(val)
    temp = ret_list
    value=searchbox.get()
    res = []
    res.append(temp[0])
    print(value)
    pattern = re.compile(".*"+str(value)+".*")
    for row in temp[1:]:
        for word in row:
            if bool(pattern.match(str(word))):
                res.append(row)
                break
    label.configure(values=res)

print(tabview.tab("Top Sites"))
label = CTkTable(master=tabview.tab("Top Sites"), values=ret_list,header_color="#6600ff")
label.pack(anchor='s', expand=True, pady=0.5, padx=1)
searchbox = CTkEntry(master=tabview.tab("Top Sites"))
searchbtn = CTkButton(master=tabview.tab("Top Sites"), text="search",
                      command=search(10))
"""
for direct modules
note this down dumbfuck -> callback functions NO FUCKING ARGUMENTS AT ALL - DON'T BREAK SHIT 
"""
searchbox.pack(expand=True)
searchbtn.pack(expand=True)


app.resizable(width=False, height=False)
app.mainloop()