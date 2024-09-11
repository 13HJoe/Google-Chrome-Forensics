from chrome_history import Parse_History
from customtkinter import *
from tkinter import *
import re

obj = Parse_History()
search_data = obj.get_google_search_history()

rows = len(search_data)
columns = len(search_data[0])

print("[+] Obtained Data")
app = CTk()
app.title("Chrome Forensics")
app.geometry("800x400")

tabview = CTkTabview(master=app)
tabview.pack(fill=BOTH)

tabview.add("Chrome History")

i = 0
for j, col in enumerate(search_data[0]):
    text = Text(master=tabview.tab("Chrome History"),
                width=30,
                height=1,
                bg="#9BC2E6")
    text.grid(row=i, column=j)
    text.insert(INSERT, col)

for i in range(rows-1):
    for j in range(columns-1):
        text = Text(master=tabview.tab("Chrome History"),
                    width=30,
                    height=1)
        text.grid(row=i+1, column=j)
        text.insert(INSERT, search_data[i][j])


app.mainloop()