from parser import tagSep

def test_tagSep1():
    assert tagSep("") == ""
    
def test_tagSep2():
    assert tagSep(1) == ""

def test_tagSep3():
    assert tagSep("/a b c") == "a"

from parser import attrsSep

def test_attrsSep1():
    assert attrsSep("") == ""
    
def test_attrsSep2():
    assert attrsSep(1) == ""

def test_atrsSep3():
    assert attrsSep("/a b c") == {"b":"","c":""}

from parser import replaceSpecSyms

def test_replaceSpecSyms1():
    assert replaceSpecSyms("") == ""

def test_replaceSpecSyms2():
    assert replaceSpecSyms(1) == 1

def test_replaceSpecSyms3():
    assert replaceSpecSyms("&nbsp;") == "\xa0"

def test_replaceSpecSyms4():
    assert replaceSpecSyms("&nbsptext") == "\xa0text"
