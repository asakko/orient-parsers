# -*- coding: utf-8 -*-
from textparsers import HTTPParser
from parsers import recognizeParser, RegexParser, RegexParser2
import sys

kwargs  = dict(x.split('=', 1) for x in sys.argv[1:])
bulk    = kwargs.pop("bulk", None)
urllink = kwargs.pop("url", "http://helsinginsuunnistajat.fi/assets/Kivikko12.10.2014_rastit.txt")
verbose = kwargs.pop("verbose", "False")=="True"
title   = kwargs.pop("title", "")
place   = kwargs.pop("place", "")
date    = kwargs.pop("date", "1.1.1982")
parser_ = kwargs.pop("parser", "recognize")
if parser_=="regex":
    urlParser = HTTPParser, 
    parser    = RegexParser(url=urllink, verbose=verbose, date=date, place=place, header=urllink, title=title);
elif parser_=="regex2":
    urlParser = HTTPParser, 
    parser    = RegexParser2(url=urllink, verbose=verbose, date=date, place=place, header=urllink, title=title);
else:
    print(urllink)
    urlParser, parser = recognizeParser(urllink, bulk=bulk, verbose=verbose, date=date, place=place, header=urllink, title=title);

parser.open_output('o.txt');
for cnt in range(len(urlParser)):
    #try:
        parser.parse(urlParser[cnt])
    #    if len(parser.output)>0:
    #        break
    #except IndexError as e:
    #    print "error with parser.parse: %s %s" % (urllink, e), parser
print("%s: extracted %u performances" % (urllink, len(parser.output)))
fp = open('insert.sql', 'w');
fp.write("# extracted %u performances.\n" % len(parser.output));
fp.write("SET @contest_id=0;\n");
fp.write("SET @track_id=0;\n");
fp.write("SET @perf_id=0;\n");
parser.insert(commit=False, output=fp);
fp.write("# OK!");
fp.close();
parser.close()
parser.close_output();
