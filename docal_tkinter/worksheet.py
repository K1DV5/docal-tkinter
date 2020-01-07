from tkinter.ttk import Frame, Label
from tkinter import font


class Worksheet(Frame):
    def __init__(self, master):
        super().__init__(master)
        math_font = font.Font(self, family='consolas', size=16)
        self.label = Label(self, text='hi', font=math_font)
        self.label.pack()
