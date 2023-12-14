import __main__ as m

def html(attrs, isClosing):
    m.backToDefault()

def head(attrs, isClosing):
	#global m.par_headOrBody
	m.par_headOrBody = 0 if isClosing else 1

def body(attrs, isClosing):
	#global m.par_headOrBody
	m.par_headOrBody = 0 if isClosing else 2

#def br(attrs, isClosing):
#	m.textProcess("\n")

def span(attrs, isClosing):
	m.textProcess("\n")

def a(attrs, isClosing):
	m.textProcess("\n")

def b(attrs, isClosing):
        m.textProcess("\n")

def button(attrs, isClosing):
        m.textProcess("\n")

def style(attrs, isClosing):
	#global m.par_inStyle
	m.par_inStyle = not isClosing

def script(attrs, isClosing):
    #global m.par_inScript
    m.par_inScript = not isClosing