# -{cd .. | python -m docal_tkinter}
# -{cd .. | ipython --pdb -m docal_tkinter}
import re
from tkinter.ttk import Frame, Label, Entry, Scrollbar
from tkinter import font, Canvas, Listbox, StringVar

import sys
# to render the math
from tkinter_math import syntax, select_font
from docal import document
from docal.parsers.dcl import to_py
from docal.parsing import UNIT_PF, to_math
from docal.handlers.latex import syntax as syntax_latex

def augment_output(output, input_str):
    if output:
        return output
    if input_str.startswith('#@'): # default options
        return [(None, ('text', '[options]'))]
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
        self.current_input = None

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
        if not event_source.output.winfo_ismapped():
            event_source.input.focus()
        elif not child.current_str.strip():
            child.edit(None)

    def delete(self, event):
        self.frame.winfo_children()[0].destroy()

class Step(Frame):
    def __init__(self, master, grand_master):
        super().__init__(master, takefocus=0)
        self.master = grand_master
        self.grid_columnconfigure(0, weight=1)

        self.input = Entry(self)
        self.input_props = {
            'kind': 'math',  # or text
            'y': 0  # not always available, to be set at scroll_into_view, for autocomplete
        }
        self.output = None
        self.output_props = {
            'kind': None,  # disp or inline or text or tag
        }
        self.exception = Label(self, foreground='red', font=(None, 8))

        self.input.bind('<Return>', self.on_return)
        self.input.bind('<BackSpace>', self.merge)
        self.input.bind('<Delete>', self.merge)
        self.input.bind('<Control-Return>', self.split)
        self.input.bind('<Shift-Return>', self.split)
        self.input.bind('<Escape>', self.restore)
        self.input.bind('<Up>', self.edit_neighbour)
        self.input.bind('<Down>', self.edit_neighbour)
        self.input.bind('<FocusIn>', self.on_focus)
        self.input.bind('<Tab>', self.autocomplete)
        self.input.bind('<KeyRelease>', self.autocomplete)
        self.bind('<1>', self.edit)

        self.current_str = ''
        self.mode = 'add'  # or edit

        self.change_displayed('init')
        self.input.focus()

    def autocomplete(self, event):
        menu = self.master.autocomplete
        if event.keysym == 'Tab':
            # prevent from firing many times
            if str(event.type) != 'KeyPress' or not menu.winfo_ismapped():
                return
            direction = 1 if event.state == 8 else -1
            menu.select_next(direction)
            return 'break'
        elif event.keysym in ('Shift_L', 'Shift_R'):
            return
        self.scroll_into_view()
        menu.suggest(self.input, self.input_props['y'])

    def change_displayed(self, kind='input'):
        if kind == 'input':
            self.output.grid_remove()
            self.input.grid()
            return
        if kind == 'init':
            self.input.grid(sticky='ew')
            return
        # output
        self.input.grid_remove()
        if self.output_props['kind'] != kind:
            self.output_props['kind'] = kind
            sticky = 'ew'
            if kind == 'disp':
                self.output = Canvas(self)
                sticky = None
            elif kind == 'inline':
                self.output = Canvas(self)
            elif kind == 'text':
                width = self.input.winfo_width()
                self.output = Label(self, font=self.master.text_font, wraplength=width)
            else:  # tag
                self.output = Label(self, font=(None, 10), foreground='blue')
            self.output.bind('<1>', self.edit)
            self.output.grid_configure(column=0, sticky=sticky)
        self.output.grid()

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
            self.exception.grid(column=0, sticky='ew')
            self.input.bind('<Key>', self.remove_err_msg)
            return False
        else:
            self.exception.grid_remove()
        kind, content = returned[0][1][0], returned[0][1][1]
        self.change_displayed(kind)
        self.__getattribute__('render_' + kind)(content)
        return True

    def on_return(self, event):
        next_step = self.neighbour(1)
        if event and next_step:  # means in the middle, update all
            self.master.update_all(self)
            return
        did_render = self.render()
        if next_step and next_step.output.winfo_ismapped():
                next_step.input.focus()
        elif did_render:
            self.master.add(event)

    def remove_err_msg(self, event):
        self.exception.grid_remove()
        self.input.unbind('<Key>')

    def edit(self, event):
        if self.output and self.output.winfo_ismapped():
            self.change_displayed('input')
        self.input.focus()
        self.current_str = self.input.get()

    def edit_neighbour(self, event):
        direction = 1 if event.keysym == 'Down' else -1
        neighbour = self.neighbour(direction)
        if not neighbour:
            return
        if self.output and not self.exception.winfo_ismapped():
            self.restore(None)
        neighbour.edit(None)

    def restore(self, event):
        self.input.delete(0, 'end')
        self.input.insert(0, self.current_str)
        self.change_displayed(self.output_props['kind'])

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
        new.input.icursor(0)

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

    def on_focus(self, event):
        self.scroll_into_view()
        # update the values above
        self.master.doc_obj.working_dict = {}
        this_row = self.grid_info()['row']
        steps = self.master.frame.grid_slaves()
        i = len(steps) - 1
        if not steps:
            return
        while i > -1:
            if steps[i].grid_info()['row'] == this_row:
                break
            steps[i].render()
            i -= 1

    def scroll_into_view(self):
        self.master.current_input = self.input
        self.master.update()  # will always get winfo_y() = 0 without this
        view_range = self.master.canvas.yview()
        canvas_height = int(self.master.canvas['scrollregion'].split()[3])
        top_offset = self.winfo_y()
        height = self.winfo_height()
        # store info for autocomplete
        self.input_props['y'] = top_offset + height - canvas_height * view_range[0]
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

class Autocomplete(Listbox):
    def __init__(self, master):
        super().__init__(master)

        self.entry = None
        self.trigger = ''
        self.index_replace = (0, 0)
        self.pattern = re.compile('[\w\d]+$')

        self.listvar = StringVar(self)
        self.config(listvar=self.listvar)
        self.font = font.Font(family='TkTextFont')  # this has to match the one for the inputs

        # items list limit
        self.limit = 5
        self.len = 0
        self.selected = None

        self.bind('<<ListboxSelect>>', self.on_select)

    def select_next(self, direction):
        if not direction:
            if self.selected is not None:
                self.select_clear(self.selected)
                self.selected = None
            return
        if self.selected is not None:
            self.select_clear(self.selected)
        if direction == 1:  # without shift
            if self.selected is None:
                self.selected = 0
            elif self.selected + 1 < self.len:
                self.selected += 1
            else:
                self.selected = None
        else:  # with shift
            if self.selected is None:
                self.selected = self.len - 1
            elif self.selected > 0:
                self.selected -= 1
            else:
                self.selected = None
        if self.selected is not None:
            self.selection_set(self.selected)
        self.on_select(None)
        return 'break'

    def on_select(self, event):
        if self.selected is None:
            selected = self.trigger
        else:
            selected = self.selection_get().split('=')[0]
        self.entry.delete(self.index_replace[0], self.index_replace[1])
        self.entry.insert(self.index_replace[0], selected)
        self.index_replace = self.index_replace[0], self.index_replace[0] + len(selected)

    def not_needed(self, text):
        return text.endswith(' ')

    def suggest(self, entry, coord_y):
        entry_cursor = entry.index('insert')
        current = entry.get()[:entry_cursor]
        if self.not_needed(current):
            self.place_forget()
            return
        match = self.pattern.search(current)
        if not match:
            self.place_forget()
            return
        trigger = match.group(0)
        if not trigger.isidentifier():
            self.place_forget()
            return
        len_trigger = len(trigger)
        matches = []
        space = self.master.doc_obj.working_dict
        for key in space:
            if key.startswith(trigger) and not key.endswith(UNIT_PF):
                item = key
                value = space[key]
                if isinstance(value, (int, float)):
                    unit = to_math(space[key + UNIT_PF], div='/', syntax=syntax_txt(), ital=False)
                    item += '=' + str(value) + unit
                elif isinstance(value, list):
                    item += '[matrix]'
                matches.append(item)
        if not matches:
            self.place_forget()
            return
        self.entry = entry
        self.trigger = trigger
        self.index_replace = (entry_cursor - len(trigger), entry_cursor)
        self.listvar.set(' '.join(matches[:self.limit]))
        coord_x = entry.winfo_x() + round(self.font.measure(current[:self.index_replace[0]]) * 0.811) + self['borderwidth']
        self.place(x=coord_x, y=coord_y)
        self.select_next(0)
        self.config(height=self.size())
        self.len = self.size()


class syntax_txt:
    '''for units on completion'''
    halfsp = ''
    greek_letters = []
    math_accents = []
    primes = []
    transformed = []

    def txt_rom(self, txt):
        return txt

    def txt(self, txt):
        return txt
