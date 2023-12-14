# - - - Выборочный парсер HTML - - - 

# В проекте существуют 3 группы глобальных переменных:
# pref_* - общие настройки и значения, par_* - параметры отображения по мере обработки документа, parser_* - временные переменные парсера

# To-do: теги, text/gui-режимы, свойства текста, атрибуты, фильтровка по атрибутам

# - - - PREFERENCES - - - 

pref_encoding = "utf8"
pref_guiMode = False
pref_replaceSpecSymsEnabled = True
pref_filterEnabled = False
pref_incEx = False #T - inclusive, F - exclusive
pref_singleTags = {"br", "hr", "img"} #tags without </tag>

#getting prefs from bash
import sys

def err_usage():
	print("Usage:\n", sys.argv[0], "-u \"url\"\n", sys.argv[0], "-p \"path\"")
	raise SystemExit

pref_usingUrl = None
pref_bashPrefs = pref_path = ""
if len(sys.argv) < 2:
    err_usage()
for word in sys.argv[1:]:
	if word[0] == "-":
		pref_bashPrefs += word[1:]
	else:
		pref_path = word

if not "u" in pref_bashPrefs and not "p" in pref_bashPrefs:
    err_usage()
if "u" in pref_bashPrefs:
	import urllib.request
	pref_usingUrl = True
	pref_file = urllib.request.urlopen(pref_path)
if "p" in pref_bashPrefs:
	pref_usingUrl = False
	pref_file = open(pref_path)
if "f" in pref_bashPrefs:
    pref_filterEnabled = True
if "i" in pref_bashPrefs:
    pref_incEx = True
if "e" in pref_bashPrefs:
    pref_incEx = False

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
        #print(pref_fltAttrs)
        pref_filterFile.close()
        temp = temp2 = mode = None
    except:
        print("filter.txt file not found! Disabling filter...\n")
        pref_filterEnabled = False
        #raise SystemExit

#tags:
#html head body title pre h1..h6 b i tt cite em font a p br blockquote dl dt dd ol li ul div img hr table tr td th noframes form select option textarea input

# - - - DISPLAY - - - 

par_headOrBody = 0 #0 - uknown, 1 - head, 2 - body
def backToDefault():
    par_headOrBody = 0

par_inStyle = par_inScript = False
par_filtered = pref_incEx
par_tags = [] #what tags we are inside

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
				if parent != "":
					attrs[parent] = None
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
    if not pref_specSyms or text == "":
        return text
    output = sym = ""
    isCode = isSym = wasSym = wasAmp = False
    for c in text:
        if c == "&":
            if isSym:
                output += "&"
            wasAmp = isSym = True
            output += sym
            sym = ""
            continue
        if wasSym:
            wasSym = False
            if c == ";":
                continue
        if wasAmp:
            wasAmp = False
            if c == "#":
                isCode = True
                continue
        if isCode:
            if c.isdigit():
                sym += c
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
    if isSym:
        output += "&" 
    output += sym
    return output


def textProcess(text):
    if not pref_filterEnabled or not par_filtered:
	    if par_headOrBody == 2 and not par_inStyle and not par_inScript:
		    text = replaceSpecSyms(text)
		    print(text, end = "")

def tagProcess(tagAndAttrs):
	global pref_singleTags, pref_filterEnabled, pref_incEx, pref_fltTags, par_tags, par_filtered
	tag = tagSep(tagAndAttrs)
	attrs = attrsSep(tagAndAttrs)
	isClosing = True if tagAndAttrs[0] == '/' else False
	#tag stack
	if not tag in pref_singleTags:
		if not isClosing:
			par_tags.append(tag)
		else:
			for i in range(len(par_tags) - 1, -1, -1):
				if par_tags[i] == tag:
					par_tags = par_tags[:i]
					break
	#print(pref_fltTags)
	#print(par_tags)
	#filtering
	if not tag in pref_singleTags:
		singleFiltered = False 
		#print("flt en = ", pref_filterEnabled)
		if pref_filterEnabled:
			par_filtered = False
			#print("inc = ", pref_incEx)
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
	#print(par_filtered)
	if not par_filtered and not singleFiltered:
	    if tag in globals():
		    globals()[tag](attrs, isClosing)

# - - - PARSER - - - 

parser_tagAndAttrs = ""
parser_text = ""
parser_isTag = False

# считываем файл построчно, т. к. он может оказаться большим
parser_rawLine = pref_file.readline()
if pref_usingUrl:
	parser_rawLine = parser_rawLine.decode(pref_encoding)
while parser_rawLine:
    for c in parser_rawLine:
	    if c == '<':
		    textProcess(" ".join(parser_text.replace("\n","").split()))
		    parser_text = ""
		    parser_isTag = True
		    continue
	    elif not parser_isTag:
		    parser_text += c
		    continue
	    if parser_isTag:
		    if c != '>':
			    parser_tagAndAttrs += c
			    continue
		    else:
			    parser_isTag = False
			    tagProcess(parser_tagAndAttrs.lower())
			    parser_tagAndAttrs = ""
			    continue
    parser_rawLine = pref_file.readline()
    if pref_usingUrl:
	    parser_rawLine = parser_rawLine.decode(pref_encoding)

pref_file.close()