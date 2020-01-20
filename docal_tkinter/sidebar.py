# -{cd .. | python -m docal_tkinter}
from tkinter.ttk import Frame, Label, Entry, Button, Labelframe, OptionMenu, Label
from tkinter import filedialog, messagebox, StringVar
from os import startfile, path

from docal import document
from docal.handlers import word, latex
from docal.parsers.dcl import parse

class Sidebar(Frame):
    def __init__(self, master):
        super().__init__(master, borderwidth='.25cm')
        # data (for master)
        self.infile = StringVar(self)
        self.outfile = StringVar(self)

        # infile area
        self.infile_area = InfileArea(self)
        self.infile_area.grid(sticky='ew')

        # outfile area
        self.outfile_area = OutfileArea(self)
        self.outfile_area.grid(sticky='ew', pady=20)

        self.send_btn = Button(self, text='Send', command=self.send_calcs)
        self.send_btn.grid(sticky='ew', padx='.25cm')

    def prepare(self):
        infile = self.infile.get()
        outfile = self.outfile.get()
        if infile.strip():
            ext = path.splitext(infile)[1]
            if ext == '.docx':
                handler = word.handler
            elif ext == '.tex':
                handler = latex.handler
            else:
                return False
        elif outfile.strip():
            ext = path.splitext(outfile)[1]
            if ext == '.docx':
                handler = word.handler
            elif ext == '.tex':
                handler = latex.handler
            else:
                return False
        else:
            return False
        doc = document(infile, outfile, handler=handler)
        return doc

    def clear_calcs(self):
        ext = path.splitext(self.infile.get())[1]
        if ext != '.tex':
            messagebox.showinfo(
                'Not supported',
                'The file type does not support clearing tags in place')
            return
        doc = self.prepare()
        doc.write()
        messagebox.showinfo('Success', 'Cleared.')

    def send_calcs(self):
        try:
            doc = self.prepare()
            if not doc:
                self.bell()
                messagebox.showerror('Error', 'Filetype not supported.')
                return
            self.master.menu.file_menu.save()
            doc.send(parse(self.master.filename))
            doc.write()
        except Exception as e:
            messagebox.showerror('Error', 'Internal error:\n' + str(e.args))
        else:
            self.infile.set(doc.document_file.infile)
            self.outfile.set(doc.document_file.outfile)
            message = ''
            if doc.log:
                message = '\n'.join(doc.log) + '\n\n'
            yes = messagebox.askokcancel(
                'Success', message + 
                'Sent successfully. Do you want to open the output document?')
            if not yes: return
            self.open_file('out')

    def open_file(self, which):
        '''open with default viewer'''
        if which == 'in':
            if not self.infile.get():
                return
            startfile(self.infile.get())
            return
        if not self.outfile.get():
            return
        startfile(self.outfile.get())

    def set_entry_text(self, entry, text):
        if entry == 'in':
            entry = self.infile_area.entry
        else:
            entry = self.outfile_area.entry
        entry.delete(0, 'end')
        entry.insert(0, text)
        entry.xview_moveto(10)

class InfileArea(Labelframe):
    def __init__(self, master):
        super().__init__(master, text='Input document', borderwidth='.25cm')

        self.entry = Entry(self, width=30, textvariable=master.infile)
        self.select_btn = Button(self, text='Select...', command=self.select_infile)
        self.clear_btn = Button(self, text='Clear', width=6, command=self.master.clear_calcs)
        open_btn = Button(self, text='Open', width=6, command=lambda: self.master.open_file('in'))
        self.entry.grid(row=0, column=0, columnspan=5, sticky='nsew')
        self.select_btn.grid(row=1, column=0, columnspan=4, sticky='ew')
        open_btn.grid(row=1, column=4, sticky='ew')

    def toggle_clear_btn(self, show=False):
        if show:
            self.select_btn.grid_configure(columnspan=3)
            self.clear_btn.grid(row=1, column=3, sticky='ew')
        else:
            self.clear_btn.grid_remove()
            self.select_btn.grid_configure(columnspan=4)

    def select_infile(self):
        filename = filedialog.askopenfilename(filetypes=[('Word documents', '*.docx'), ('LaTeX documents', '*.tex')])
        if not filename: return
        if path.splitext(filename)[1] == '.tex':
            self.toggle_clear_btn(True)
        else:
            self.toggle_clear_btn(False)
        self.master.set_entry_text('in', filename)

class OutfileArea(Labelframe):
    def __init__(self, master):
        super().__init__(master, text='Output document', borderwidth='.25cm')

        self.entry = Entry(self, width=30, textvariable=self.master.outfile)
        self.select_btn = Button(self, text='Select...', command=self.select_outfile)
        self.open_btn = Button(self, text='Open', command=lambda: self.master.open_file('out'))
        self.entry.grid(row=0, column=0, columnspan=5, sticky='nsew')
        self.select_btn.grid(row=1, column=0, columnspan=3, sticky='ew')
        self.open_btn.grid(row=1, column=3, columnspan=2, sticky='ew')

    def select_outfile(self):
        filename = filedialog.asksaveasfilename(filetypes=[('Word documents', '*.docx'), ('LaTeX documents', '*.tex')])
        if filename:
            self.master.set_entry_text('out', filename)

