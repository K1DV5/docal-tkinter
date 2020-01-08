# -{cd .. | python -m docal_tkinter}
from tkinter import Tk, Menu
from tkinter.ttk import Menubutton
from .app import App
from .menubar import Menubar

master = Tk()
master.minsize(900, 500)

# app
app = App(master)
app.grid(row=0, column=0, sticky='nsew')

# make stretchable
master.grid_columnconfigure(0, weight=1)
master.grid_rowconfigure(0, weight=1)

# menubar
master.config(menu=Menubar(master))

master.mainloop()
