# -{cd .. | python -m docal_tkinter}
from tkinter import Tk, Menu
from .sidebar import Sidebar
from .worksheet import Worksheet
from .menubar import Menubar
from .toolbar import Toolbar


class App(Tk):
    def __init__(self):
        super().__init__()

        self.config(menu=Menubar(self))

        self.minsize(400, 300)
        self.geometry('800x500')

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = Sidebar(self)
        self.worksheet = Worksheet(self)
        self.toolbar = Toolbar(self)

        self.sidebar.grid(row=0, column=0, sticky='nsw')
        self.worksheet.grid(row=0, column=1, sticky='nsew')
        self.toolbar.grid(row=0, column=2, sticky='nse')
