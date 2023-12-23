# - - - Выборочный парсер HTML - - - 

# В проекте есть 2 группы глобальных переменных:
# pref_* - общие настройки и значения, par_* - параметры отображения по мере обработки документа

# - - - PREFERENCES - - - 

pref_encoding = "utf8"
pref_guiMode = True
pref_replaceSpecSymsEnabled = True
pref_filterEnabled = False
pref_incEx = False #T - inclusive, F - exclusive
pref_singleTags = {"area", "base", "br", "col", "command", "embed", "hr", "img", "input", "keygen", "link", "meta", "param", "source", "track", "wbr"} #tags without </tag>

#getting prefs from bash
import sys
sys.path.append("./modules")

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

def strToFile(text):
    """Writes the given str to file and returns it.
    
    :param text: given str
    :type text: str
    :returns: file with the str
    :rtype: file"""
    
    with open(".tmp", "w") as tmpFile:
        tmpFile.write(text)
    return open(".tmp")

def get_file(path, isUrl, isBin):
    """Returns the file by the url or the path stored in variable path. 
    Depends on isUrl in using the url or the local path. If isBin == True,
    creates a binary file.
    
    :param path: path of the file
    :type path: str
    :param isUrl: is it the URL or the local path 
    :type isUrl: bool
    :param isBin: make the file binary or standard
    :type isBin: bool
    :returns: file
    :rtype: file"""
    
    if isUrl:
        import requests
        if isBin:
            with open(".tmp", "wb") as tmpFile:
                tmpFile.write(requests.get(path).content)
            return open(".tmp", "rb")
        else: return strToFile(requests.get(path).text)
    else:
        settings = "rb" if isBin else "r"
        return open(path, settings)

# - - - DISPLAYING - - - 

def backToDefault():
    """Returns the global variables that can change to their initial values."""
    
    global pref_path, pref_incEx, par_pathOrig, par_filtered, par_tags
    global par_attrs, par_cssProps, par_fontSize, par_fontColor
    global par_fontFace
    par_pathOrig = pref_path
    par_filtered = pref_incEx
    par_tags = [] #what tags we are inside
    par_attrs = [] #what attrs are going with the tags, [dict, dict, ...]
    par_cssProps = {} #what css props we use, {tag : {class : {prop : value}}}
    
    par_fontSize = par_fontColor = par_fontFace = "" #used only for 
    #html tag <font>, not css fonts

def getAbsPath(path):
    """Returns absolute path.
    
    :param path: local or absolute path
    :type path: str
    :returns: absolute path
    :rtype: str"""
    
    global par_pathOrig
    if not par_pathOrig or not path: return path
    if not "http" in path and path[0:2] != "//":
        if par_pathOrig[-1] == "/" and path[0] == "/": path = path[1:]
        elif par_pathOrig[-1] != "/" and path[0] != "/": path = "/" + path
        path = par_pathOrig + path
    elif path[0:2] == "//":
        path = "https:" + path
    print(path)
    return path

def closestAttr(attr):
    """Returns the closest attribute value in par_attrs.
    
    :param attr: attribute
    :type attr: str
    :returns: attribute value
    :rtype: str"""
    
    global par_attrs
    for num in range(len(par_attrs) - 1, -1, -1):
        if attr in par_attrs[num]:
            return par_attrs[num][attr]
    return ""

def findCssVal(tag, cl, prop):
    """Returns the css value if it exists.
    
    :param tag: tag
    :type tag: str
    :param cl: class
    :type cl: str
    :param prop: property
    :type prop: str
    :returns: value
    :rtype: str"""
    
    global par_cssProps
    if tag in par_cssProps:
        if cl in par_cssProps[tag]:
            if prop in par_cssProps[tag][cl]:
                return par_cssProps[tag][cl][prop]
    return ""

def closestCssVal(prop):
    """Returns the closest css value by property.
    
    :param prop: property
    :type prop: str
    :returns: value
    :rtype: str"""
    
    #приоритеты: attr -> id -> class -> tag
    global par_tags, par_attrs
    if not par_attrs or not par_tags: return ""
    if "style" in par_attrs[-1]:
        style = "*{" + par_attrs[-1]["style"] + "}"
        localCssDict = {}
        parse_css(strToFile(style), localCssDict)
        if "*" in localCssDict:
            if "*" in localCssDict["*"]:
                if prop in localCssDict["*"]["*"]:
                    return localCssDict["*"]["*"][prop]
    for num in range(len(par_tags) - 1, -1, -1):
        tag = par_tags[num]
        iden = ""
        if "id" in par_attrs[num]: iden = par_attrs[num]["id"]
        if iden:
            val = findCssVal("*", iden, prop)
            if val: return val
        if "class" in par_attrs[num]: cls = par_attrs[num]["class"].split()
        else: cls = []
        #смотрим классы
        for cl in range(len(cls) - 1, -1, -1):
            val = findCssVal("*", cls[cl], prop)
            if not val: val = findCssVal(tag, cls[cl], prop)
            if val: return val
        #смотрим теги
        val = findCssVal(tag, "*", prop)
        if val: return val
    return ""

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
                attrs[parent] = word[1:-1] #removing quots
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
    print(par_tags)
    #print(par_attrs)

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
    
    global pref_singleTags, pref_fltTags, pref_fltAttrs, pref_incEx, par_tags
    global par_attrs, par_filtered
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

def initGui():
    """Inits the module with graphical interface."""
    
    global gui
    import module_gui as gui

def textProcess(text):
    """Sends the given text to some output, stdout or GUI depending on
    pref_guiMode. Follows the filtering.
    
    :param text: given text
    :type text: str"""
    
    if not pref_filterEnabled or not par_filtered:
        if "body" in par_tags and not "style" in par_tags\
            and not "script" in par_tags:
            text = replaceSpecSyms(text)
            if pref_guiMode: gui.show(text)
            else: print(text, end = "")
        elif "style" in par_tags:
            parse_css(strToFile(text), par_cssProps)
        elif "title" in par_tags:
            if pref_guiMode: gui.setTitle(text)
            else: print("Visiting \"", text, "\"", sep = "")

def tagProcess(tagAndAttrs):
    """Processes a raw tag-and-attributes str splitting it in tag as an str
    and attributes as a dict, calls tagStack function to manage tag location
    in the document, calls checkFilter if pref_filterEnabled == True and
    calls the function with the same name as a tag if it exists.
    
    :param tagAndAttrs: tag and attributes in one str
    :type tagAndAttrs: str"""
    
    if tagAndAttrs[0] == "!": return
    
    global pref_filterEnabled, par_filtered
    tag = tagSep(tagAndAttrs)
    attrs = attrsSep(tagAndAttrs)
    isClosing = True if tagAndAttrs[0] == '/' else False
    
    tagStack(tag, attrs, isClosing)
    singleFiltered = False
    if pref_filterEnabled: singleFiltered = checkFilter(tag, attrs)
    
    if not par_filtered and not singleFiltered:
        if tag in globals():
            globals()[tag](attrs, isClosing)

# - - - PARSER - - - 

def parse_css(sourceFile, cssDict):
    """Parses CSS code from the given file and stores the CSS
    properties in cssDict.
    
    :param sourceFile: given file
    :type sourceFile: file
    :param cssDict: dict the properties are stored in
    :type cssDict: dict"""
    
    global pref_usingUrl, pref_encoding
    insideBlock = isCl = False
    tags = []
    classes = []
    tag = cl = prop = value = ""
    propOrVal = True # T - property, F - value
    #неподдерживаемые символы
    skipSymbols = ['@', ':', '#', '[', ']', '^', '>', '~', '+']
    skip = False #пропускаем неподдерживаемые символы
    
    rawLine = sourceFile.readline()
    #if pref_usingUrl: rawLine = rawLine.decode(pref_encoding)
    while rawLine:
        for c in rawLine.replace("\n", "").replace("#", "."):
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
                        if not tag in cssDict:
                            cssDict[tag] = {}
                        for cl in classes:
                            if not cl in cssDict[tag]:
                                cssDict[tag][cl] = {}
                            cssDict[tag][cl][prop] = value
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
                    prop = prop.replace(' ', '').replace('\t', '')
                    continue
                if c == ';':
                    propOrVal = True
                    if prop:
                        for tag in tags:
                            if not tag in cssDict:
                                cssDict[tag] = {}
                            for cl in classes:
                                if not cl in cssDict[tag]:
                                    cssDict[tag][cl] = {}
                                cssDict[tag][cl][prop] = value
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
        rawLine = sourceFile.readline()
        #if pref_usingUrl: rawLine = rawLine.decode(pref_encoding)
    print(cssDict, '\n')

def parse_html():
    """Parses the HTML from pref_file and calls tagProcess if it went inside
    <>, or textProcess if it is outside of <>."""
    
    global pref_usingUrl, pref_file, pref_encoding, par_tags
    tagAndAttrs = ""
    text = ""
    isTag = False
    
    rawLine = pref_file.read()
    for i in range(1):
        for c in rawLine:
            if "script" in par_tags: #<> brackets can appear in JS as
            #comparison operators, so we need a special case of processing
            #the scripts. We don't parse JS, so we can skip it.
                if c == "<": isTag = True
                if isTag:
                    tagAndAttrs += c
                    if not tagAndAttrs in "</script>":
                        isTag = False
                        tagAndAttrs = ""
                    if tagAndAttrs == "</script>":
                        isTag = False
                        tagProcess(tagAndAttrs[1:-1])
                        tagAndAttrs = ""
                continue
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


# - - - Actual program - - - 
def run():
    """Calls all the needed functions to run the program:
    reset the variables that can change, load, parse and close the file."""
    
    global pref_usingUrl, pref_path, pref_file
    backToDefault()
    if pref_guiMode: initGui()
    if pref_path:
        pref_file = get_file(pref_path, pref_usingUrl, False)
        print(pref_file.read())
        pref_file.seek(0)
        parse_html()
        pref_file.close()
    if pref_guiMode: gui.runGui()

run()
