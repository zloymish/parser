import sys

if sys.argv[1] == "-u":
	import urllib.request
	url = sys.argv[2]
	f = urllib.request.urlopen(url).read().decode("utf8")
elif sys.argv[1] == "-p":
	f = open(sys.argv[2]).read()
else:
	print("Usage:\npy3 html.py -u url\npy3 html.py -p path")
	raise SystemExit

tags = ["!DOCTYPE", "html", "head", "body", "a", "b", "br", "h1", "h2", "h3", "h4", "h5", "h6"]
head_or_body = 0 #0 - uknown, 1 - head, 2 - body


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
	print("")



def tag_process(tag_w_par):
	tag = tag_sep(tag_w_par)
	params = par_sep(tag_w_par)
	isClosing = True if tag_w_par[0] == '/' else False
	for t in tags:
		if tag == t and tag in globals():
			tag_func = globals()[tag]
			tag_func(params, isClosing)


def text_process(text):
	if head_or_body == 2:
		print(text, end = "")


tag_w_par = ""
text = ""
isTag = False
for c in f:
	if c == '<':
		text_process(text)
		text = ""
		isTag = True
		continue
	elif not isTag:
		text += c
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
