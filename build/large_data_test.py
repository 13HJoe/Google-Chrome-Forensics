from chrome_history import Parse_History
from customtkinter import *
from tkinter import *
from tkinter import ttk
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

table = ttk.Treeview(master=tabview.tab("Chrome History"), columns = (1,2,3), show = 'headings')
for i,head_val in enumerate(search_data[0]):
    table.heading(i+1, text=head_val)
for row in search_data[1:]:
    try:
        table.insert('', 'end', values=row)
        print(row)
    except:
        pass
table.pack(expand=True, fill="both")

scrollbar_table = ttk.Scrollbar(master=tabview.tab("Chrome History"),
                               orient='vertical',
                               command=table.yview)
table.configure(yscrollcommand=scrollbar_table.set)
scrollbar_table.place(relx=1, 
                      rely =0,
                      relheight = 1,
                      anchor = 'ne')



app.mainloop()