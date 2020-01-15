# -{cd .. | python -m docal_tkinter}
from tkinter import Menu, filedialog

class Menubar(Menu):
    def __init__(self, master):
        super().__init__(master, tearoff=0)

        self.add_cascade(label='File', menu=FileMenu(self))
        self.add_cascade(label='Operations', menu=OpsMenu(self))
        self.add_cascade(label='Help', menu=HelpMenu(self))

    def say(self):
        print('say hi')

class FileMenu(Menu):
    def __init__(self, master):
        # tearoff to get rid of the -- at the top
        super().__init__(master, tearoff=0)

        self.add_command(label='New', command=self.new)
        self.add_command(label='Open...', command=self.open)
        self.add_command(label='Save', command=self.save)
        self.add_command(label='Save as...', command=self.save_as)
        self.add_separator()
        self.add_command(label='Exit', command=self.exit)

        self.filetypes = [
            ('docal file', '*dcl'),
            ('Python file', '*py'),
            ('Excel worksheet', '*.xlsx'),
        ]

    def new(self):
        self.master.say()

    def open(self):
        filename = filedialog.askopenfilename(filetypes=self.filetypes)
        print(filename)

    def save(self):
        print('hi')

    def save_as(self):
        filename = filedialog.asksaveasfilename(filetypes=self.filetypes[:-1])
        print(filename)

    def exit(self):
        self.master.master.quit()

class OpsMenu(Menu):
    def __init__(self, master):
        super().__init__(master, tearoff=0)

        self.add_command(label='Select input document', command=self.select_infile)
        self.add_command(label='Clear input document', command=self.clear_infile)
        self.add_command(label='Select output document', command=self.select_outfile)
        self.add_separator()
        self.add_command(label='Send calculations', command=self.send_calcs)

    def select_infile(self):
        print('sel in')

    def clear_infile(self):
        print('clear')

    def select_outfile(self):
        print('sel out')

    def send_calcs(self):
        print('Send')

class HelpMenu(Menu):
    def __init__(self, master):
        super().__init__(master, tearoff=0)

        self.add_command(label='Help', command=self.help)
        self.add_command(label='About', command=self.about)

    def help(self):
        print('help')

    def about(self):
        print('about')
