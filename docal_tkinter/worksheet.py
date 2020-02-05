# -{cd .. | python -m docal_tkinter}
# -{cd .. | ipython --pdb -m docal_tkinter}
import re
from tkinter.ttk import Frame, Label, Entry, Scrollbar, Style
from tkinter import font, Canvas, Listbox, StringVar
from inspect import signature

import sys
# to render the math
from tkinter_math import syntax, select_font
from docal import processor
from docal.parsers.dcl import to_py
from docal.parsing import UNIT_PF, to_math
from docal.document.latex import syntax as syntax_latex

def augment_output(output, input_str):
    if output:
        return output
    if input_str.startswith('#@'): # default options
        return [(None, ('text', '[options]'))]
    if input_str.startswith('##'):  # comments
        return [(None, ('text', '[comment]'))]
    if input_str.strip().startswith('#'):  # means a tag
        tag = input_str.strip()
        return [(None, ('tag', tag))]
    elif input_str.strip():  # arbitrary code
        return [(None, ('text', '[code]'))]
    return [(None, ('text', ' '))]

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

        self.processor = processor(syntax())
        self.process = self.processor.process

        self.autocomplete = Autocomplete(self)
        self.current_input = None

        # for undo/redo
        self.history = []
        self.i_history = 'head'
        self.bind_all('<Control-z>', self.undo)
        self.bind_all('<Control-y>', self.redo)

        first = self.add(None)
        first.is_new = False
        self.update_above(first)  # to include the math functions

        self.style = Style()
        self.style.configure('WS.TFrame', background='white')

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

    def add(self, next_to):
        step = Step(self.frame, self)
        if next_to:
            step.grid(row=next_to.grid_info()['row'] + 1, column=0, sticky='ew')
            self.add_history('add', step, next_to)
        else:
            step.grid(sticky='ew')
        if next_to == 0:
            step.is_new = False  # for when opening file
        else:
            step.edit(None)
        return step

    def update_above(self, step):
        self.processor.working_dict = {}
        self.process('from math import *')  # scientific math funcs
        this_row = step.grid_info()['row']
        steps = self.frame.grid_slaves()
        if not steps: return
        steps.sort(key=lambda s: s.grid_info()['row'])  # preserve grid order
        for step in steps:
            if step.grid_info()['row'] == this_row:
                break
            step.render(False)  # only update the values

    def update_below(self, step):
        steps = self.frame.grid_slaves()
        if not steps: return
        steps.sort(key=lambda s: s.grid_info()['row'])  # preserve grid order
        this_row = step.grid_info()['row'] if step else -1
        for step in steps:
            row = step.grid_info()['row']
            if row > this_row:
                step.render()

    def add_history(self, action, step, additional=None):
        if self.i_history != 'head':  # delete the old branch
            to_purge = self.history[self.i_history:]
            for event in to_purge:
                if event[0] == 'add':
                    event[1].destroy()   # it will never be added again
            self.history = self.history[:self.i_history]
            self.i_history = 'head'
        self.history.append([action, step, additional])

    def undo(self, event):
        len_history = len(self.history)
        i_history = len_history if self.i_history == 'head' else self.i_history
        if not len_history or i_history == 0:
            self.bell()
            return
        self.i_history = i_history - 1
        last = self.history[self.i_history]
        if last[0] == 'add':
            last[1].grid_remove()
            last[2].edit(None)
        elif last[0] == 'delete':
            last[2].render()
            self.recover(last[1])
            self.change_text(last[1], last[1].current_str)
            last[1].edit(None)
        elif last[0] == 'edit':
            # swap for redo
            last[2] = self.change_text(last[1], last[2])
            if last[1].grid_info()['row'] == 0:
                return
            last[1].render()
            self.update_below(last[1])

    def redo(self, event):
        if self.i_history == 'head':
            self.bell()
            return
        recent = self.history[self.i_history]
        if recent[0] == 'add':
            recent[2].render()
            self.recover(recent[1])
        elif recent[0] == 'delete':
            recent[1].grid_remove()
            recent[2].edit(None)
        elif recent[0] == 'edit':
            # for undo
            recent[2] = self.change_text(recent[1], recent[2])
            if recent[1].grid_info()['row'] != 0:
                recent[1].render()
                self.update_below(recent[1])
        else:
            return
        self.i_history += 1
        if self.i_history == len(self.history):
            self.i_history = 'head'

    def remove(self, step, neighbour=None):
        '''take the step to the graveyard'''
        if not isinstance(step, Step):  # is event
            step = step.widget.master
            neighbour = step.neighbour(-1)
            if not neighbour:
                neighbour = step.neighbour(1)
            if not neighbour:
                self.bell()
                return
        self.add_history('delete', step, neighbour)
        self.update_above(neighbour)
        step.grid_remove()  # to remember the grid data
        neighbour.edit(None)

    def recover(self, step):
        '''bring back removed steps from the dead'''
        step.grid()  # reuse grid data
        self.update_above(step)
        step.edit(None)

    def change_text(self, step, text):
        '''replace the input text in step with text'''
        current_txt = step.input.get()
        step.input.delete(0, 'end')
        step.input.insert(0, text)
        return current_txt


class Step(Frame):
    def __init__(self, master, grand_master):
        super().__init__(master, takefocus=0, style='WS.TFrame')
        self.master = grand_master
        self.grid_columnconfigure(0, weight=1)

        self.input = Entry(self)
        self.input_props = {
            'kind': 'math',  # or text
            'y': 0  # not always available, to be set at scroll_into_view, for autocomplete
        }
        self.output = Label(self, text='', background='white')
        self.output_props = {
            'kind': None,  # disp or inline or text or tag
        }
        self.exception = Label(self, foreground='red', font=(None, 8))

        self.input.bind('<Return>', self.on_return)
        self.input.bind('<BackSpace>', self.merge)
        self.input.bind('<Control-BackSpace>', self.master.remove)
        self.input.bind('<Delete>', self.merge)
        self.input.bind('<Control-Return>', self.split)
        self.input.bind('<Shift-Return>', self.split)
        self.input.bind('<Escape>', self.restore)
        self.input.bind('<Up>', self.edit_neighbour)
        self.input.bind('<Down>', self.edit_neighbour)
        self.input.bind('<FocusIn>', self.on_focus)
        self.input.bind('<Tab>', self.master.autocomplete.suggest)
        self.input.bind('<KeyRelease>', self.master.autocomplete.suggest)
        self.bind('<1>', self.edit)

        self.current_str = ''
        self.is_new = True # for undo

        self.change_displayed('init')
        self.input.focus()

    def change_displayed(self, kind='input'):
        if kind == 'input':
            self.output.grid_remove()
            self.input.grid()
            return
        if kind == 'init':
            self.input.grid(sticky='ew')
            self.output.grid(sticky='ew')
            self.output.grid_remove()
            return
        # output
        self.input.grid_remove()
        if self.output_props['kind'] != kind:
            self.output_props['kind'] = kind
            self.output.destroy()
            sticky = 'ew'
            if kind == 'disp':
                self.output = Canvas(self, background='white', highlightthickness=0)
                sticky = None
            elif kind == 'inline':
                self.output = Canvas(self, bg='white', highlightthickness=0)
            elif kind == 'text':
                width = self.master.winfo_width()
                self.output = Label(self, font=self.master.text_font, wraplength=width, background='white')
            else:  # tag
                self.output = Label(self, font=(None, 8), foreground='white', background='#37F')
            self.output.bind('<1>', self.edit)
            self.output.grid_configure(column=0, sticky=sticky)
        self.output.grid()

    def render_disp(self, math):
        self.output.delete('all')
        math.y = math.x = 5
        self.output.config(width=math.width + 10, height=math.height + 10)
        math.render(self.output)

    def render_inline(self, math):
        self.output.delete('all')
        self.output.config(width=math.width, height=math.height)
        math.render(self.output)

    def render_text(self, text):
        self.output.config(text=text, wraplength=self.master.winfo_width())

    def render_tag(self, tag):
        self.output.config(text=tag)

    def render(self, show=True):
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
        if not show:  # only update the data
            return True
        kind, content = returned[0][1][0], returned[0][1][1]
        self.change_displayed(kind)
        self.__getattribute__('render_' + kind)(content)
        return True

    def on_return(self, event):
        last_str = self.current_str  # before changing, for undo
        if not self.render():
            return
        if self.is_new:
            self.is_new = False
        else:
            self.master.add_history('edit', self, last_str) # for undo
        next_step = self.neighbour(1)
        if not next_step:  # means last
            self.master.add(self)
            return
        self.master.update_below(self)
        if next_step.input.winfo_ismapped():
            next_step.input.focus()
        elif not next_step.input.get().strip():
            next_step.edit(None)

    def remove_err_msg(self, event):
        self.exception.grid_remove()
        self.input.unbind('<Key>')

    def edit(self, event):
        if self.output.winfo_ismapped():
            self.change_displayed('input')
        self.input.focus()

    def edit_neighbour(self, event):
        direction = 1 if event.keysym == 'Down' else -1
        neighbour = self.neighbour(direction)
        if not neighbour:
            self.bell()
            return
        if not self.exception.winfo_ismapped():
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
            self.bell()
            return
        if event.keysym == 'BackSpace':
            cursor_idx = neighbour.input.index(insert_pos)
        current_content = self.input.get()
        neighbour.input.insert(insert_pos, current_content)
        neighbour.input.icursor(cursor_idx)
        self.master.remove(self, neighbour)

    def split(self, event):
        current_content = self.input.get()
        i_cursor = self.input.index('insert')
        self.input.delete(i_cursor, 'end')
        self.render()

        this_row = self.grid_info()['row']
        if not self.is_last():
            # make place for the new one
            for step in self.master.frame.grid_slaves(column=0):
                row = step.grid_info()['row']
                if row > this_row:
                    step.grid_configure(row=row+1)

        new = self.master.add(self)
        new.current_str = current_content[i_cursor:]
        new.input.insert(0, new.current_str)
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
        self.master.update_above(self)

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
            selected = self.selection_get().split('\u200B')[0]
        self.entry.delete(self.index_replace[0], self.index_replace[1])
        self.entry.insert(self.index_replace[0], selected)
        self.index_replace = self.index_replace[0], self.index_replace[0] + len(selected)

    def build_matches(self, trigger):
        '''build the completion list'''
        if not trigger.isidentifier(): return []
        len_trigger = len(trigger)
        matches, fillers = [], []  # fillers shown if len(matches) < limit
        space = self.master.processor.working_dict
        for key in space:
            if key.startswith(trigger) and not key.endswith(UNIT_PF):
                item = key
                value = space[key]
                if isinstance(value, float):
                    value = round(value, 5)
                if isinstance(value, (int, float)):
                    item += '\u200B=' + str(value)
                    if key + UNIT_PF in space:  # has unit
                        item += to_math(space[key + UNIT_PF],
                                        div='/',
                                        syntax=UnitSyntax(),
                                        ital=False)
                elif isinstance(value, list):
                    item += '\u200B=[mat]'
                elif callable(value):
                    try:
                        sig = str(signature(value)).replace(' ', '').replace(',/', '')
                    except ValueError:
                        sig = '(...)'
                    fillers.append(item + '\u200B' + sig)
                    continue
                matches.append(item)
        n_matches = len(matches)
        if n_matches < self.limit:
            matches += fillers[:self.limit - n_matches]
        return matches

    def show_matches(self, entry, coord_y):
        entry_cursor = entry.index('insert')
        current = entry.get()[:entry_cursor]
        match = self.pattern.search(current)
        if not match:
            self.place_forget()
            return
        self.trigger = match.group(0)
        matches = self.build_matches(self.trigger)
        if not matches:
            self.place_forget()
            return
        self.entry = entry
        self.index_replace = (entry_cursor - len(self.trigger), entry_cursor)
        self.listvar.set(' '.join(matches[:self.limit]))
        coord_x = entry.winfo_x() + round(self.font.measure(current[:self.index_replace[0]]) * 0.811) + self['borderwidth']
        self.place(x=coord_x, y=coord_y)
        self.select_next(0)
        self.config(height=self.size())
        self.len = self.size()

    def suggest(self, event):
        step = event.widget.master
        # varying states due to caps lock, num lock and shift changes
        no_mod = event.state in (0, 2, 8, 10)  # no special modifier
        shift = event.state in (1, 3, 9, 11)  # holding shift
        typing = (no_mod or shift) and (event.keysym in ('underscore', 'BackSpace')
                                      or len(event.keysym) == 1)
        if typing:
            step.scroll_into_view()  # recalculate the y
            self.show_matches(event.widget, step.input_props['y'])
            return
        if event.keysym == 'Tab':
            # prevent from firing twice
            if str(event.type) != 'KeyPress' or not self.winfo_ismapped():
                return
            direction = 1 if no_mod else -1 if shift else None
            if direction: self.select_next(direction)
            return 'break'
        elif event.keysym in ('Shift_L', 'Shift_R'):
            return
        self.place_forget()  # prevent visibility after render


class UnitSyntax:
    '''for units on completion'''
    halfsp = ''
    greek_letters = math_accents = primes = transformed = []

    def txt_rom(self, txt):
        return txt

    def txt(self, txt):
        return txt

    def sup(self, base, sup):
        return base + '^' + sup
