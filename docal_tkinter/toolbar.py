# -{cd .. | python -m docal_tkinter}
from tkinter.ttk import Frame, OptionMenu, Button

class Toolbar(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        self.btn_add = Button(self, text='Add')
        self.btn_add_py = Button(self, text='Add Python')
        self.btn_add_xl = Button(self, text='Add Excel')
        self.btn_options = Button(self, text='Options')
        self.btn_preview = Button(self, text='Preview')
        self.btn_delete = Button(self, text='Delete')

        self.btn_add.pack(side='left')
        self.btn_add_py.pack(side='left')
        self.btn_add_xl.pack(side='left')
        self.btn_options.pack(side='left')
        self.btn_preview.pack(side='left')
        self.btn_delete.pack(side='left')

        self.btn_add.bind('<1>', self.master.worksheet.add)
        self.btn_delete.bind('<1>', self.master.worksheet.delete)
