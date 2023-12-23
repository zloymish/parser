from tkinter import *
from tkinter import ttk, font
from PIL import Image, ImageTk

import __main__ as m

col_bg = "#18191d"
col_light = "#7d8084"
col_dark = "#3e4348"
col_form = "#3d444b"

window = Tk()
window.title("Website")
def setTitle(title):
    """Sets the title of the window.
    
    :param title: title
    :type title: str"""
    window.title(title)

window.geometry('1280x720')
window.configure(background=col_bg)

toolbar = Frame(window, width = 100, height = 200, background=col_bg)
toolbar.pack(anchor="nw")

def reply(url):
    """Sends url to the main module and loads the new page.
    
    :param url: url
    :type url: str"""
    global l
    m.pref_path = url
    if l:
        for el in l:
            el.grid_forget()
    l = []
    m.run()

urlBox = Entry(toolbar, background=col_form, bd=0, borderwidth=0, 
    textvariable="url")
urlBox.bind("<Return>", (lambda event: reply(urlBox.get())))
urlBox.grid(column=1, row=0)

style = ttk.Style()
style.theme_use('classic')
style.configure("Vertical.TScrollbar", troughcolor='#7d8084', 
    background="#7d8084", bordercolor="black", arrowcolor="#3e4348")

bg = "white"

def setBody():
    """Sets the background and other settings that are related to body."""
    
    global bg
    background = setBg()
    if background: bg = background
    try:
        canvas.configure(background = bg)
        scrollable_frame.configure(background = bg)
    except: bg = "white"

# container {canvas {scrollable_frame {labels}}, scrollbar}
container = Frame(window, width = 800, height = 600, background = "white")
container.pack(anchor="nw") #wh не влияет
canvas = Canvas(container, background = bg)
scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
scrollable_frame = Frame(canvas, background = bg) 
def resize(self):
    """Resizes the window.
    
    :param self: the parent
    :type self: object"""
    
    container.configure(width = window.winfo_width(), 
        height = window.winfo_height())
    canvas.configure(width = container.winfo_width() - 20, 
        height = container.winfo_height())
    scrollable_frame = Frame(canvas, background = bg, 
        width = container.winfo_width() - 20, 
        height = container.winfo_height())
    canvas.configure(scrollregion=canvas.bbox("all"))

window.bind("<Configure>",resize)

scrollable_frame.pack(fill = "both")

canvas.configure(scrollregion=canvas.bbox("all"),
    yscrollcommand=scrollbar.set)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

def setFont():
    """Sets the font.
    
    :returns: font
    :rtype: tkinter.font.Font"""
    family = "Serif"
    size = 10
    weight = "normal"
    slant = "roman"
    underline = False
    overstrike = False
    
    if "a" in m.par_tags: underline = True
    
    if "b" in m.par_tags or "strong" in m.par_tags or "th" in m.par_tags:
        weight = "bold"
    if "i" in m.par_tags or "em" in m.par_tags: slant = "italic"
    if "u" in m.par_tags or "ins" in m.par_tags: underline = True
    if "s" in m.par_tags or "strike" in m.par_tags: overstrike = True
    
    #if m.par_fontSize: 
    if m.par_fontFace: fontFamily = m.par_fontFace
    
    fontFamily = m.closestCssVal("font-family")
    if fontFamily:
        family = fontFamily.split()[0]
    fontWeight = m.closestCssVal("font-weight")
    if fontWeight == "bold": weight = "bold"
    elif fontWeight == "normal": weight = "normal"
    fontStyle = m.closestCssVal("font-style")
    if fontStyle == "italic" or fontStyle == "oblique": slant = "italic"
    elif fontStyle == "normal": slant = "roman"
    decoration = m.closestCssVal("text-decoration")
    if decoration == "underline": underline = True
    elif decoration == "line-through": overstrike = True
    elif decoration == "none": underline = overstrike = False
    
    return font.Font(
        family = family, size = size, weight = weight,
        slant = slant, underline = underline, overstrike = overstrike
    )

def setFg():
    """Sets foreground.
    
    :returns: color
    :rtype: str"""
    
    color = m.closestCssVal("color")
    if color: return color
    return ""

def setBg():
    """Sets background.
    
    :returns: color
    :rtype: str"""
    
    background = m.closestCssVal("background-color")
    if not background: background = m.closestCssVal("background")
    if not background: background = m.closestAttr("bgcolor")
    if background: return background
    return ""

def position():
    """Sets position."""
    
    global row, column
    display = m.closestCssVal("display")
    if "inline" in display:
        column += 1
    else:
        column = 0
        row += 1
    if "tr" in m.par_tags:
        if m.par_tags.count("td") < 2:
            column = 0
            row += 1
        else: column += 1

l = []
row = column = 0
def show(text):
    """Shows the text as label.
    
    :param text: text
    :type text: str"""
    
    if not text: return
    global row, column
    position()
    if text == '\n':
        row += 1
        clolumn = 0
        return
    align = "wn"
    if "center" in m.par_tags: align = ""
    if m.closestCssVal("justify-content") == "center"\
        or m.closestCssVal("text-align"):
        align = ""
    
    bg = "white"
    background = setBg()
    if background: bg = background
    if not "a" in m.par_tags:
        fg = "black"
        if m.par_fontColor: fg = m.par_fontColor
        color = setFg()
        if color: fg = color
    else:
        fg = "#0000FF"
        if "class" in m.par_attrs[-1]:
            cls = m.par_attrs[-1]["class"].split()
            for cl in range(len(cls) - 1, -1, -1):
                color = m.findCssVal(m.par_tags[-1], cl, "color")
                if color:
                    fg = color
                    break
    try:
        if column == 0: l.append(Frame(scrollable_frame, bg = bg))
        if len(l) > 0: lab = Label(
            l[-1], text="text", font=setFont(), fg = fg, bg = bg,
            justify = LEFT
        )
    except:
        fg = "black"
        bg = "white"
        if column == 0: l.append(Frame(scrollable_frame, bg = bg))
        if len(l) > 0: lab = Label(l[-1], text="text", font=setFont(),
            fg = fg, bg = bg, justify = LEFT)
    if len(l) > 0: lab.config(text = text)
    if len(l) > 0: lab.grid(row = 0, column = column, sticky = "wn")
    if len(l) > 0: 
        if column == 0: l[-1].grid(row = row, column = 0, sticky = align)

def showImg(img):
    """Shows the image.
    
    :param img: file with image
    :type img: file"""
    
    global row, column
    
    import os
    image = ImageTk.PhotoImage(Image.open(img.name))
    l.append(
    Label(scrollable_frame, image = image, justify = LEFT))
    l[-1].image = image
    l[-1].grid(row = row, column = column, sticky = "wn")

def runGui():
    """Runs the gui."""
    
    canvas.pack(side=LEFT, fill = "both")
    scrollbar.pack(side=RIGHT, fill = "y")
    
    window.mainloop()
