import sys

def err_usage():
	print("Usage:\npython3", sys.argv[0], "-u \"url\"\npython3", sys.argv[0], "-p \"path\"")
	raise SystemExit

if len(sys.argv) > 1:
	if sys.argv[1] == "-u":
		import urllib.request
		url = sys.argv[2]
		f = urllib.request.urlopen(url).read().decode("utf8")
	elif sys.argv[1] == "-p":
		f = open(sys.argv[2]).read()
	else:
		err_usage()
else:
	err_usage()



tags = ["!DOCTYPE", "html", "head", "body", "br", "style", "script", "a", "button", "span"]
head_or_body = 0 #0 - uknown, 1 - head, 2 - body
style_ins = False
script_ins = False


def text_process(text):
	text = text.replace("&nbsp;","")
	if head_or_body == 2:
		if not style_ins and not script_ins:
			print(text, end = "")


def tag_sep(tag_w_par):
	tp_list = tag_w_par.split(' ')
	tag = tp_list.pop(0)
	if tag[0] == '/':
		return tag[1:]
	return tag

def par_sep(tag_w_par):
	params_list = tag_w_par.split(' ')
	params_list.pop(0)
	params = ' '.join(params_list)
	return params


#tag functions
def head(params, isClosing):
	global head_or_body
	head_or_body = 0 if isClosing else 1

def body(params, isClosing):
	global head_or_body
	head_or_body = 0 if isClosing else 2

def br(params, isClosing):
	text_process('\n')

def style(params, isClosing):
	global style_ins
	style_ins = False if isClosing else True

def script(params, isClosing):
	global script_ins
	script_ins = False if isClosing else True

def a(params, isClosing):
	if not isClosing:
		text_process('\n')

def button(params, isClosing):
	if not isClosing:
		text_process("\n[button] ")

def span(params, isClosing):
	if not isClosing:
		text_process('\n')



def tag_process(tag_w_par):
	tag = tag_sep(tag_w_par)
	params = par_sep(tag_w_par)
	isClosing = True if tag_w_par[0] == '/' else False
	for t in tags:
		if tag == t and tag in globals():
			tag_func = globals()[tag]
			tag_func(params, isClosing)



tag_w_par = ""
text = ""
isTag = False
wasSp = False
for c in f:
	if c == '<':
		text_process(text)
		text = ""
		isTag = True
		continue
	elif not isTag:
		if c != '\n' and not (wasSp == True and c == ' '):
			text += c
		wasSp = True if c == ' ' else False
		continue
	if isTag:
		if c != '>':
			tag_w_par += c
			continue
		else:
			isTag = False
			tag_process(tag_w_par)
			tag_w_par = ""
			continue
