# -{cd .. | python -m docal_tkinter}
from tkinter import Tk, Menu
from tkinter.ttk import Menubutton
from .app import App
from .menubar import Menubar

master = Tk()
master.minsize(900, 600)

app = App(master)
app.grid(row=0, column=0, sticky='nsew')

master.config(menu=Menubar(master))

master.mainloop()
