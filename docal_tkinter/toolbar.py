# -{cd .. | python -m docal_tkinter}
from tkinter.ttk import Frame, LabelFrame, Checkbutton, Entry, Label, Button, Style
from tkinter import IntVar
from docal.document.word import PRIMES, GREEK_LETTERS

MATH_ACCENTS = {
    'hat': '\u0302',
    'check': '\u030C',
    'breve': '\u02D8',
    'acute': '\u0301',
    'grave': '\u0300',
    'tilde': '\u0303',
    'bar': '\u0304',
    'vec': '\u20D7',
    'dot': '\u0307',
    'ddot': '\u0308',
    'dddot': '\u20DB',
    }


class Toolbar(Frame):
    def __init__(self, master):
        super().__init__(master)

        self.options = Options(self)
        self.options.grid(sticky='ew', padx=10, pady=10)

        self.greek = Greek(self)
        self.greek.grid(sticky='ew', padx=10)

        self.accents = Accents(self)
        self.accents.grid(sticky='ew', padx=10, pady=10)

        self.style = Style()
        self.style.map('TLabel', background=[('active', 'blue')])

class Options(LabelFrame):
    def __init__(self, master):
        super().__init__(master, text='Options')

        self.unit = Entry(self)
        unit_label = Label(self, text='Unit')
        unit_label.grid(sticky='ew', pady=10)
        self.unit.grid(row=0, column=1, sticky='ew')

        self.note = Entry(self)
        note_label = Label(self, text='Note')
        note_label.grid(sticky='ew')
        self.note.grid(row=1, column=1, sticky='ew')

        steps = LabelFrame(self, text='Steps')
        self.step_vars = [IntVar(self, value=0), IntVar(self, value=0), IntVar(self, value=0)]
        step_1 = Checkbutton(steps, text='Equation', variable=self.step_vars[0])
        step_2 = Checkbutton(steps, text='Equation with values', variable=self.step_vars[1])
        step_3 = Checkbutton(steps, text='Result', variable=self.step_vars[2])
        step_1.grid(sticky='ew', padx=10)
        step_2.grid(sticky='ew', padx=10)
        step_3.grid(sticky='ew', padx=10)
        steps.grid(sticky='ew', columnspan=2, pady=10, padx=10)

        self.v_inline = IntVar(self, value=0)
        inline = Checkbutton(self, text='Inline', variable=self.v_inline)
        inline.grid(sticky='ew', columnspan=2)

        self.v_horiz = IntVar(self, value=0)
        horizontal = Checkbutton(self, text='Horizontal', variable=self.v_horiz)
        horizontal.grid(sticky='ew', columnspan=2)

        self.v_hidden = IntVar(self, value=0)
        hidden = Checkbutton(self, text='Hidden', variable=self.v_hidden)
        hidden.grid(sticky='ew', columnspan=2)

        self.grid_rowconfigure(6, pad=10)
        clear_btn = Button(self, text='Clear', command=self.clear_options, width=7)
        clear_btn.grid()
        insert_btn = Button(self, text='Insert', command=self.insert_options)
        insert_btn.grid(row=6, column=1, sticky='ew')

    def insert_options(self):
        entry = self.master.master.worksheet.current_input
        if not entry or not entry.winfo_ismapped():
            self.bell()
            return
        options = []
        unit = self.unit.get()
        if unit.strip():
            options.append(unit)
        note = self.note.get()
        if ',' in note:
            options.append('#(' + note + ')')
        elif note.strip():
            options.append('#' + note)
        steps = ''.join([str(i + 1) for i, var in enumerate(self.step_vars) if var.get()])
        if steps:
            options.append(steps)
        if self.v_inline.get():
            options.append('$')
        if self.v_horiz.get():
            options.append('-')
        if self.v_hidden.get():
            options.append(';')
        self.clear_options()
        current = entry.get()
        if current.strip():
            if options:
                entry.insert('end', ' # ' + ', '.join(options))
        else:
            entry.insert('end', '#@ ' + ', '.join(options))
        entry.focus()

    def clear_options(self):
        entry = self.master.master.worksheet.current_input
        if not entry or not entry.winfo_ismapped():
            self.bell()
            return
        current = entry.get()
        i_hash = current.find('#')
        i_del = len(current[:i_hash].rstrip())
        if i_hash == -1: return
        entry.delete(i_del, 'end')
        entry.focus()

class Greek(LabelFrame):
    def __init__(self, master):
        super().__init__(master, text='Symbols')
        self.data = self.create_table(self, {**GREEK_LETTERS, 'integral': '\u222B'}, self.insert_letter)

    @staticmethod
    def create_table(self, data, command):
        cols = 9
        row = col = 0
        collect = {}
        for key, val in data.items():
            collect[val] = key
            label = Label(self, text=val)
            label.grid(row=row, column=col, sticky='ew')
            label.bind('<1>', command)
            if col == cols:
                col = 0
                row += 1
            else:
                col += 1
        for col in range(cols):
            self.grid_columnconfigure(col, weight=1)
        return collect

    def insert_letter(self, event):
        entry = self.master.master.worksheet.focus_get()
        if not entry: return
        until_cursor = entry.get()[: entry.icursor('insert')]
        if until_cursor:
            last_char = until_cursor[-1]
            if last_char.isalpha() or last_char.isdigit():
                return
        letter = self.data[event.widget['text']]
        entry.insert(entry.index('insert'), letter)

class Accents(LabelFrame):
    def __init__(self, master):
        super().__init__(master, text='Accents')
        self.data = Greek.create_table(self, {**MATH_ACCENTS, **PRIMES}, self.insert_accent)

    def insert_accent(self, event):
        entry = self.master.master.worksheet.focus_get()
        if not entry: return
        until_cursor = entry.get()[: entry.icursor('insert')]
        if not until_cursor: return
        last_char = until_cursor[-1]
        if not last_char.isalpha() and not last_char.isdigit(): return
        accent = self.data[event.widget['text']]
        entry.insert(entry.index('insert'), '_' + accent)
