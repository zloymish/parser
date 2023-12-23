from parser import *

def test_strToFile():
    with open(".tmp", "w") as f:
        f.write("abc")
    with open(".tmp") as f:
        assert strToFile("abc").read() == f.read()

def test_get_file():
    with open(".tmp", "w") as f:
        f.write("abc")
    with open(".tmp") as f:
        assert get_file(".tmp", False, False).read() == f.read()

def test_getAbsPath():
    assert getAbsPath("abcd") == "abcd"

def test_closestAttr():
    assert closestAttr("aoscnuosanc") == ""

def test_findCssVal():
    assert findCssVal("cmda", "anxjcs", "caodnc") == ""

def test_closestCssVal():
    assert closestCssVal("cnjadocojna") == ""

def test_tagSep1():
    assert tagSep("") == ""
    
def test_tagSep2():
    assert tagSep(1) == ""

def test_tagSep3():
    assert tagSep("/a b c") == "a"

def test_attrsSep1():
    assert attrsSep("") == ""
    
def test_attrsSep2():
    assert attrsSep(1) == ""

def test_atrsSep3():
    assert attrsSep("/a b c") == {"b":"","c":""}

def test_replaceSpecSyms1():
    assert replaceSpecSyms("") == ""

def test_replaceSpecSyms2():
    assert replaceSpecSyms(1) == 1

def test_replaceSpecSyms3():
    assert replaceSpecSyms("&nbsp;") == "\xa0"

def test_replaceSpecSyms4():
    assert replaceSpecSyms("&nbsptext") == "\xa0text"
