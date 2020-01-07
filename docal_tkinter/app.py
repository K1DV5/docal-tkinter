# -{cd .. | python -m docal_tkinter}
from tkinter.ttk import Frame
from .sidebar import Sidebar
from .worksheet import Worksheet
from .toolbar import Toolbar


class App(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.sidebar = Sidebar(master)
        self.sidebar.grid(row=0, column=0, rowspan=2)
        self.menubar = Toolbar(master)
        self.menubar.grid(row=0, column=1, sticky='ew')
        self.worksheet = Worksheet(master)
        self.worksheet.grid(row=1, column=1, sticky='nsew')

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)
