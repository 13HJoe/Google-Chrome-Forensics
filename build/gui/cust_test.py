"""from customtkinter import *
from PIL import Image


app = CTk()
app.geometry("800x600")
set_appearance_mode("dark")



# to display text
label = CTkLabel(master=app, text="Chrome Forensics",font=("Arial", 20), text_color="#6699ff")
label.place(relx=0.15,
            rely=0.1,
            anchor="center")


#check box
checkbox = CTkCheckBox(master=app,
                       text="Option",
                       fg_color="#C850C0",
                       checkbox_height=30,
                       checkbox_width=30,
                       corner_radius=36)
checkbox.place(relx=0.1,
               rely=0.9,
               anchor="center")

#slider
slider = CTkSlider(master=app,
                   from_=0, to=50,
                   number_of_steps=6,
                   button_color="#ffffff",
                   progress_color="#ffffff",
                   orientation="horizontal",
                   button_hover_color="#6699ff")
slider.place(relx=0.2,
            rely=0.8,
            anchor="center")

#text_input
text_input = CTkEntry(master=app,
                      placeholder_text="Start typing..",
                      width=300,
                      text_color="#FFCC70")
text_input.place(relx=0.5,
                 rely=0.5,
                 anchor="center")

#event handling
#button click
count = 0
def click_handler():
    global count 
    count += 1
    btn.configure(text=f"Save To CSV {count}")
    
btn = CTkButton(master=app, text="Save To CSV", command=click_handler,
                corner_radius=5, fg_color="transparent", border_color="#ffffff",border_width=3)
btn.place(relx=0.80,
          rely=0.90,
          anchor="nw")

#combobox - event
def combo_event(value):
    print(value)

#dropdown menu
combobox = CTkComboBox(master=app,
                       values=["saved login data","cookies","credit card data"],
                       command=combo_event,
                       fg_color="#0093E9",
                       border_color="#ffffff",
                       dropdown_fg_color="#0093E9")
combobox.place(relx=0.9,
               rely=0.1,
               anchor="center")

#get text input - EVENT
#textbox
def get_textbox_input():
    print(textbox.get('0.0','end'))
    
textbox = CTkTextbox(master=app,
                     scrollbar_button_color="#ffffff",
                     corner_radius=10,
                     border_color="#FFCC70",
                     border_width=2)
text_button = CTkButton(master=app, text="Submit",command=get_textbox_input)
textbox.place(relx=0.15,
                 rely=0.6,
                 anchor="center")
text_button.place(relx=0.45,
                  rely=0.6,
                  anchor="center")





app.resizable(width=False, height=False)
app.mainloop()
"""
class A:
    def __init__(self):
        self.a = "Class A"

class B(A):
    def __init(self):
        super().__init__()
        self.b = "Class B"

obj = B()
 