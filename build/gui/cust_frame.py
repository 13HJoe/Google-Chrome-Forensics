from customtkinter import *

app = CTk()
app.geometry("600x500")

"""
FRAME
frame1 = CTkScrollableFrame(master=app,
                 fg_color="#8D6F3A",
                 border_color="#FFCC70",
                 border_width=2,
                 orientation="vertical")
frame1.pack(expand=True)

label = CTkLabel(master=frame1, text="Frame1")
entry = CTkEntry(master=frame1, placeholder_text="input.....")
btn = CTkButton(master=frame1, text="Submit")

label.pack(anchor='s', expand=True, pady=10, padx=30)
entry.pack(anchor='s', expand=True, pady=10, padx=30)
btn.pack(anchor='n', expand=True, pady=30, padx=20)
"""

# TABS
tabview = CTkTabview(master=app)
tabview.pack(padx=20,pady=20)

tabview.add("Tab 1")
tabview.add("Tab 2")
tabview.add("Tab 3")

label = CTkLabel(master=tabview.tab("Tab 1"), text="Frame1")
entry = CTkEntry(master=tabview.tab("Tab 2"), placeholder_text="input.....")
btn = CTkButton(master=tabview.tab("Tab 3"), text="Submit")

label.pack(anchor='s', expand=True, pady=10, padx=30)
entry.pack(anchor='s', expand=True, pady=10, padx=30)
btn.pack(anchor='n', expand=True, pady=30, padx=20)



app.mainloop()
