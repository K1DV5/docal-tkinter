# -{cd .. | python -m docal_tkinter}
from tkinter import Menu, filedialog, messagebox
from json import dump, loads, dumps
from os import path

class Menubar(Menu):
    def __init__(self, master):
        super().__init__(master, tearoff=0)

        self.file_menu = FileMenu(self)

        self.add_cascade(label='File', menu=self.file_menu)
        self.add_cascade(label='Edit', menu=EditMenu(self))
        self.add_cascade(label='Operations', menu=OpsMenu(self))
        self.add_cascade(label='Help', menu=HelpMenu(self))

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
        self.sidebar = self.master.master.sidebar

        self.bind_all('<Control-n>', lambda e: self.new())
        self.bind_all('<Control-o>', lambda e: self.open())
        self.bind_all('<Control-s>', lambda e: self.save())

        self.current_file_contents = str(self.get_data())

    def file_modified(self):
        return str(self.get_data()) != self.current_file_contents

    def new(self):
        current = self.worksheet.frame.grid_slaves()
        if self.file_modified():  # maybe sth useful
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
        filename = filedialog.askopenfilename(filetypes=self.filetypes)
        if not filename:
            return
        with open(filename) as file:
            self.current_file_contents = file.read()
        ext = path.splitext(filename)[1]
        self.worksheet.frame.grid_slaves()[0].destroy()
        if ext == '.dcl':
            data = loads(self.current_file_contents)
            for step in data['data'][0]['data']:
                wid = self.worksheet.add(0)  # as editable (not new)
                wid.input.insert(0, step)
            self.worksheet.update_below(None)
            self.sidebar.infile.set(data['infile'])
            self.sidebar.outfile.set(data['outfile'])
            self.master.master.change_filename(filename)
        elif ext == '.py':
            for step in self.current_file_contents.split('\n'):
                wid = self.worksheet.add(None)
                wid.input.insert(0, step.strip())
            # self.worksheet.update_below(None)

    def save(self):
        if self.master.master.file_selected:
            with open(self.master.master.filename, 'w', encoding='utf-8') as file:
                dump(self.get_data(), file, ensure_ascii=False)
        else:
            self.save_as()

    def get_data(self):
        steps = [step.input.get() for step in self.worksheet.frame.grid_slaves()]
        steps.reverse()
        data = {
            'infile': self.sidebar.infile.get(),
            'outfile': self.sidebar.outfile.get(),
            'data': [
                {
                    'type': 'ascii',
                    'data': steps
                }
            ]
        }
        return data

    def save_as(self):
        filename = filedialog.asksaveasfilename(filetypes=self.filetypes[:-1],
                                                defaultextension='.dcl',
                                                initialfile=self.master.master.default_filename
                                                )
        if not filename:  # cancelled
            return
        self.current_file_contents = self.get_data()
        with open(filename, 'w', encoding='utf-8') as file:
            dump(self.current_file_contents, file, ensure_ascii=False)
        self.current_file_contents = str(self.current_file_contents)
        self.master.master.change_filename(filename)

    def exit(self):
        if self.file_modified():
            response = messagebox.askyesnocancel('Not saved', 'File modified. Do you want to save it?')
            if response:
                self.save()
            elif response is None:
                return
        self.master.master.quit()

class EditMenu(Menu):
    def __init__(self, master):
        super().__init__(master, tearoff=0)

        self.worksheet = self.master.master.worksheet

        self.add_command(label='Cut', command=lambda: self.clipboard('Cut'), accelerator='Ctrl+X')
        self.add_command(label='Copy', command=lambda: self.clipboard('Copy'), accelerator='Ctrl+C')
        self.add_command(label='Paste', command=lambda: self.clipboard('Paste'), accelerator='Ctrl+V')

        self.add_separator()

        self.add_command(label='Undo', command=lambda: self.worksheet.undo(None), accelerator='Ctrl+Z')
        self.add_command(label='Redo', command=lambda: self.worksheet.redo(None), accelerator='Ctrl+Y')

        self.bind_all('<3>', self.show_context)

    def clipboard(self, action):
        entry = self.worksheet.current_input
        if not entry.winfo_ismapped():
            return
        entry.event_generate(f'<<{action}>>')

    def show_context(self, event):
        '''for right click'''
        self.post(event.x_root, event.y_root)

class OpsMenu(Menu):
    def __init__(self, master):
        super().__init__(master, tearoff=0)

        self.sidebar = self.master.master.sidebar

        self.add_command(label='Select input document', command=self.sidebar.infile_area.select_infile)
        self.add_command(label='Clear input document', command=self.sidebar.clear_calcs)
        self.add_command(label='Select output document', command=self.sidebar.outfile_area.select_outfile)
        self.add_separator()
        self.add_command(label='Send calculations', command=self.sidebar.send_calcs)

class HelpMenu(Menu):
    def __init__(self, master):
        super().__init__(master, tearoff=0)

        self.add_command(label='Help', command=self.help)
        self.add_command(label='About', command=self.about)

    def help(self):
        print('help')

    def about(self):
        messagebox.showinfo('About', 'docal\n\n2.2.1\n\n2020')
