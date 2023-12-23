import __main__ as m

def body(attrs, isClosing):
    """A function that processes body tag.
    
    :param attrs: attributes
    :type attrs: dict
    :param isClosing: is the tag closing or not
    :type isClosing: bool"""
    
    if not isClosing:
        m.gui.setBody()

def link(attrs, isClosing):
    """A function that processes link tag.
    
    :param attrs: attributes
    :type attrs: dict
    :param isClosing: is the tag closing or not
    :type isClosing: bool"""
    
    if "rel" in attrs and "href" in attrs:
        if attrs["rel"] == "stylesheet":
            path = m.getAbsPath(attrs["href"])
            m.parse_css(m.get_file(path, True, False), m.par_cssProps)

def br(attrs, isClosing):
    """A function that processes br tag.
    
    :param attrs: attributes
    :type attrs: dict
    :param isClosing: is the tag closing or not
    :type isClosing: bool"""
    
    m.textProcess("\n")

def span(attrs, isClosing):
    """A function that processes span tag.
    
    :param attrs: attributes
    :type attrs: dict
    :param isClosing: is the tag closing or not
    :type isClosing: bool"""
    
    m.textProcess("\n")

def a(attrs, isClosing):
    """A function that processes a tag.
    
    :param attrs: attributes
    :type attrs: dict
    :param isClosing: is the tag closing or not
    :type isClosing: bool"""
    
    m.textProcess("\n")

def b(attrs, isClosing):
    """A function that processes b tag.
    
    :param attrs: attributes
    :type attrs: dict
    :param isClosing: is the tag closing or not
    :type isClosing: bool"""
    
    m.textProcess("\n")

def button(attrs, isClosing):
    """A function that processes button tag.
    
    :param attrs: attributes
    :type attrs: dict
    :param isClosing: is the tag closing or not
    :type isClosing: bool"""
    
    m.textProcess("\n")

def base(attrs, isClosing):
    """A function that processes base tag.
    
    :param attrs: attributes
    :type attrs: dict
    :param isClosing: is the tag closing or not
    :type isClosing: bool"""
    
    global pathOrig
    if "href" in attrs:
        pathOrig = attrs["href"][1:-1]

def img(attrs, isClosing):
    """A function that processes img tag.
    
    :param attrs: attributes
    :type attrs: dict
    :param isClosing: is the tag closing or not
    :type isClosing: bool"""
    
    path = m.getAbsPath(attrs["src"])
    try:
        tmpFile = m.get_file(path, True, True)
        m.gui.showImg(tmpFile)
    except:
        pass

def font(attrs, isClosing):
    """A function that processes font tag.
    
    :param attrs: attributes
    :type attrs: dict
    :param isClosing: is the tag closing or not
    :type isClosing: bool"""
    
    if not isClosing:
        if "size" in attrs: m.par_fontSize = attrs["size"]
        if "color" in attrs: m.par_fontColor = attrs["color"]
        if "face" in attrs: m.par_fontFace = attrs["face"]
