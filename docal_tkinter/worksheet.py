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
        return step

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
        self.input.bind('<Return>', self.render)
        self.input.bind('<BackSpace>', self.merge)
        self.input.bind('<Delete>', self.merge)
        self.input.bind('<Control-Return>', self.split)
        self.input.bind('<Shift-Return>', self.split)
        self.input.bind('<Escape>', self.restore)
        self.output.bind('<1>', self.edit)
        self.bind('<1>', self.edit)

        self.input.focus()

        self.current_str = ''
        self.mode = 'add'  # or edit

    def render(self, event=None):
        self.output.delete('all')
        self.current_str = self.input.get()

        is_last = self.is_last()
        if not is_last:
            self.master.working_dict = {}

        returned = self.master.process(self.current_str)
        if returned[0][1][0] == 'text':
            print(returned[0][1][1])
            return False
        e = returned[0][1][1]
        cwidth = e.size[0]*1.2
        cheight = e.size[1]*1.2
        e.coords = (e.size[0]*0.1, e.size[1]*0.1)

        self.output.config(width=cwidth, height=cheight)
        e.render(self.output)
        self.input.pack_forget()
        self.output.pack()
        if is_last:
            self.master.add(event)

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

    def merge(self, event):
        cursor_idx = event.widget.index('insert')
        if event.keysym == 'BackSpace':
            if cursor_idx > 0:
                return
            insert_pos = 'end'
            sibling = self.sibling(-1)
        elif event.keysym == 'Delete':
            if cursor_idx < event.widget.index('end'):
                return
            insert_pos = 0
            sibling = self.sibling(1)
        else:
            return
        if not sibling:
            return
        sibling.edit(None)
        if event.keysym == 'BackSpace':
            cursor_idx = sibling.input.index(insert_pos)
        current_content = event.widget.get()
        sibling.input.insert(insert_pos, current_content)
        sibling.input.icursor(cursor_idx)
        self.destroy()

    def split(self, event):
        current_content = event.widget.get()
        i_cursor = event.widget.index('insert')
        event.widget.delete(i_cursor, 'end')
        self.render()

        this_row = self.grid_info()['row']
        if not self.is_last():
            for step in self.master.frame.grid_slaves(column=0):
                row = step.grid_info()['row']
                if row > this_row:
                    step.grid_forget()
                    step.grid(row=row+1, sticky='ew')

        new = self.master.add(None)
        new.grid_forget()
        new.grid(row=this_row + 1, sticky='ew')
        new.input.insert(0, current_content[i_cursor:])

    def sibling(self, direction=0):
        n_row = self.grid_info()['row']
        if n_row + direction < 0 or direction == 0:
            return False
        if direction < 0:
            next_exists = lambda row: row > 0
            increment = -1
        else:
            rowsize = self.master.frame.grid_size()[1]
            next_exists = lambda row: row < rowsize
            increment = 1
        row = n_row
        while next_exists(row):
            row += increment
            siblings = self.master.frame.grid_slaves(row=row)
            if siblings:
                return siblings[0]
        return False

    def is_last(self):
        return False if self.sibling(1) else True
