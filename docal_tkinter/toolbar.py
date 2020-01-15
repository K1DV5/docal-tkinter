# -{cd .. | python -m docal_tkinter}
from tkinter.ttk import Frame, LabelFrame, Radiobutton, Entry, Label, Button
from docal.handlers.word import PRIMES, GREEK_LETTERS

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

        # print(event.widget.winfo_x(), step.input_props['y'], self.winfo_width())

class Options(LabelFrame):
    def __init__(self, master):
        super().__init__(master, text='Options')

        self.unit = Entry(self)
        unit_label = Label(self, text='Unit: ')
        unit_label.grid(sticky='ew', pady=10)
        self.unit.grid(row=0, column=1, sticky='ew')

        self.note = Entry(self)
        note_label = Label(self, text='Note: ')
        note_label.grid(sticky='ew')
        self.note.grid(row=1, column=1, sticky='ew')

        self.steps = LabelFrame(self, text='Steps')
        self.step_1 = Radiobutton(self.steps, text='Equation')
        self.step_2 = Radiobutton(self.steps, text='Equation with values')
        self.step_3 = Radiobutton(self.steps, text='Result')
        self.step_1.grid(sticky='ew', padx=10)
        self.step_2.grid(sticky='ew', padx=10)
        self.step_3.grid(sticky='ew', padx=10)
        self.steps.grid(sticky='ew', columnspan=2, pady=10)

        self.inline = Radiobutton(self, text='Inline')
        self.inline.grid(sticky='ew', columnspan=2)

        self.horizontal = Radiobutton(self, text='Horizontal')
        self.horizontal.grid(sticky='ew', columnspan=2)

        self.hidden = Radiobutton(self, text='Hidden')
        self.hidden.grid(sticky='ew', columnspan=2)

        self.clear_options = Button(self, text='Clear', command=self.clear_options)
        self.clear_options.grid()

        self.insert_btn = Button(self, text='Insert', command=self.insert_options)
        self.insert_btn.grid(row=6, column=1, sticky='ew')

    def insert_options(self):
        print('options')

    def clear_options(self):
        print('clear_options')

class Greek(LabelFrame):
    def __init__(self, master):
        super().__init__(master, text='Greek letters')
        self.data = {}
        self.create_table(self, GREEK_LETTERS, self.insert_letter)

    @staticmethod
    def create_table(self, data, command):
        cols = 10
        row = col = 0
        for key, val in data.items():
            self.data[val] = key
            label = Label(self, text=val)
            label.grid(row=row, column=col)
            label.bind('<1>', command)
            if col == cols:
                col = 0
                row += 1
            else:
                col += 1
        for col in range(cols):
            self.grid_columnconfigure(col, weight=1)

    def insert_letter(self, event):
        print(event.widget['text'])

class Accents(LabelFrame):
    def __init__(self, master):
        super().__init__(master, text='Accents')
        self.data = {}
        Greek.create_table(self, {**MATH_ACCENTS, **PRIMES}, self.insert_accent)

    def insert_accent(self, event):
        print(event.widget['text'])
