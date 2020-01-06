from tkinter.ttk import Frame, Label

class Worksheet(Frame):
    def __init__(self, master, font):
        super().__init__(master)
        self.label = Label(self, text='hi', font=font)
        self.label.pack()
