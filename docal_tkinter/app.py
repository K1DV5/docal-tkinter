from tkinter.ttk import Frame
from tkinter import font
from .sidebar import Sidebar
from .worksheet import Worksheet
from .menubar import Menubar


class App(Frame):
    def __init__(self, master):
        FONT = font.Font(master, family='consolas', size=16)
        super().__init__(master)
        self.sidebar = Sidebar(master)
        self.sidebar.grid(row=0, column=0)
        self.menubar = Menubar(master)
        self.menubar.grid(row=0, column=1)
        self.worksheet = Worksheet(master, FONT)
        self.worksheet.grid(row=1, column=1)

