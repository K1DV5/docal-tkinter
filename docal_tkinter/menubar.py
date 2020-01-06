from tkinter.ttk import Frame, Label

class Menubar(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.label = Label(self, text='hello')
        self.label.pack()
