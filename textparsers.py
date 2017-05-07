# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import base64
from urllib.request import urlopen
import regex as re
import sys
from database import database
#from string import join

def bs_preprocess(html):
     pat = re.compile('(^[\s]+)|([\s]+$)', re.MULTILINE)
     html = html.replace("\n", " ").replace("\r", " ")
     html = html.replace("</pre>", "</pre>\n").replace("</title>", "</title>\n").replace("</h2>", "</h2>\n").replace("<br>", "<br>\n").replace("<br>\n<br>\n", "<br><br>\n");
     html = html.replace("</PRE>", "</PRE>\n").replace("</TITLE>", "</TITLE>\n").replace("</H2>", "</H2>\n").replace("<BR>", "<BR>\n").replace("<BR>\n<BR>\n", "<BR><BR>\n");
     return html

class TextParser:
    def __init__(self, url):
        html = urlopen(url).read()    
        self.text = html.decode("latin-1")

    def getText(self):
        return self.text

class LocalHTTPParser(TextParser):
    def __init__(self, url):
        html = urlopen(url).read()    
        soup = BeautifulSoup(html, "lxml")
        for script in soup(["script", "style"]):
            script.extract()
        self.text = soup.get_text()
   
class HTTPParser(TextParser):
    def __init__(self, url):
        #fp = open(url, 'r');
        #html = join(fp.readlines(), ' ');
        #fp.close();
        html = urlopen(url).read()    
        soup = BeautifulSoup(html, "lxml")
        for script in soup(["script", "style"]):
            script.extract()
        self.text = soup.get_text()

class HTTPParserHS(TextParser):
    def __init__(self, url):
        #fp = open(url, 'r');
        #html = join(fp.readlines(), ' ');
        #fp.close();
        html = urlopen(url).read()    
        soup = BeautifulSoup(html, "lxml")
        ## Remove the team (Third column in each table row)
        [k.find_all("td")[2].extract() for k in soup.find_all("tr")]
        for script in soup(["script", "style"]):
            script.extract()
        self.text = soup.get_text()


class HTTPParserWithPreprocess(TextParser):
    def __init__(self, url):
        html = urlopen(url).read()    
        html = bs_preprocess(html.decode('latin-1')) ##.encode("utf-8"))
        soup = BeautifulSoup(html, "lxml")
        for script in soup(["script", "style"]):
            script.extract()
        self.text = soup.get_text()


