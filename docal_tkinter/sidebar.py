# -{cd .. | python -m docal_tkinter}
from tkinter.ttk import Frame, Label, Entry, Button, Labelframe, OptionMenu, Label
from tkinter import filedialog, StringVar

class Sidebar(Frame):
    def __init__(self, master):
        super().__init__(master, borderwidth='.25cm')
        # data (for master)
        self.infile = self.outfile = None

        # infile area
        self.infile_area = InfileArea(self)
        self.infile_area.grid(row=0, column=0, sticky='ew')
        self.grid_rowconfigure(0, pad=15)

        # outfile area
        self.outfile_area = OutfileArea(self)
        self.outfile_area.grid(row=1, column=0, sticky='ew')
        self.grid_rowconfigure(1, pad=15)

        log_frame = Frame(self, borderwidth='.25cm')
        log_frame.grid(row=2, column=0, sticky='ew')
        log_frame.grid_columnconfigure(1, weight=1)

        log_label = Label(log_frame, text='Log level:')
        log_label.grid(row=0, column=0, sticky='w')

        log_levels = ('Info', 'Warning', 'Error', 'Debug')
        self.log_var = StringVar(self)
        self.log_var.set(log_levels[1])
        self.log_level = OptionMenu(log_frame, self.log_var, *log_levels)
        self.log_level.grid(row=0, column=1, sticky='ew')

        self.send_btn = Button(self, text='Send')
        self.send_btn.grid(row=3, column=0, sticky='ew')
        self.grid_rowconfigure(3, pad=20)

def set_entry_text(entry, text):
    entry.delete(0, 'end')
    entry.insert(0, text)
    entry.xview_moveto(10)

class InfileArea(Labelframe):
    def __init__(self, master):
        super().__init__(master, text='Input document', borderwidth='.25cm')

        self.infile = None

        self.entry = Entry(self, width=30)
        self.select_btn = Button(self, text='Select...')
        self.clear_btn = Button(self, text='Clear', width=6)
        self.open_btn = Button(self, text='Open', width=6)
        self.entry.grid(row=0, column=0, columnspan=5, sticky='nsew')
        self.select_btn.grid(row=1, column=0, columnspan=3, sticky='ew')
        self.clear_btn.grid(row=1, column=3, sticky='ew')
        self.open_btn.grid(row=1, column=4, sticky='ew')

        self.select_btn.bind('<1>', self.select_infile)

    def select_infile(self, event):
        filename = filedialog.askopenfilename(filetypes=[('Word documents', '*.docx'), ('LaTeX documents', '*.tex')])
        if filename:
            set_entry_text(self.entry, filename)
            self.infile = filename

class OutfileArea(Labelframe):
    def __init__(self, master):
        super().__init__(master, text='Output document', borderwidth='.25cm')

        self.outfile = None

        self.entry = Entry(self, width=30)
        self.select_btn = Button(self, text='Select...')
        self.open_btn = Button(self, text='Open')
        self.entry.grid(row=0, column=0, columnspan=5, sticky='nsew')
        self.select_btn.grid(row=1, column=0, columnspan=3, sticky='ew')
        self.open_btn.grid(row=1, column=3, columnspan=2, sticky='ew')

        # binding
        self.select_btn.bind('<1>', self.select_outfile)

    def select_outfile(self, event):
        filename = filedialog.asksaveasfilename(filetypes=[('Word documents', '*.docx'), ('LaTeX documents', '*.tex')])
        if filename:
            set_entry_text(self.entry, filename)
            self.outfile = filename


