# - - - Выборочный парсер HTML - - - 

# В проекте существуют 2 группы глобальных переменных:
# pref_* - общие настройки и значения, par_* - параметры отображения по мере обработки документа

# To-do: теги, свойства текста, атрибуты, фильтровка по атрибутам, cookies, привести всё к чистому виду, pytest, документация

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
    print("Usage:\n", sys.argv[0], "\nor\n", sys.argv[0], "-u \"url\"\n", sys.argv[0], "-p \"path\"")
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
#фильтровать можно теги, атрибуты, значения атрибутов.
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
                mode = 0 if line == "#method:" else (1 if line == "#tags:" else (2 if line == "#attributes:" else None))
                continue
            if mode == 0:
                pref_incEx = True if line == "inclusive" else (False if line == "exclusive" else pref_incEx)
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
        #raise SystemExit

def get_file():
    global pref_file
    if pref_usingUrl:
        import urllib.request
        pref_file = urllib.request.urlopen(pref_path)
    else:
        pref_file = open(pref_path)

#tags:
#html head body title pre h1..h6 b i tt cite em font a p br blockquote dl dt dd ol li ul div img hr table tr td th noframes form select option textarea input

# - - - DISPLAY - - - 

def backToDefault():
    global pref_incEx, par_filtered, par_tags, par_attrs, par_cssProps
    par_filtered = pref_incEx
    par_tags = [] #what tags we are inside
    par_attrs = [] #what attrs are going with the tags, [dict, dict, ...]
    par_cssProps = {} #what css properties we use, {tag : {class : {prop : value}}}

def tagSep(tagAndAttrs):
    tag = tagAndAttrs.split(' ').pop(0)
    if tag[0] == '/':
        return tag[1:]
    return tag

def attrsSep(tagAndAttrs):
    attrs_list = tagAndAttrs.replace("="," = ").split()
    attrs_list.pop(0)
    attrs = {}
    parent = ""
    isParent = True
    for word in attrs_list:
        if word != "=":
            if isParent:
                if parent != "": attrs[parent] = None
                parent = word
            else:
                attrs[parent] = word
                parent = ""
                isParent = True
        else:
            isParent = False
    return attrs

#getting tag functions for gui or text
if pref_guiMode:
    from module_guiMode import *
else:
    from module_textMode import *

#replacing special symbols
def replaceSpecSyms(text):
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

string = ""
def textProcess(text):
    global string
    if not pref_filterEnabled or not par_filtered:
        if "body" in par_tags and not "style" in par_tags and not "script" in par_tags:
            text = replaceSpecSyms(text)
            if pref_guiMode:
                string += text
            else:
                print(text, end = "")

def tagProcess(tagAndAttrs):
    global pref_singleTags, pref_filterEnabled, pref_incEx, pref_fltTags, par_tags, par_attrs, par_filtered
    tag = tagSep(tagAndAttrs)
    attrs = attrsSep(tagAndAttrs)
    isClosing = True if tagAndAttrs[0] == '/' else False
    #tag stack
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
    #filtering
    if not tag in pref_singleTags:
        singleFiltered = False 
        if pref_filterEnabled:
            par_filtered = False
            if pref_incEx:
                for el in par_tags:
                    if not el in pref_fltTags:
                        par_filtered = True
            else:
                for el in par_tags:
                    if el in pref_fltTags:
                        par_filtered = True
    else:
        if pref_incEx:
            singleFiltered = pref_filterEnabled and not tag in pref_fltTags
        else:
            singleFiltered = pref_filterEnabled and tag in pref_fltTags
    if not par_filtered and not singleFiltered:
        if tag in globals():
            globals()[tag](attrs, isClosing)

# - - - PARSER - - - 

def parse_css():
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
    backToDefault()
    if pref_path:
        get_file()
        parse_html()
        pref_file.close()

run()

if pref_guiMode:
    from module_gui import *
