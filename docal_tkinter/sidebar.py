from tkinter.ttk import Frame, Label

class Sidebar(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(width=200)
        self.label = Label(self, text='in frame')
        self.label.pack()

