# - - - Выборочный парсер HTML - - - 

# В проекте существуют 2 группы глобальных переменных:
# pref_* - общие настройки и значения, par_* - параметры отображения по мере обработки документа

# To-do: теги, свойства текста, cookies, pytest

# - - - PREFERENCES - - - 

pref_encoding = "utf8"
pref_guiMode = True
pref_replaceSpecSymsEnabled = True
pref_filterEnabled = False
pref_incEx = False #T - inclusive, F - exclusive
pref_singleTags = {"br", "hr", "img"} #tags without </tag>

#getting prefs from bash
import sys

def err_usage():
    """Prints the error message in stdout and raises SystemExit if the program
     was called with bad arguments.
    
    :raises SystemExit:"""
    
    print("Usage:\n", sys.argv[0], "\nor\n", sys.argv[0], "-u \"url\"\n", 
        sys.argv[0], "-p \"path\"")
    raise SystemExit

pref_usingUrl = True
pref_bashPrefs = pref_path = ""
#if len(sys.argv) == 1: pass
if len(sys.argv) == 2: err_usage()

if len(sys.argv) > 2:
    for word in sys.argv[1:]:
        if word[0] == "-": pref_bashPrefs += word[1:]
        else: pref_path = word
    
    if not "u" in pref_bashPrefs and not "p" in pref_bashPrefs: err_usage()
    if "u" in pref_bashPrefs: pref_usingUrl = True
    if "p" in pref_bashPrefs: pref_usingUrl = False
    if "t" in pref_bashPrefs: pref_guiMode = False
    if "f" in pref_bashPrefs: pref_filterEnabled = True
    if "i" in pref_bashPrefs: pref_incEx = True
    if "e" in pref_bashPrefs: pref_incEx = False

#special symbols
if pref_replaceSpecSymsEnabled:
    try:
        pref_specSymsFile = open("specSyms.txt")
        temp = pref_specSymsFile.read().replace("\n", " ").split(" ")
        pref_specSyms = dict(zip(temp[::2], [int(i) for i in temp[1::2]]))
        temp = None
        pref_specSymsFile.close()
    except:
        print("specSyms.txt file not found! Disabling replacing...\n")
        pref_replaceSpecSymsEnabled = False

#filtered attributes
pref_fltTags = set()
pref_fltAttrs = {}

if pref_filterEnabled:
    try:
        temp = temp2 = mode = None
        pref_filterFile = open("filter.txt")
        temp = pref_filterFile.read().split("\n")
        for line in temp:
            if line == "": continue
            if line[0] == "#":
                if line == "#method:": mode = 0
                elif line == "#tags:": mode = 1
                elif line == "#attributes:": mode = 2
                else: mode = None
                continue
            if mode == 0:
                if line == "inclusive": pref_incEx = True
                elif line == "exclusive": pref_incEx = False
            elif mode == 1:
                pref_fltTags.update(line.split())
            elif mode == 2:
                temp2 = line.split()
                if temp2[0][-1] == ":":
                    pref_fltAttrs[temp2[0][:-1]] = temp2[1:]
        pref_filterFile.close()
        temp = temp2 = mode = None
    except:
        print("filter.txt file not found! Disabling filter...\n")
        pref_filterEnabled = False

def get_file():
    """Gets the file in pref_file by the url or the path stored in pref_path. 
    Depends on pref_usingUrl in using the url or the local path."""
    
    global pref_usingUrl, pref_path, pref_file
    if pref_usingUrl:
        import urllib.request
        pref_file = urllib.request.urlopen(pref_path)
    else:
        pref_file = open(pref_path)


# - - - DISPLAY - - - 

def backToDefault():
    """Returns the global variables that can change to their initial values."""
    
    global pref_incEx, par_filtered, par_tags, par_attrs, par_cssProps
    par_filtered = pref_incEx
    par_tags = [] #what tags we are inside
    par_attrs = [] #what attrs are going with the tags, [dict, dict, ...]
    par_cssProps = {} #what css props we use, {tag : {class : {prop : value}}}

def tagSep(tagAndAttrs):
    """Separates html-tag from the string with tag and attributes
    and returns it.
    
    :param tagAndAttrs: str with tag and attributes
    :type tagAndAttrs: str
    :returns: tag
    :rtype: str"""
    
    if not tagAndAttrs or not isinstance(tagAndAttrs, str):
        return ""
    tag = tagAndAttrs.split().pop(0)
    if tag[0] == '/':
        return tag[1:]
    return tag

def attrsSep(tagAndAttrs):
    """Separates attributes from the string with tag and attributes
    and returns it.
    
    :param tagAndAttrs: str with tag and attributes
    :type tagAndAttrs: str
    :returns: attributes
    :rtype: dict"""
    
    if not tagAndAttrs or not isinstance(tagAndAttrs, str):
        return ""
    attrs_list = tagAndAttrs.replace("="," = ").split()
    attrs_list.pop(0)
    attrs = {}
    parent = ""
    isParent = True
    for word in attrs_list:
        if word != "=":
            if isParent:
                if parent != "": attrs[parent] = ""
                parent = word
            else:
                attrs[parent] = word
                parent = ""
                isParent = True
        else:
            isParent = False
    if parent != "": attrs[parent] = ""
    return attrs

#getting tag functions for gui or text
if pref_guiMode:
    from module_guiMode import *
else:
    from module_textMode import *

def replaceSpecSyms(text):
    """Replaces the special symbols such as &nbsp; in a given text
    and returns the output.
    
    :param text: initial text
    :type text: str
    :returns: text with special symbols replaced
    :rtype: str"""
    
    if not isinstance(text, str):
        return text
    global pref_specSyms
    if not pref_specSyms or text == "": return text
    output = sym = ""
    isCode = isSym = wasSym = wasAmp = False
    for c in text:
        if c == "&":
            if isSym: output += "&"
            wasAmp = isSym = True
            output += sym
            sym = ""
            continue
        if wasSym:
            wasSym = False
            if c == ";": continue
        if wasAmp:
            wasAmp = False
            if c == "#":
                isCode = True
                continue
        if isCode:
            if c.isdigit(): sym += c
            else:
                if sym != "":
                    output += chr(int(sym))
                    sym = ""
                    wasSym = True
                isCode = isSym = False
        else:
            sym += c
            if sym in pref_specSyms:
                output += chr(pref_specSyms.get(sym))
                sym = ""
                wasSym = True
                isSym = False
    if isSym: output += "&" 
    output += sym
    return output

def tagStack(tag, attrs, isClosing):
    """Adds the given tag to the list par_tags if isClosing == False.
    If isClosing == True, removes all the tags from the end to the first tag
    that the same as given. If there's no such tag in par_tags
    and isClosing == True, does nothing. attrs variable goes together with
    tag and interacts with par_attrs list.
    
    :param tag: given tag
    :type tag: str
    :param attrs: given attributes
    :type attrs: dict
    :param isClosing: is the tag closing or not
    :type isClosing: bool"""
    
    global pref_singleTags, par_tags, par_attrs
    if not tag in pref_singleTags:
        if not isClosing:
            par_tags.append(tag)
            par_attrs.append(attrs)
        else:
            for i in range(len(par_tags) - 1, -1, -1):
                if par_tags[i] == tag:
                    par_tags = par_tags[:i]
                    par_attrs = par_attrs[:i]
                    break

def checkFilter(tag, attrs):
    """Checks if the tag and attrs are in those that are filtered.
    If inclusive filtering is preferred (pref_incEx == True), the blocks with
    tags and attrs that are only in filter are shown; if exclusive filtering
    is preferred (pref_incEx == False), the blocks with tags and attrs
    that are only not in filter are shown. If some block should not be
    shown, par_filtered == True
    
    :param tag: given tag
    :type tag: str
    :param attrs: given attributes
    :type attrs: dict"""
    
    global pref_singleTags, pref_fltTags, pref_fltAttrs, pref_incEx, par_tags, par_attrs, par_filtered
    if not tag in pref_singleTags:
        singleFiltered = False 
        par_filtered = False
        if pref_incEx:
            for el in range(len(par_tags)):
                if not par_tags[el] in pref_fltTags: 
                    par_filtered = True
                    break
                for attr in par_attrs[el]:
                    if not attr in pref_fltAttrs: 
                        par_filtered = True
                        break
                    if not par_attrs[el][attr] in pref_fltAttrs[attr]:
                        par_filtered = True
                        break
        else:
            for el in range(len(par_tags)):
                if par_tags[el] in pref_fltTags:
                    par_filtered = True
                    break
                for attr in par_attrs[el]:
                    if par_attrs[el][attr] in pref_fltAttrs[attr]:
                        par_filtered = True
                        break
                    if attr in pref_fltAttrs: 
                        par_filtered = True
                        break
    else:
        if pref_incEx: singleFiltered = not tag in pref_fltTags
        else: singleFiltered = tag in pref_fltTags
    return singleFiltered

string = ""
def textProcess(text):
    """Sends the given text to some output, stdout or GUI depending on
    pref_guiMode. Follows the filtering.
    
    :param text: given text
    :type text: str"""
    
    global string
    if not pref_filterEnabled or not par_filtered:
        if "body" in par_tags and not "style" in par_tags and not "script" in par_tags:
            text = replaceSpecSyms(text)
            if pref_guiMode:
                string += text
            else:
                print(text, end = "")

def tagProcess(tagAndAttrs):
    """Processes a raw tag-and-attributes str splitting it in tag as an str
    and attributes as a dict, calls tagStack function to manage tag location
    in the document, calls checkFilter if pref_filterEnabled == True and
    calls the function with the same name as a tag if it exists.
    
    :param tagAndAttrs: tag and attributes in one str
    :type tagAndAttrs: str"""
    
    global pref_filterEnabled, par_filtered
    tag = tagSep(tagAndAttrs)
    attrs = attrsSep(tagAndAttrs)
    isClosing = True if tagAndAttrs[0] == '/' else False
    
    tagStack(tag, attrs, isClosing)
    if pref_filterEnabled: singleFiltered = checkFilter(tag, attrs)
    
    if not par_filtered and not singleFiltered:
        if tag in globals():
            globals()[tag](attrs, isClosing)

# - - - PARSER - - - 

def parse_css():
    """Parses CSS code from the pref_file variable and stores the CSS
    properties in par_cssProps."""
    
    global pref_file, pref_usingUrl, pref_encoding, par_cssProps
    insideBlock = isCl = False
    tags = []
    classes = []
    tag = cl = prop = value = ""
    propOrVal = True # T - property, F - value
    skipSymbols = ['@', ':', '#', '[', ']', '^', '>', '~', '+'] #неподдерживаемые символы
    skip = False #пропускаем неподдерживаемые символы
    
    rawLine = pref_file.readline()
    if pref_usingUrl: rawLine = rawLine.decode(pref_encoding)
    while rawLine:
        for c in rawLine.replace(" ", "").replace("\n", "").replace("\t", ""):
            if c == '{':
                if isCl: 
                    if cl: classes.append(cl)
                else:
                    if tag: tags.append(tag)
                tag = cl = ""
                if tags == []: tags = ["*"]
                if classes == []: classes = ["*"]
                insideBlock = propOrVal = True
                isCl = False
                continue
            if c == '}':
                if prop:
                    for tag in tags:
                        if not tag in par_cssProps:
                            par_cssProps[tag] = {}
                        for cl in classes:
                            if not cl in par_cssProps[tag]:
                                par_cssProps[tag][cl] = {}
                            par_cssProps[tag][cl][prop] = value
                insideBlock = False
                propOrVal = True
                tags = []
                classes = []
                tag = cl = prop = value = ""
                skip = False
                continue
            if skip: continue
            if insideBlock:
                if c == ':':
                    propOrVal = False
                    continue
                if c == ';':
                    propOrVal = True
                    if prop:
                        for tag in tags:
                            if not tag in par_cssProps:
                                par_cssProps[tag] = {}
                            for cl in classes:
                                if not cl in par_cssProps[tag]:
                                    par_cssProps[tag][cl] = {}
                                par_cssProps[tag][cl][prop] = value
                    prop = value = ""
                    continue
                if propOrVal: prop += c
                else: value += c
            else:
                if c in skipSymbols:
                    skip = True
                    continue
                if c == '.':
                    if tag: tags.append(tag)
                    tag = ""
                    isCl = True
                    continue
                if c == ',':
                    if isCl:
                        if cl: classes.append(cl)
                        cl = ""
                    else:
                        if tag: tags.append(tag)
                        tag = ""
                    continue
                if isCl: cl += c
                else: tag += c
        rawLine = pref_file.readline()
        if pref_usingUrl: rawLine = rawLine.decode(pref_encoding)

def parse_html():
    """Parses the HTML file and calls tagProcess if it went inside <>,
    or textProcess if it is outside of <>."""
    
    global pref_usingUrl, pref_file, pref_encoding
    tagAndAttrs = ""
    text = ""
    isTag = False
    
    rawLine = pref_file.readline()
    if pref_usingUrl: rawLine = rawLine.decode(pref_encoding)
    while rawLine:
        for c in rawLine:
            if c == '<':
                textProcess(" ".join(text.replace("\n","").split()))
                text = ""
                isTag = True
                continue
            elif not isTag:
                text += c
                continue
            if isTag:
                if c != '>':
                    tagAndAttrs += c
                    continue
                else:
                    isTag = False
                    if len(tagAndAttrs) > 0:
                        tagProcess(tagAndAttrs.lower())
                    tagAndAttrs = ""
                    continue
        rawLine = pref_file.readline()
        if pref_usingUrl: rawLine = rawLine.decode(pref_encoding)


# - - - Actual program - - - 
def run():
    """Calls all the needed functions to process the document:
    reset the variables that can change, load, parse and close the file."""
    
    backToDefault()
    if pref_path:
        get_file()
        parse_html()
        pref_file.close()

run()

#if pref_guiMode:
    #from module_gui import *
