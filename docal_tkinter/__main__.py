# -{cd .. | python -m docal_tkinter d:\documents\medi.dcl}
from docal_tkinter.app import App
from sys import argv

# app
app = App()

if len(argv) > 1:
    app.after_idle(app.after, 300, app.menu.file_menu.open, argv[1])

app.mainloop()
