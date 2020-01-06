from tkinter import Tk, Label
from .app import App

master = Tk()
master.minsize(900, 600)

app = App(master)

master.mainloop()
