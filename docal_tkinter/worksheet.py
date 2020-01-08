# -{cd .. | python -m docal_tkinter}
from tkinter.ttk import Frame, Label, Entry, Scrollbar
from tkinter import font, Canvas, font

import sys
sys.path.insert(1, 'd:/Documents/Code/Projects/docal')
# to render the math
from tkinter_math import syntax, select_font
from docal.parsing import eqn

syntax = syntax()

class Worksheet(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # math_font = font.Font(self, family='consolas', size=16)

        self.frame = self.scrolled_frame()

        math_font = font.Font(family='cambria math', size=14)
        select_font(math_font)

        # dummy with the font for performance when measuring
        Label(self, text='', font=math_font)

        # the data
        self.ins = {}
        self.outs = {}

    def scrolled_frame(self):
        '''make a frame with a scrollbar and that can be scrolled with mouse'''
        # this supports scrollbars, without the light grey border on focus
        canvas = Canvas(self, highlightthickness=0)
        canvas.grid(row=0, column=0, sticky='nsew')

        scrollbar = Scrollbar(self, orient='vertical', command=canvas.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')

        # config scrollbar
        canvas.configure(yscrollcommand=scrollbar.set)

        frame = Frame(canvas)

        # insert the frame into the canvas
        frame_id = canvas.create_window((0, 0), window=frame, anchor='nw')

        # resize the scrolled region with the canvas
        frame.bind('<Configure>',
                   lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        # make the size of the frame always fill the canvas
        canvas.bind('<Configure>',
                    lambda e: canvas.itemconfig(frame_id, width=e.width))
        # bind the mouse as well
        canvas.bind_all('<MouseWheel>',
                        lambda e: canvas.yview_scroll(-1 if e.delta > 0 else 1,
                                                      'units'))
        return frame

    def add(self, event):
        # Label(self.frame, text='hello', font=('', 80)).pack()
        step = Step(self.frame)
        step.pack(fill='x', expand=1)

    def delete(self, event):
        self.frame.winfo_children()[0].destroy()


class Step(Frame):
    def __init__(self, master, kind='python'):
        super().__init__(master)

        self.kind = kind

        self.input = Entry(self)
        self.output = Canvas(self)
        self.input.pack(fill='x')
        # self.output.pack()
        self.input.bind('<Return>', self.calculate)
        self.input.bind('<Escape>', self.restore)
        self.output.bind('<1>', self.edit)

        self.input.focus()

        self.current_str = ''

    def calculate(self, event):
        self.output.delete('all')
        self.current_str = event.widget.get()

        e = eqn(self.current_str, syntax=syntax)
        cwidth = e.size[0]*1.2
        cheight = e.size[1]*1.2
        e.coords = (e.size[0]*0.1, e.size[1]*0.1)

        self.output.config(width=cwidth, height=cheight)
        e.render(self.output)

        self.input.pack_forget()
        self.output.pack()

    def edit(self, event):
        self.output.pack_forget()
        self.input.pack(fill='x')
        self.input.focus()
        self.current_str = self.input.get()

    def restore(self, event):
        self.input.delete(0, 'end')
        self.input.insert(0, self.current_str)
        self.input.pack_forget()
        self.output.pack()

