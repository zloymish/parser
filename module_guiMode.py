import __main__ as m

#tags:
#html head body title pre h1..h6 b i tt cite em font a p br blockquote dl dt dd ol li ul div img hr table tr td th noframes form select option textarea input

def html(attrs, isClosing):
    m.backToDefault()

def head(attrs, isClosing):
	m.par_headOrBody = 0 if isClosing else 1

def body(attrs, isClosing):
	m.par_headOrBody = 0 if isClosing else 2

def br(attrs, isClosing):
	m.textProcess("\n")

def span(attrs, isClosing):
	m.textProcess("\n")

def a(attrs, isClosing):
	m.textProcess("\n")

def b(attrs, isClosing):
    m.textProcess("\n")

def button(attrs, isClosing):
    m.textProcess("\n")

def style(attrs, isClosing):
	m.par_inStyle = not isClosing

def script(attrs, isClosing):
    m.par_inScript = not isClosing
