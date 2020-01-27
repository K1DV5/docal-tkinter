# -{cd .. | python -m docal_tkinter}
from tkinter import Tk, Menu
from .sidebar import Sidebar
from .worksheet import Worksheet
from .menubar import Menubar
from .toolbar import Toolbar
from os import path


class App(Tk):
    def __init__(self):
        super().__init__()

        self.minsize(600, 470)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.default_filename = 'Untitled'
        self.filename = self.default_filename
        self.change_filename(self.filename)
        self.file_selected = False

        self.sidebar = Sidebar(self)
        self.worksheet = Worksheet(self)
        self.toolbar = Toolbar(self)

        self.sidebar.grid(row=0, column=0, sticky='nsw')
        self.worksheet.grid(row=0, column=1, sticky='nsew')
        self.toolbar.grid(row=0, column=2, sticky='nse')

        self.menu = Menubar(self)

        self.config(menu=self.menu)

        # set the icon
        self.after_idle(self.iconbitmap, path.abspath('./docal.ico'))
        self.protocol('WM_DELETE_WINDOW', self.menu.file_menu.exit)

    def change_filename(self, filename=None):
        if not filename:
            filename = self.default_filename
            self.file_selected = False
        else:
            self.file_selected = True
        self.filename = filename
        self.title(path.basename(filename) + ' - docal')

