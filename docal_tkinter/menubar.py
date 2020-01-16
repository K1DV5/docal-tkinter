# -{cd .. | python -m docal_tkinter}
from tkinter import Menu, filedialog, messagebox
from json import dump, load

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

        self.add_command(label='New', command=self.new, accelerator='Ctrl+N')
        self.add_command(label='Open...', command=self.open, accelerator='Ctrl+O')
        self.add_command(label='Save', command=self.save, accelerator='Ctrl+S')
        self.add_command(label='Save as...', command=self.save_as)
        self.add_separator()
        self.add_command(label='Exit', command=self.exit)

        self.filetypes = [
            ('docal file', '*dcl'),
            ('Python file', '*py'),
            ('Excel worksheet', '*.xlsx'),
        ]

        self.worksheet = self.master.master.worksheet

        self.bind_all('<Control-n>', lambda e: self.new())
        self.bind_all('<Control-o>', lambda e: self.open())
        self.bind_all('<Control-s>', lambda e: self.save())

    def new(self):
        current = self.worksheet.frame.grid_slaves()
        if not (len(current) == 1 and not current[0].current_str.strip()):  # maybe sth useful
            response = messagebox.askyesnocancel('Not saved', 'Save current file?')
            if response:
                self.save_as()
            elif response is None:
                return
        for step in current:
            step.destroy()
        self.worksheet.add(None)
        self.master.master.change_filename()
        return True

    def open(self):
        if not self.new():
            return
        filename = filedialog.askopenfilename(filetypes=self.filetypes, defaultextension='.dcl')
        if not filename:
            return
        with open(filename) as file:
            data = load(file)
        self.worksheet.frame.grid_slaves()[0].destroy()
        for step in data['data'][0]['data']:
            wid = self.worksheet.add(None)
            wid.input.insert(0, step)
            wid.render()
        self.master.master.change_filename(filename)

    def save(self):
        if self.master.master.file_selected:
            self.to_file(self.master.master.filename)
            print(self.master.master.filename)
        else:
            self.save_as()

    def to_file(self, filename):
        steps = [step.input.get() for step in self.worksheet.frame.grid_slaves()]
        steps.reverse()
        data = {
            'infile': None,
            'outfile': None,
            'data': [
                {
                    'type': 'ascii',
                    'data': steps
                }
            ]
        }
        with open(filename, 'w', encoding='utf-8') as file:
            dump(data, file, ensure_ascii=False, indent=4)

    def save_as(self):
        filename = filedialog.asksaveasfilename(filetypes=self.filetypes[:-1],
                                                defaultextension='.dcl',
                                                initialfile=self.master.master.default_filename
                                                )
        if not filename:  # cancelled
            return
        self.to_file(filename)
        self.master.master.change_filename(filename)

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
