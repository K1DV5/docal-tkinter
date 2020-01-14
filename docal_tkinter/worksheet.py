# -{cd .. | python -m docal_tkinter}
# -{cd .. | ipython --pdb -m docal_tkinter}
import re
from tkinter.ttk import Frame, Label, Entry, Scrollbar
from tkinter import font, Canvas, Listbox, StringVar

import sys
sys.path.insert(1, 'd:/Documents/Code/Projects/tkinter-math')
sys.path.insert(1, 'd:/Documents/Code/Projects/docal')
# to render the math
from tkinter_math import syntax, select_font
from docal import document
from docal.parsers.dcl import to_py
from docal.parsing import UNIT_PF

def augment_output(output, input_str):
    if output:
        return output
    if input_str.strip().startswith('#'):  # means a tag
        tag = input_str.strip()
        return [(None, ('tag', tag))]
    elif input_str.strip():  # arbitrary code
        return [(None, ('text', '[code]'))]
    return [(None, ('text', ' '))]

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

        self.frame, self.canvas = self.scrolled_frame()
        self.frame.grid_columnconfigure(0, weight=1)

        math_font = font.Font(family='cambria math', size=12)
        select_font(math_font)
        self.text_font = font.Font(family='times', size=12)

        # dummy with the font for performance when measuring
        Label(self, text='', font=math_font)

        self.doc_obj = document(None, 'untitled.tex', handler, working_dict={})
        self.process = self.doc_obj.process

        self.autocomplete = Autocomplete(self)

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
        # resize the scrolled region with canvas, + some clearance from bottom
        frame.bind('<Configure>', lambda e: canvas.configure(
            scrollregion=(*canvas.bbox('all')[:3],
                          canvas.bbox('all')[3] + 150)))
        # make the size of the frame always fill the canvas
        canvas.bind('<Configure>',
                    lambda e: canvas.itemconfig(frame_id, width=e.width))
        # bind the mouse as well
        canvas.bind_all('<MouseWheel>',
                        lambda e: canvas.yview_scroll(-1 if e.delta > 0 else 1,
                                                      'units'))
        return frame, canvas

    def add(self, event):
        step = Step(self.frame, self)
        step.grid(sticky='ew')
        return step

    def update_all(self, event_source):
        self.doc_obj.working_dict = {}
        for child in self.frame.winfo_children():
            child.render()
        if not event_source.is_rendered():
            event_source.input.focus()
        elif not child.current_str.strip():
            child.edit(None)

    def delete(self, event):
        self.frame.winfo_children()[0].destroy()

class Autocomplete(Listbox):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        self.coord_y = 0  # this is not available with winfo_y, set using scroll_into_view

        self.listvar = StringVar(self)
        self.config(listvar=self.listvar)
        self.font = font.Font(family='TkTextFont')  # this has to match the one for the inputs

        self.entry = None
        self.matches = []

        # items list limit
        self.limit = 5

    def show(self, x, y):
        self.place(x=x, y=y)
        self.entry.bind('<Tab>', self.select_next)
        self.entry.bind('<Shift-Tab>', self.select_next)
        self.config(height=len(self.matches))

    def hide(self):
        self.place_forget()
        self.entry.unbind('<Tab>')
        self.entry.unbind('<Shift-Tab>')

    def select_next(self, event):
        print(self.selection_get())

    def not_needed(self, text):
        return text.endswith(' ')

    def suggest(self, event):
        i_cursor = self.entry.index('insert')
        current = self.entry.get()[:i_cursor]
        if self.not_needed(current):
            self.hide()
            return
        current_word = current.split(' ')[-1]
        if not current_word.isidentifier():
            self.hide()
            return
        self.matches = [key for key in self.master.doc_obj.working_dict if key.startswith(current_word) and not key.endswith(UNIT_PF) and len(key) > 1]
        if not self.matches:
            self.hide()
            return
        self.listvar.set(' '.join(self.matches[:self.limit]))
        coord_y = self.coord_y + self.entry.winfo_height()
        coord_x = self.entry.winfo_x() + round(self.font.measure(current) * 0.811)
        self.show(coord_x, coord_y)

class Step(Frame):
    def __init__(self, master, grand_master):
        super().__init__(master)
        self.master = grand_master

        self.input = Entry(self, font=('TkTextFont',))
        self.input_props = {
            'kind': 'ascii',  # or python or excel
            'y': 0  # not always available, to be set at scroll_into_view, for autocomplete
        }
        self.output = Canvas(self)
        self.output_props = {
            'kind': 'disp',  # or inline or text or tag
            'pack': {}
        }
        self.exception = Label(self, foreground='red', font=(None, 8))

        self.input.pack(fill='x')

        self.input.bind('<Return>', self.on_return)
        self.input.bind('<BackSpace>', self.merge)
        self.input.bind('<Delete>', self.merge)
        self.input.bind('<Control-Return>', self.split)
        self.input.bind('<Shift-Return>', self.split)
        self.input.bind('<Escape>', self.restore)
        self.input.bind('<Up>', self.edit_neighbour)
        self.input.bind('<Down>', self.edit_neighbour)
        self.input.bind('<FocusIn>', self.scroll_into_view)
        self.input.bind('<KeyRelease>', self.autocomplete)
        self.output.bind('<1>', self.edit)
        self.bind('<1>', self.edit)

        self.input.focus()

        self.current_str = ''
        self.mode = 'add'  # or edit

    def autocomplete(self, event):
        self.master.autocomplete.coord_y = self.input_props['y']
        self.master.autocomplete.entry = self.input
        self.master.autocomplete.suggest(event)

    def set_output(self, kind):
        '''cheap widget type change'''
        self.input.pack_forget()
        if self.output_props['kind'] == kind:
            self.output.pack(**self.output_props['pack'])
            return
        self.output_props['kind'] = kind
        self.output.destroy()
        if kind == 'disp':
            self.output = Canvas(self)
            self.output_props['pack'] = {}
        elif kind == 'inline':
            self.output = Canvas(self)
            self.output_props['pack'] = {'fill': 'x'}
        elif kind == 'text':
            width = self.input.winfo_width()
            self.output = Label(self, font=self.master.text_font, wraplength=width)
            self.output_props['pack'] = {'fill': 'x'}
        else:  # tag
            self.output = Label(self, font=(None, 10), foreground='blue')
            self.output_props['pack'] = {'fill': 'x'}
        self.output.pack(**self.output_props['pack'])
        self.output.bind('<1>', self.edit)

    def render_disp(self, math):
        self.output.delete('all')
        cwidth = math.size[0]*1.2
        cheight = math.size[1]*1.2
        math.coords = (math.size[0]*0.1, math.size[1]*0.1)

        self.output.config(width=cwidth, height=cheight)
        math.render(self.output)

    def render_inline(self, math):
        self.output.delete('all')
        self.output.config(width=math.size[0], height=math.size[1])
        math.render(self.output)

    def render_text(self, text):
        self.output.config(text=text)

    def render_tag(self, tag):
        self.output.config(text=tag)

    def render(self):
        self.current_str = self.input.get().replace('\n', ' ')
        input_str = to_py(self.current_str)

        try:
            returned = augment_output(self.master.process(input_str), input_str)
        except Exception as exc:
            self.edit(None)
            message = exc.args[0]
            self.exception.config(text=message)
            self.exception.pack(fill='x')
            self.input.bind('<Key>', self.remove_err_msg)
            return False
        else:
            self.exception.pack_forget()
        kind, content = returned[0][1][0], returned[0][1][1]
        self.set_output(kind)
        self.__getattribute__('render_' + kind)(content)
        return True

    def on_return(self, event):
        next_step = self.neighbour(1)
        if event and next_step:  # means in the middle, update all
            self.master.update_all(self)
            return
        did_render = self.render()
        if next_step and next_step.is_rendered():
                next_step.input.focus()
        elif did_render:
            self.master.add(event)

    def remove_err_msg(self, event):
        self.exception.pack_forget()
        self.input.unbind('<Key>')

    def edit(self, event):
        if self.is_rendered():
            self.remove_err_msg(event)
            self.output.pack_forget()
            self.input.pack(fill='x')
        self.input.focus()
        self.current_str = self.input.get()

    def edit_neighbour(self, event):
        direction = 1 if event.keysym == 'Down' else -1
        neighbour = self.neighbour(direction)
        if not neighbour:
            return
        if not self.exception.winfo_ismapped():
            self.restore(None)
        neighbour.edit(None)

    def restore(self, event):
        self.input.delete(0, 'end')
        self.input.insert(0, self.current_str)
        self.input.pack_forget()
        self.output.pack(**self.output_props['pack'])

    def merge(self, event):
        cursor_idx = self.input.index('insert')
        if event.keysym == 'BackSpace':
            if cursor_idx > 0:
                return
            insert_pos = 'end'
            neighbour = self.neighbour(-1)
        elif event.keysym == 'Delete':
            if cursor_idx < self.input.index('end'):
                return
            insert_pos = 0
            neighbour = self.neighbour(1)
        else:
            return
        if not neighbour:
            return
        neighbour.edit(None)
        if event.keysym == 'BackSpace':
            cursor_idx = neighbour.input.index(insert_pos)
        current_content = self.input.get()
        neighbour.input.insert(insert_pos, current_content)
        neighbour.input.icursor(cursor_idx)
        self.destroy()

    def split(self, event):
        current_content = self.input.get()
        i_cursor = self.input.index('insert')
        self.input.delete(i_cursor, 'end')
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

    def neighbour(self, direction=0):
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
        return False if self.neighbour(1) else True

    def is_rendered(self):
        return not isinstance(self.pack_slaves()[0], Entry)

    def scroll_into_view(self, event):
        self.master.update()  # will always get winfo_y() = 0 without this
        view_range = self.master.canvas.yview()
        canvas_height = int(self.master.canvas['scrollregion'].split()[3])
        top_offset = self.winfo_y()
        # store info for autocomplete
        self.input_props['y'] = top_offset
        height = self.winfo_height()
        to_bottom = top_offset + height > canvas_height * view_range[1]
        to_top = top_offset < canvas_height * view_range[0]
        if to_top:
            offset = top_offset - view_range[0] * canvas_height
        elif to_bottom:
            offset = top_offset + height - canvas_height * view_range[1]
        else:
            return
        new = offset / canvas_height + view_range[0]
        self.master.canvas.yview_moveto(new)

