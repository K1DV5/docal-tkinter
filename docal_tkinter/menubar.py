# -{cd .. | python -m docal_tkinter}
from tkinter import Menu, filedialog, messagebox, Toplevel, Label
from json import dump, loads, dumps
from docal.parsers.excel import parse as parse_xl
from docal.parsers.dcl import to_py
from os import path, startfile
from webbrowser import open_new_tab

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
            ('docal file', '*.dcl'),
            ('Python file', '*.py'),
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
            response = messagebox.askyesnocancel('Not saved',
                                                 'Do you want to save changes to '
                                                 + path.basename(self.master.master.filename)
                                                 + '?')
            if response:
                self.save_as()
            elif response is None:
                return
        for step in current:
            step.destroy()
        self.worksheet.add(None)
        self.master.master.change_filename()
        self.sidebar.infile.set('')
        self.sidebar.outfile.set('')
        return True

    def open(self, filename=None):
        if not filename:
            filename = filedialog.askopenfilename(filetypes=self.filetypes)
            if not filename: return
            if not self.new(): return
        ext = path.splitext(filename)[1]
        self.worksheet.frame.grid_slaves()[0].destroy()  # start from scratch
        with open(filename) as file:
            in_file = file.read()
        if ext == '.dcl':
            data = loads(in_file)
            steps = data['data'][0]['data']
            self.sidebar.infile.set(data['infile'])
            self.sidebar.outfile.set(data['outfile'])
        elif ext == '.py':
            steps = in_file.split('\n')
        else:
            messagebox.showerror('Error', 'File type not supported')
            return
        self.master.master.change_filename(filename)
        for step in steps:
            wid = self.worksheet.add(0)  # as editable (not new)
            wid.input.insert(0, step)
        self.worksheet.update_below(None)
        self.current_file_contents = str(self.get_data())

    def save(self):
        self.worksheet.update_below(None) # try to render all
        if self.master.master.file_selected:
            self.save_as(False)
        else:
            self.save_as()

    def get_data(self):
        '''get the data displayed'''
        steps = self.worksheet.frame.grid_slaves(column=0)
        steps.sort(key=lambda s: s.grid_info()['row'])  # preserve grid order
        data = {
            'infile': self.sidebar.infile.get(),
            'outfile': self.sidebar.outfile.get(),
            'data': [
                {
                    'type': 'ascii',
                    'data': [step.current_str for step in steps]
                }
            ]
        }
        return data

    def save_as(self, dialog=True):
        if dialog:
            filename = filedialog.asksaveasfilename(
                filetypes=self.filetypes,
                initialfile=self.master.master.default_filename,
                defaultextension='.dcl',
            )
            if not filename:  # cancelled
                return
        else:
            filename = self.master.master.filename
        ext = path.splitext(filename)[1]
        data = self.get_data()
        if ext not in ('.dcl', '.py'):
            messagebox.showerror('Error', 'File type not supported')
            return
        with open(filename, 'w', encoding='utf-8') as file:
            if ext == '.dcl':
                dump(data, file, ensure_ascii=False)
            elif ext == '.py':
                file.write('\n'.join([to_py(line) for line in data['data'][0]['data']]))
        self.current_file_contents = str(data)
        self.master.master.change_filename(filename)

    def exit(self):
        if self.file_modified():
            response = messagebox.askyesnocancel('Not saved', 'Do you want to save changes to ' + self.master.master.filename + '?')
            if response:
                self.save()
            elif response is None:
                return
        self.master.master.destroy()


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

        self.add_command(label='Select input document', command=self.sidebar.select_infile)
        self.add_command(label='Clear input document', command=self.sidebar.clear_calcs)
        self.add_command(label='Select output document', command=self.sidebar.select_outfile)
        self.add_separator()
        self.add_command(label='Send calculations', command=self.sidebar.send_calcs)

class HelpMenu(Menu):
    def __init__(self, master):
        super().__init__(master, tearoff=0)

        self.add_command(label='Help', command=self.help)
        self.add_command(label='About', command=self.about)

    def help(self):
        startfile('docal.chm')

    def about(self):
        win = Toplevel()
        win.title('About docal')
        Label(win, text='docal', font=(None, 19)).grid(sticky='w')
        Label(win, text='Version 2.2.1').grid(sticky='w')
        Label(win, text='New releases can be found at').grid(sticky='w')
        Label(win, text='\nProject URLs').grid(sticky='w')
        Label(win, text=' (Core project)').grid(row=4, column=1, sticky='w')
        Label(win, text=' (UI project)').grid(row=5, column=1, sticky='w')
        Label(win, text=' (Math renderer project, for the UI)').grid(row=6, column=1, sticky='w')
        links = [
            ('https://github.com/K1DV5/docal-tkinter/releases', 2, 1),
            ('https://github.com/K1DV5/docal', 4, 0),
            ('https://github.com/K1DV5/docal-tkinter', 5, 0),
            ('https://github.com/K1DV5/tkinter-math', 6, 0),
        ]
        for url, row, col in links:
            link = Label(win, text=url, foreground='blue', cursor='hand2')
            link.grid(row=row, column=col, sticky='e')
            link.bind('<1>', lambda e: open_new_tab(e.widget['text']))
        win.protocol('WM_DELETE_WINDOW', lambda: win.destroy())
        win.mainloop()
