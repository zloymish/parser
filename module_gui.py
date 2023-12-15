from tkinter import *
from tkinter import ttk

import __main__ as m

window = Tk()
window.title("Website")
#window.geometry('350x200')

toolbar = Frame(window, width = 100, height = 200)
toolbar.pack(anchor="nw")

button_rel = Button(toolbar, text='R')
button_rel.grid(column=0, row=0)

def reply(puk):
	m.pref_path = puk
	m.get_file()
	m.string = ""
	m.parse_html()
	x.config(text = m.string)

urlBox = Entry(toolbar, textvariable="url")
urlBox.bind("<Return>", (lambda event: reply(urlBox.get())))
urlBox.grid(column=1, row=0)

container = Frame(window, background = "white")
container.pack(anchor="nw")
canvas = Canvas(container, background = "white", width = 1280, height = 720)
scrollbar = Scrollbar(container, orient="vertical", command=canvas.yview)
scrollable_frame = Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

canvas.configure(yscrollcommand=scrollbar.set)

x=Label(scrollable_frame, text="Sample scrolling label\n\n\n\n\n\n\n\naaa", background = "white", justify = LEFT)
x.grid(column=0, row=0)

i = 0
for c in range(len(m.string)):
	if m.string[c] == '\n':
		i = 0
	else:
		i += 1
	if i > 50:
		i = 0
		m.string = m.string[:i] + '\n' + m.string[i:]

x.config(text = m.string)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

window.mainloop()
