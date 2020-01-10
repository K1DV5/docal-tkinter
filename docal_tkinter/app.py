# -{cd .. | python -m docal_tkinter}
from tkinter import Tk, Menu
from .sidebar import Sidebar
from .worksheet import Worksheet
from .menubar import Menubar


class App(Tk):
    def __init__(self):
        super().__init__()

        self.config(menu=Menubar(self))

        self.minsize(900, 500)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = Sidebar(self)
        self.worksheet = Worksheet(self)

        self.sidebar.grid(row=0, column=0, rowspan=2, sticky='nsw')
        self.worksheet.grid(row=1, column=1, sticky='nsew')
