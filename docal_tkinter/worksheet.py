# -{cd .. | python -m docal_tkinter}
from tkinter.ttk import Frame, Label, Entry, Scrollbar
from tkinter import font, Canvas, font

import sys
sys.path.insert(1, 'd:/Documents/Code/Projects/tkinter-math')
sys.path.insert(1, 'd:/Documents/Code/Projects/docal')
# to render the math
from tkinter_math import syntax, select_font
from docal import document

# just to get the process method from document
class handler:
    syntax = syntax()
    def __init__(self, infile, pattern, to_clear):
        self.tags = []
        pass
    def write(self, outfile, values):
        pass

class Worksheet(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # math_font = font.Font(self, family='consolas', size=16)

        self.frame = self.scrolled_frame()
        self.frame.grid_columnconfigure(0, weight=1)

        math_font = font.Font(family='cambria math', size=14)
        select_font(math_font)

        # dummy with the font for performance when measuring
        Label(self, text='', font=math_font)

        self.working_dict = {}
        self.process = document(None, 'untitled.tex', handler, working_dict=self.working_dict).process

        self.add(None)

    def scrolled_frame(self):
        '''make a frame with a scrollbar and that can be scrolled with mouse'''
        # this supports scrollbars, without the light grey border on focus
        canvas = Canvas(self, highlightthickness=0)
        canvas.grid(row=0, column=0, sticky='nsew')

        scrollbar = Scrollbar(self, orient='vertical', command=canvas.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
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
        step = Step(self.frame, self)
        step.grid(sticky='ew')

    def delete(self, event):
        self.frame.winfo_children()[0].destroy()


class Step(Frame):
    def __init__(self, master, grand_master, kind='python'):
        super().__init__(master)
        self.master = grand_master

        self.kind = kind

        self.input = Entry(self)
        self.output = Canvas(self)
        self.input.pack(fill='x')
        # self.output.pack()
        self.input.bind('<Return>', self.calculate)
        self.input.bind('<BackSpace>', self.merge)
        self.input.bind('<Escape>', self.restore)
        self.output.bind('<1>', self.edit)
        self.bind('<1>', self.edit)

        self.input.focus()

        self.current_str = ''
        self.mode = 'add'  # or edit

    def calculate(self, event):
        self.output.delete('all')
        self.current_str = event.widget.get()

        returned = self.master.process(self.current_str)
        if returned[0][1][0] == 'text':
            print(returned[0][1][1])
        else:
            e = returned[0][1][1]
            cwidth = e.size[0]*1.2
            cheight = e.size[1]*1.2
            e.coords = (e.size[0]*0.1, e.size[1]*0.1)

            self.output.config(width=cwidth, height=cheight)
            e.render(self.output)

            self.input.pack_forget()
            self.output.pack()

            if self.mode == 'add':
                self.master.add(event)

    def edit(self, event):
        self.mode = 'edit'
        self.output.pack_forget()
        self.input.pack(fill='x')
        self.input.focus()
        self.current_str = self.input.get()

    def restore(self, event):
        self.input.delete(0, 'end')
        self.input.insert(0, self.current_str)
        self.input.pack_forget()
        self.output.pack()

    def merge(self, event):
        if event.widget.index('insert') == 0:
            current_content = event.widget.get()
            if not current_content.strip():
                breakpoint()
                self.destroy()
            else:
                pass
