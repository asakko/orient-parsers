from bs4 import BeautifulSoup
import base64
from urllib.request import urlopen
import regex as re
import sys
import time
from database import database
from textparsers import *
from time import sleep

def orderNames(inp, c1, c2):
    n1 = 0
    n2 = 0
    n3 = 0
    n4 = 0
    n5 = 0
    n6 = 0
    for cnt in range(len(inp)):
        if(inp[cnt][c1][-3:]=='NEN'):
            n1 += 1
        if(inp[cnt][c1][-2:]=="LA"):
            n2+= 1
        if(inp[cnt][c1][-2:]=="LÄ"): ##.decode("utf-8")):
            n3+= 1
        if(inp[cnt][c2][-3:]=='NEN'):
            n4 += 1
        if(inp[cnt][c2][-2:]=='LA'):
            n5 += 1
        if(inp[cnt][c2][-2:]=="LÄ"): ##.decode("utf-8")):
            n6+= 1

    # family, first
    if n1+n2+n3>n4+n5+n6:
        return [inp[cnt][c1] for cnt in range(len(inp))], [inp[cnt][c2] for cnt in range(len(inp))] 
    else:
        return [inp[cnt][c2] for cnt in range(len(inp))], [inp[cnt][c1] for cnt in range(len(inp))] 

def recognizeParser(url, **kwargs):
    bulk = kwargs.pop("bulk")
    if bulk:
        return (TextParser, ), BulkParser(url, **kwargs)
    elif url.find("/ar/")>=0 or url.find("www.rasti-jyry.fi/")>=0:
        return (HTTPParser,), AluerastitParser(url, **kwargs)
    if url.find("Lataukset")>=0 or \
       url=="https://espoonsuunta.fi/wp-content/uploads/2016/08/egames2016la_kuntovaliajat.html" or \
       url=="https://espoonsuunta.fi/wp-content/uploads/2016/09/v160910.html" or \
       url=="http://koti.kapsi.fi/~sakko/v160917.html":
        return (LocalHTTPParser,), ItarastitParser(url, **kwargs)
    elif url.find("www.ku-rastit.net")>=0 or url=="http://koti.kapsi.fi/~sakko/valiajat2508.html" or url=="http://sakko.kapsi.fi/lr/valiajat2909.html" or url=="http://sakko.kapsi.fi/lr/valiajat0610.html" or url=="http://sakko.kapsi.fi/lr/valiajat1310.html" or url=="http://sakko.kapsi.fi/lr/valiajat2010.html":
        return (HTTPParser, HTTPParserWithPreprocess), KUParser(url, **kwargs)
    elif url.find("rastihaukat.fi/Itarastit/")>=0 or url.find("/mesik/")>=0:
        return (HTTPParser,), ItarastitParser(url, **kwargs)
    elif (url.find("online.helsinginsuunnistajat.fi")>=0 or url.find("valiajat.html")>=0):
        return (HTTPParserHS,), IltarastitHS3Parser(url, **kwargs)
    elif (url.find("helsinginsuunnistajat.fi")>=0 or url.find("~sakko")>=0):
        return (HTTPParser,), IltarastitHS2Parser(url, **kwargs)
    elif url.find("rajamaenrykmentti.fi")>=0 or url=="http://sakko.kapsi.fi/v170516.html":
        return (HTTPParser,), IltarastitRRParser(url, **kwargs)
    elif url.find("ok77.fi")>=0 or url=="http://koti.kapsi.fi/~sakko/v160908.html" or url=="http://www.ku-rastit.net/tulokset/valiajat0809.html":
        return (HTTPParser,), LansirastitParser(url, **kwargs)
    elif url.find("www.espoonakilles.fi")>=0:
        return (HTTPParser,), EspoorastitParser(url, **kwargs)

class RouteParser:
    def __init__(self, url, verbose=False, title="null", place="null", date="null", header=None):
        self.url = url
        self.outputfile   = None
        self.verbose      = verbose
        self.title        = title.upper() #decode("utf-8").upper()
        self.header       = header.upper() #decode("utf-8").upper()
        self.place        = place.upper() #encode('latin-1').upper()
        self.date         = date.upper() #decode("utf-8").upper()
        self.organizer    = "null".upper() #decode("utf-8").upper()
        self.routes = {'A': 7.0, 'B':5.0, 'C': 3.0, 'C2': 3.01, 'CV': 3.02, 'D':2.0, '9': 9.0, '7': 7.0, '5': 5.0, 'ARATA': 7.0, 'BRATA': 6.0, 'CRATA': 5.0, 'DRATA': 4.0, 'ERATA': 3.0, 'FRATA': 2.0, 'SPRT': 3.0}
        self.routeline    = None
        self.nameline     = None
        self.intervalline = None
        self.firstname = None
        self.familyname = None
        self.fulltime = None
        self.route = None
        self.track_bug_count = 0
        self.output = []
        self.extraparser = None
        self.linecount = 0
        self.track_type = 'NORMAL'
        self.permanent_night = False
        self.db = database(host="localhost", user="root", db="orient", passwd="1jw9DsKFwojjjcm");
        #self.db = database(host="localhost", user="root", db="Orientas2", passwd=base64.b64decode("anV0dW5qdXVyaQ=="))
        #self.db = database(host="localhost", user="root", db="Orienteering", passwd=base64.b64decode("anV0dW5qdXVyaQ=="))
        #self.db = database(host="db4free.net", user="sakko", db="orientas", passwd="emapummi"); #base64.b64decode("ZW3DpHB1bW1p"))
        #self.db = database(host="fdb12.biz.nf", user="1749465_orientas", db="1749465_orientas", passwd="emapumm1")
        #self.db = database(host="127.0.0.1", port=3307, user="sakko", db="sakko", passwd="emapummi")

    def close(self):
        if self.extraparser is not None:
            return self.extraparser.close()
        self.db.close()

    def open_output(self, fname):
        self.outputfile = open(fname, 'wb');

    def close_output(self):
        self.outputfile.close();

    def printstr(self, strout, force=False):
        if strout is not None and (self.verbose or force and strout!=None):
            if self.outputfile is None:
                print(strout.encode('utf-8'))
            else:
                #self.outputfile.write(strout.encode('utf-8')+'\n');
                self.outputfile.write((strout+'\n').encode('utf-8'));

    def parse(self, urlparser):
        #self.printstr("parsing: %s" % self)
        self.urlparser = urlparser(self.url);
        self.text = self.urlparser.getText().upper().splitlines()

        waitforintervals = False
        lineno = 0
        while lineno<len(self.text):
            line = self.text[lineno]

            if len(line)>0:
                x = self.newline(line)
                if x =='Nameline' and self.route is not None:
                    self.handleNameline()
                    # move to next line and analyze it
                    lineno += 1
                    self.intervalline = self.text[lineno]
                    self.handleintervalline()
                if x== 'Routeline':
                    print("Routeline: ", line, " >>> ", self.route, " >>> ", self.routetag)

            # move to next line
            lineno += 1

    def insert(self, commit=True, output=None):
        if self.extraparser is not None:
            return self.extraparser.insert(commit, output)
        self.printstr("event: %s %s %s" % (self.date, self.title, self.place)); #.decode('latin-1')));
        familynames, firstnames = orderNames(self.output, 4, 5)
        # insert event
        datestr = '%04u-%02u-%02u' % (int(self.date.split(".")[2]), int(self.date.split(".")[1]), int(self.date.split(".")[0]))
        print('%s' % self.place) #.decode('latin-1')
        contest_id = self.db.AddContest(self.title, self.place, datestr, self.organizer, output=output);
        #print contest_id
        ## insert performances
        prev_track = None
        for (perf, fam, fir) in zip(self.output, familynames, firstnames):
            if str(perf[6])+perf[10]+perf[11] != prev_track:
                # Rank performances of the finished track
                if prev_track is not None:
                    if output is not None:
                        output.write("CALL Rank_Performances2(@track_id);\n");
                
                if len(perf)==11: perf.append('NORMAL');
                num_intervals = perf[9]
                print(len(perf))
                print(str(perf))
                track_id = self.db.AddTrack(contest_id, length=perf[6], tag=perf[10], intervals=perf[9], track_type=perf[11], output=output)
                if track_id<0:
                    continue
                prev_track = str(perf[6])+perf[10]+perf[11]
            if min(perf[8])==0 or len(perf[8])!=perf[9] or len(perf[8])!=num_intervals:
              continue
            #print track_id
            # call addperformance(@id_track, "sakko", "arto", null, @id_perf);
            perf_id = self.db.AddPerformance(track_id, fam, fir, perf[7], datestr, output=output)
            #break
            #self.printstr("call addperformance(track_id, %s, %s, %u, performance_id)" % (fam, fir, perf[7])) #perf[4], perf[5], perf[7]))
            for cnt in range(len(perf[8])):
                try:
                    self.db.AddInterval(perf_id, track_id, cnt+1, perf[8][cnt], output=output)
                except:
                    print("AddInterval failed: ", fam.encode('utf-8'), fir.encode('utf-8'))
            # Ensure correct values
            if not self.db.CheckNumberOfIntervals(perf_id):
                print("CheckNumberOfIntervals failed for %s %s" % (fam, fir))

        # Rank performances of the last track
        if output is not None:
            output.write("CALL Rank_Performances2(@track_id);\n");

        # insert invervals
        if commit:
            self.db.commit()

    def newline(self, line):
        pass

    def parseintervalline(self):
        line = self.intervalline.replace(".","").replace(":","");
        columns = line.replace("-", " ").split()
        interval_secs = [self.parseseconds(c) for c in columns[1::2]];
        secs = sum(interval_secs)
        return line, columns, interval_secs, secs

    def handleintervalline(self):
        #print self.parseintervalline()
        try:
            Line, columns, interval_secs, secs = self.parseintervalline()
        except:
            return
        
        #print "handling intervals for %s %u: %s" % (self.familyname, secs, line)
        if abs(self.fulltime-secs)>1:
            self.printstr("warning: fulltime %u != sum(intervaltimes) %u for %s (%.2f %s %s)" % (self.fulltime, secs, self.header, self.route, self.familyname, self.firstname), True)
            self.printstr(self.header, True)
            self.printstr(self.routeline, True)
            self.printstr(self.nameline, True)
            self.printstr(self.intervalline, True)
            ##print self.familyname, self.firstname, columns
            return
        hours = secs/3600
        mins = (secs-3600*hours)/60
        secs_rest = secs-3600*hours-60*mins
   
        #self.printstr("%s %s %16s %16s %3.1f %6u %6u %02u-%02u:%02u" % (self.date, self.place, self.firstname, self.familyname, self.route, len(columns), secs, hours, mins, secs_rest))

        if len(interval_secs) != self.intervals:
            self.printstr("Warning: strange number of intervals for %s %s" % (self.familyname, self.firstname))
        else:
            self.output.append((self.date.split(".")[0], self.date.split(".")[1], self.date.split(".")[2],  # date
                                self.place,
                                self.firstname,
                                self.familyname,
                                self.route,
                                secs,
                                interval_secs,
                                self.intervals,
                                self.routetag,
                                self.track_type))
        # todo: update tables here
        return

    def handleNameline(self):
        line = self.nameline.replace(".","");
        columns = line.split()
        if len(columns)>3 and columns[0].isdigit() and columns[1].replace("-","").isalpha() and columns[2].replace("-","").isalpha() and columns[-1].isdigit():
            self.firstname  = columns[1]
            self.familyname = columns[2]
            self.fulltime   = self.parseseconds(columns[-1])
            return True
        else:
            return False

    def parseseconds(self, instr):
        if len(instr)==2:
            assert(int(instr)<=60)
            return int(instr)
        elif len(instr)==4:
            return int(instr[0:2])*60+self.parseseconds(instr[2:4])
        elif len(instr)==3:
            return self.parseseconds("0%s" % instr)
        elif len(instr)>4:
            return int(instr[:-4])*3600+self.parseseconds(instr[-4:]);
        else:
            raise exception("unable to extract seconds from input string %s" % instr)

class IltarastitHSParser(RouteParser):

    def handleNameline(self):
        line = self.nameline;
        columns = line.split()
        if len(columns)>3 and columns[0].isdigit() and columns[1].replace("-","").isalpha() and columns[2].replace("-","").isalpha() and columns[-1].isdigit():
            self.firstname  = columns[2]
            self.familyname = columns[1]
            self.fulltime   = self.parseseconds(columns[-1])
            return True
        else:
            return False

    def newline(self, line):
        ind = line.find("RATA:")
        self.routetag = ""
        # separator line
        if ind>=0:
            if line[ind:].split()[1].replace(",","").isdigit():
                self.route = float(line[ind:].split()[1].replace(",","."))
            else:
                tag = line[ind:].split()[1]
                self.route = self.routes.get(tag)
                if self.route is None:
                    return 'DummyRouteLine'
            self.routeline = line
            self.track_type = 'NORMAL';
            self.nameline = None
            return 'Routeline'

        #  name line
        columns = line.replace(".","").split()
        if len(columns)>3 and columns[0].isdigit() and columns[1].replace("-","").isalpha() and columns[2].replace("-","").isalpha() and columns[-1].isdigit():
            self.nameline = line.replace(".","")
            return 'Nameline'

        if self.route != None and self.nameline is None:
            self.intervals = len(line.split())


    def parseseconds(self, instr):
        if len(instr)==2:
            assert(int(instr)<=60)
            return int(instr)
        elif len(instr)==4:
            return int(instr[0:2])*60+self.parseseconds(instr[2:4])
        elif len(instr)==3:
            return self.parseseconds("0%s" % instr)
        elif len(instr)>4:
            return int(instr[:-2])*60+self.parseseconds(instr[-2:])
        else:
            raise exception("unable to extract seconds from input string %s" % instr)
   
class AluerastitParser(RouteParser):

    def newline(self, line):
        nameline = False
        routeline = False

        if (line.find('OMA')>=0 or line.find('0MA')>=0) and len(line.split())<10: # and line.find('AJAT')>=0: # or line.find('RATA')>=0:
            self.route = None
            return 'DummyRouteLine'

        #if line.find('PUUTTUU'.decode('utf-8'))>=0 and line.find("RASTIVÄLIEN AJAT".decode('utf-8'))>=0:
        if line.find('PUUTTUU')>=0 and line.find("RASTIVÄLIEN AJAT")>=0:
            self.route=None
            return 'DummyRouteLine'

        #if line.find('YÖ'.decode('utf-8'))>=0 and len(line.split())<10:
        #    self.route=None
        #    return 'DummyRouteLine'

        #if line.find('VÄÄRÄ'.decode('utf-8'))>=0 and len(line.split())<10:
        if line.find('VÄÄRÄ')>=0 and len(line.split())<10:
            self.route=None
            return 'DummyRouteLine'

        #if line.find('RATA'.decode('utf-8'))>=0 and line.find('RASTIVÄLIEN AJAT'.decode('utf-8')) and line.replace("_", " ").replace(",", " ").rfind("KM ")<0:
        if line.find('RATA')>=0 and line.find('RASTIVÄLIEN AJAT') and line.replace("_", " ").replace(",", " ").rfind("KM ")<0:
            self.route=None
            return 'DummyRouteLine'

        #if line.find('PUUTTUU'.decode('utf-8'))>=0 and len(line.split())<10:
        if line.find('PUUTTUU')>=0 and len(line.split())<10:
            self.route=None
            return 'DummyRouteLine'

        #if line.find('JÄRJESTYS'.decode('utf-8'))>=0 and (len(line.split())<10 or line.find('RASTIVÄLIEN AJAT'.decode('utf-8'))>=0):
        if line.find('JÄRJESTYS')>=0 and (len(line.split())<10 or line.find('RASTIVÄLIEN AJAT')>=0):
            self.route=None
            return 'DummyRouteLine'

        #if line.find("KÄYRÄ".decode('utf-8'))>=0 and len(line.split())<10:
        if line.find("KÄYRÄ")>=0 and len(line.split())<10:
            self.route=None
            return 'DummyRouteLine'

        #if line.find("FIRA-YÖ".decode('utf-8'))>=0:
        if line.find("FIRA-YÖ")>=0:
            self.permanent_night=True

        # Separator for intervals
        if False:
            ind = line.find("RASTIVÄLIEN")
            if ind>0:
                    thisline = line[:ind].replace("RATA", " ").replace(",", " ")
                    tag = thisline.split(" ")[0]
                    self.counter = 0
                    if len(thisline.split(" "))>1:
                        tag += thisline.split()[0]
                    try:
                        print(tag)
                        if tag.isdigit():
                            self.routeline = None
                            self.routetag = None
                            self.route = None
                            return 'DummyRouteLine'
                        self.route = self.routes[tag]
                        self.routetag = tag
                        self.routetag = str(self.route) + " km " + " ".join(thisline.split(" "))
                        self.routeline = line
                        self.readwinner = True
                        return 'Routeline'
                    except:
                        return 'DummyRouteLine'
                        pass

        #ind = max(line.find("-RATA"), line.replace("_", " ").replace(",", " ").rfind("KM "))
        ind = line.replace("_", " ").replace(",", " ").rfind("KM ");

        # separator line
        #if ind>=0 and line.find("PYORA")<0 and line.find("PYÖRÄ".decode('utf-8'))<0: # and line.find("YÖ".decode('utf-8'))<0 
        if ind>=0 and line.find("PYORA")<0 and line.find("PYÖRÄ")<0: # and line.find("YÖ".decode('utf-8'))<0 
            try:
                #try:
                #    self.route = self.routes.get(str(line[ind-1]));
                #except:
                num=''.join(i for i in line[:ind].replace("_", " ").split()[-1] if (i.isdigit() or i in ('.',','))).replace(",",".")
                self.route = float(num)
                self.routeline = line
                self.routetag = ' '.join(line[:ind].replace("_", " ").split()[:-1])
                ##hack for some ku-rastit:
                #ind = line.find(',');
                #self.routetag = ' '.join(line[:ind].replace("_", " ").split()[1:])
                #if self.permanent_night or line.replace('_YO'.decode('utf-8'), '_YÖ'.decode('utf-8')).find("YÖ".decode('utf-8'))>=0:
                if self.permanent_night or line.replace('_YO', '_YÖ').find("YÖ")>=0:
                    self.track_type = 'NIGHT'
                #elif line.find('SPR'.decode('utf-8'))>=0:
                elif line.find('SPR')>=0:
                    self.track_type = 'SPRINT'
                else:
                    self.track_type = 'NORMAL';
                #if line.find("VAIKEA".decode('utf-8'))>=0:
                if line.find("VAIKEA")>=0:
                    self.routetag = "VAIKEA"
                #if line.find("HELPPO".decode('utf-8'))>=0:
                if line.find("HELPPO")>=0:
                    self.routetag = "HELPPO"
                self.routetag = ("%.2f %s" % (self.route, self.routetag)).strip();
                if len(self.routetag)<80:
                    print("#TAG: ", self.route, self.routetag)
                    print("# ", line[:ind])
                pass #return 'Routeline'

            except:
                print("error with num at %s: num=%s" % (self.header, num))
                print(line)
                sys.exit()
            routeline = True

        #if (self.route != None and line[-16:]=="RASTIVÄLIEN AJAT".decode('utf-8')):
        #    self.route = None
        #    return 'DummyRouteLine'

        self.linecount += 1
        #if line[-5:]=='TULOS'.decode('utf-8') and self.route != None:
        if line[-5:]=='TULOS' and self.route != None:
            self.intervals = int(line.replace("[", " ").replace("]", " ")[:-6].split(".")[-2].split()[-1])
            print(self.routetag, self.intervals)
            #sys.exit()

        #  name line
        columns = line.replace(".","").split()
        if len(columns)>3 and columns[0].isdigit() and columns[1].replace("-","").isalpha() and columns[2].replace("-","").isalpha() and columns[-1].isdigit():
            self.nameline = line
            self.routeline = None
            nameline = True
            #print line, self.route, routeline, nameline
        if routeline:
            return 'Routeline'
        if nameline:
            return 'Nameline'
   
    
class ItarastitParser(AluerastitParser):
    pass    
    

class KUParser(RouteParser):

    def parse(self, urlparser):
        print(self, urlparser)
        self.urlparser = urlparser(self.url);
        self.text = self.urlparser.getText().upper().splitlines()
        waitforintervals = False
        lineno = 0
        while lineno<len(self.text):
            line = self.text[lineno]

            if len(line)>0:
                if self.newline(line)=='Nameline' and self.route is not None:
                    self.handleNameline()
                    self.handleintervalline()

            # move to next line
            lineno += 1
        if len(self.output)==0:
            self.close()
            print("Using AluerastitParser!");
            self.extraparser = AluerastitParser(url=self.url, date=self.date, place=self.place, header=self.header, title=self.title);
            self.extraparser.parse(urlparser)
            self.output = self.extraparser.output
            return
        pass

    def parseintervalline(self):
        line = self.intervalline.replace(".","")
        columns = line.split()
        try:
            interval_secs = [self.parseseconds(c.replace("1--", " ").replace("-", " ").split()[-1]) for c in columns[3:-4]]
            secs = sum(interval_secs)
        except:
            return None
        return line, columns, interval_secs, secs

    def handleNameline(self):
        line = self.nameline.replace(".","");
        columns = line.split()
        if len(columns)>3 and columns[0].isdigit() and columns[1].replace("-","").isalpha() and columns[2].replace("-","").isalpha() and columns[-3].isdigit():
            self.firstname  = columns[2]
            self.familyname = columns[1]
            self.fulltime   = self.parseseconds(columns[-3])
            return True
        else:
            return False


    def newline(self, line):
        ind = line.find("TILANNE")
        if ind>=0:
            self.route = None
            return 'DummyRouteLine'

        if line[-5:]=='TULOS' and self.route!=None:
            self.intervals = len(line.split())-4
            #print self.intervals, line.split()
            #self.intervals = int(line.replace("[", " ").replace("]", "    ")[:-9].split(".")[-2].split()[-1])
            #print self.intervals, line.split()
            #sleep(5)

        ind = line.find("RASTIVÄLIEN")
        #print ind, line
        #sleep(1);
        # Separator line
        if ind>=0:
            try:
               if line[:ind].split()[0].replace(",","").replace(".","").replace("P","").replace("V","").replace("H","").replace("YO","").replace("Y","").isdigit(): # P for Paiva, V for Vaikea, Y for Yo
                   self.route = float(line[:ind].split()[0].replace(",",".").replace("P","").replace("V","").replace("H","").replace("YO","").replace("Y",""))
                   self.routeline = line
                   self.routetag = " ".join(line[:ind].split()[:-1])
                   #print "AJAT: ", ind, line, " >>> ", self.routetag
                   #sleep(2);
                   if line.find("YO")>=0 or line[:ind].split()[0][-1]=='Y' or line[:ind].split()[0][-2:]=='YO':
                       self.track_type = "NIGHT";
                   else:
                       self.track_type = "NORMAL";
                   if line.find("VAIKEA")>=0 or line[:ind].split()[0][-1]=='V' or line[:ind].split()[0][-3:]=='VYO':
                       self.routetag = "VAIKEA"
                   if line.find("HELPPO")>=0 or line[:ind].split()[0][-1]=='H':
                       self.routetag = "HELPPO"
                   self.routetag = ("%.2f %s" % (self.route, self.routetag)).strip();
                   #print "#TAG: ", self.route, self.routetag, self.track_type
                   #sleep(2);
                   return 'Routeline'
               else:
                   self.route = None
                   return 'DummyRouteline'
            except:
                return
    
        #  Name line
        columns = line.replace(".","").split()
        if len(columns)>3 and columns[0].isdigit() and columns[1].replace("-","").isalpha() and columns[2].replace("-","").isalpha() and columns[-3].isdigit():
            self.nameline = line.replace(".","")
            self.intervalline = self.nameline
            return 'Nameline'


class EspoorastitParser(KUParser):
    def __init__(self, url, verbose=False, title="null", place="null", date="null", header=None):
        KUParser.__init__(self, url, verbose, title, place, date, header)
        self.readwinner = False # Needed for unsystematic expression of last interval at interval-timelines
        print("Espoorastit...")

    def parseintervalline(self):
        line = self.intervalline.replace(".","").replace(" - ", " ")
        columns = line.split()
        interval_secs = [self.parseseconds(c.replace("-", " ").split()[-1]) for c in columns[3:-3]]
        secs = sum(interval_secs)
        if self.readwinner:
            self.winner = False
            if self.intervals==len(interval_secs)-1:
                self.intervals += 1
        return line, columns, interval_secs, secs

    def newline(self, line):
        if (line.find('EI AIKAA')>=0):
            self.route = None
            return 'DummyRouteLine'

        if line.find('YÖ')>=0 and len(line.split())<10:
            self.route = None
            return 'DummyRouteLine'

        if line.find('POLUTON')>=0 and len(line.split())<10:
            self.route = None
            return 'DummyRouteLine'

        if line[-5:]=='TULOS' and self.route!=None:
            self.intervals = len(line.split())-4


        ind = line.replace("_", " ").replace(",", " ").find(" KM")
        # Separator for total times
        if ind>=0:
            try:
                num=''.join(i for i in line[:ind].replace("_", " ").split()[-1] if (i.isdigit() or i in ('.',','))).replace(",",".")
                tag = line[:ind].split()[0]
                if len(line[:ind].split())>3:
                    tag += line[:ind].split()[1][0]
                self.routes[tag]=float(num)
                self.route = None
                self.routetag = ' '.join(line[:ind].split()[:-1]).replace(" -", "").replace(" :", "")
                self.track_type = 'NORMAL';
            except:
                print("error with num at %s: num=%s" % (self.header, num))
            return 'Routeline'

        # Separator for intervals
        ind = line.find("TILANNE")
        if ind>=0:
            self.statusline = True
            self.route = None

        # Separator for intervals
        ind = line.find("RASTIVÄLIEN")
        if ind>0:
                tag = line[:ind].split()[0]
                self.counter = 0
                if len(line[:ind].split())>1:
                    tag += line[:ind].split()[1][0]
                try:
                    self.route = self.routes[tag]
                    self.routetag = tag
                    self.routetag = str(self.route) + " km " + " ".join(line[:ind].split())
                    self.routeline = line
                    self.readwinner = True
                except:
                    pass

        #  Name line
        columns = line.replace("."," ").split()
        if self.route is not None:
            print(self.route)
            #if len(columns)>3:
                #print columns

        if self.route is not None and len(columns)>3 and columns[0].isdigit() and columns[1].replace("-","").isalpha() and columns[2].replace("-","").isalpha() and columns[-3].isdigit():
            self.nameline = line.replace(".","")
            self.intervalline = self.nameline
            print(self.route, columns, self.nameline, self.intervalline)
            sys.exit()
            return 'Nameline'

class LansirastitParser(AluerastitParser):
    def newline(self, line):
        if (line.find('OMA')>=0 and line.find('AJAT')>=0): # or line.find('RATA')>=0:
            self.route = None
            return 'DummyRouteLine'

        # Separator for intervals
        ind = line.find("TILANNE")
        if ind>=0:
            self.statusline = True
            self.route = None

        if (line[-5:]=='TULOS' or line[-8:]=='RESULTAT') and self.route!=None:
            self.intervals = int(line.replace("[", " ").replace("]", "    ")[:-9].split(".")[-2].split()[-1])

        ind = line.replace("_", " ").replace(",", " ").rfind("KM ")
        if line.find("TEK ")>=0 or ind>=0:
            # Flag for night and technical tracks
            if line.find("PÄIVÄ")>=0:
                self.track_type = 'NORMAL';
            if line.find("YÖ")>=0:
                self.track_type = 'NIGHT';
            elif line.find("TEK")>=0:
                self.track_type = 'TECHNICAL';
            else:
                self.track_type = 'NORMAL';

            if True: #try:
                num=''.join(i for i in line[:ind].replace("_", ".").split()[-1] if (i.isdigit() or i in ('.',','))).replace(",",".").rstrip('.')
                num=''.join(i for i in line[:ind].replace("_", " ").split()[-1] if (i.isdigit() or i in ('.',','))).replace(",",".").rstrip('.')
                if line.find('TEK ')==1:
                  num = str(re.split(' |,', line)[2])
                  ind = 4+len(str(num))
                self.route = float(num)
                self.routeline = line
                if line.find("KÄYRÄ")>=0:
                    self.routetag = str(self.route) + " km (%s)" % ("käyrä")
                    self.track_type = 'TECHNICAL';
                else:
                    self.routetag = line[:line.find(',')]
                    self.routetag = ' '.join(line[:ind].split()[:-1]).replace(" -", "")
                    #print self.routetag.find(',')
                    self.routetag = self.routetag[1:]
                    #print "TAG: ", self.routetag
                    #sleep(3)
                if len(self.routetag)==0:
                    self.routetag = str(self.route) + " km"
                #print self.route, self.track_type
            #except:
            #    print("error with num at %s: num=%s" % (self.header, num))
            #    print(line)
            #    sys.exit()
            return 'Routeline'

        #  name line
        columns = line.replace(".","").split()
        if len(columns)>3 and columns[0].isdigit() and columns[1].replace("-","").isalpha() and columns[2].replace("-","").isalpha() and columns[-1].isdigit():
            self.nameline = line
            return 'Nameline'

    pass

class IltarastitHS2Parser(AluerastitParser):
    def newline(self, line):
        if (line.find('OMA')>=0 and line.find('AJAT')>=0): # or line.find('RATA')>=0:
            self.route = None
            return 'DummyRouteLine'

        # Separator for intervals
        #ind = line.find("TILANNE")
        ind = line.find("TILANNE")
        if ind>=0:
            self.statusline = True
            self.route = None

        #if (line[-5:]=='TULOS'.decode('utf-8') or line[-8:]=='RESULTAT'.decode('utf-8')) and self.route!=None:
        if (line[-5:]=='TULOS' or line[-8:]=='RESULTAT') and self.route!=None:
            self.intervals = int(line.replace("[", " ").replace("]", "    ")[:-9].split(".")[-2].split()[-1])

        ind = line.replace("_", " ").replace(",", " ").rfind("KM ")
        if ind>=0:

            # Flag for night and technical tracks
            #if line.find("YÖ")>=0:
            if line.find("YÖ")>=0:
                self.track_type = 'NIGHT';
            #elif line.find("TEK")>=0:
            elif line.find("TEK")>=0:
                self.track_type = 'TECHNICAL';
            else:
                self.track_type = 'NORMAL';

            try:
                num=''.join(i for i in line[:ind].replace("_", " ").split()[-1] if (i.isdigit() or i in ('.',','))).replace(",",".").rstrip('.')
                self.route = float(num)
                self.routeline = line
                self.routetag = re.sub(' /$', '', ' '.join(line[:ind].split()[:-1]).replace(" -", ""));
                print(self.route, self.track_type)
            except:
                print("error with num at %s: num=%s" % (self.header, num))
                print(line)
                sys.exit()
            return 'Routeline'

        #  name line
        columns = line.replace(".","").split()
        if len(columns)>3 and columns[0].isdigit() and columns[1].replace("-","").isalpha() and columns[2].replace("-","").isalpha() and columns[-1].isdigit():
            self.nameline = line
            return 'Nameline'

    pass

class IltarastitRRParser(RouteParser):

    def newline(self, line):
        nameline = False
        routeline = False
        num = ""
        #if line.find('SPRINTTI'): self.track_type = 'SPRINT'

        if (line.find('OMA')>=0 or line.find('0MA')>=0) and len(line.split())<10: # and line.find('AJAT')>=0: # or line.find('RATA')>=0:
            self.route = None
            return 'DummyRouteLine'

        if line.find('TUKIREITTI')>=0 and len(line.split())<10:
            self.route=None
            return 'DummyRouteLine'

        if line.find('TR, ')>=0 and len(line.split())<10:
            self.route=None
            return 'DummyRouteLine'

        if line.find('RR, ')>=0 and len(line.split())<10:
            self.route=None
            return 'DummyRouteLine'

        if line.find('RASTIREITTI')>=0 and len(line.split())<10:
            self.route=None
            return 'DummyRouteLine'

        #if line.find('YÖ')>=0 and len(line.split())<10:
        #    self.route=None
        #    return 'DummyRouteLine'
        if line.find('VÄLIAJAT')>=0 and line.find('YÖ')>=0:
            self.permanent_night = True
            return 'DummyRouteLine'

        if line.find("KÄYRÄ")>=0 and len(line.split())<10:
            self.route=None
            return 'DummyRouteLine'

        if line.find("E-RATA")>=0 and len(line.split())<10:
            self.route=None
            return 'DummyRouteLine'

        if line[-5:]=='TULOS': # and self.route != None:
            try:
                self.intervals = int(line.replace("[", " ").replace("]", " ")[:-6].split(".")[-2].split()[-1])
            except:
                self.intervals = 0

        line += " ";
        ind = max(line.find("RATA"), line.replace("_", " ").replace(",", " ").upper().find("KM "))
        # separator line
        if ind>=0 and line.find("PYORA")<0 and line.find("PYÖRÄ")<0 and line.find("KM")>=0:
            try:
                try:
                    self.route = float(line[:ind].split()[-1].replace(",", "."));
                except:
                    try:
                        if ind==1:
                            self.route = self.routes[line[ind+5]]
                        else:
                            self.route = self.routes[line[ind-2]]
                    except: 
                        num=''.join(i for i in line[:ind].replace("_", " ").split()[-1] if (i.isdigit() or i in ('.',','))).replace(",",".")
                        self.route = float(num)
                self.routeline = line
                self.routetag = ' '.join(line[:ind].replace("_", " ").split()[:-1])
                self.track_type = 'NIGHT' if (self.permanent_night or line.find("YÖ")>=0) else 'NORMAL';
                if line.find("VAIKEA")>=0:
                    self.routetag = "VAIKEA"
                if line.find("HELPPO")>=0:
                    self.routetag = "HELPPO"
                self.routetag = "%.2f %s" % (self.route, self.routetag)
                #if len(self.routetag)<80:
                #    print "#TAG: ", self.route, self.routetag
                print("UPDATE Tracks SET track_length_km=%.2f, track_tag='%s' WHERE track_id=(SELECT track_id FROM (SELECT * FROM Tracks) AS dmy WHERE track_contest_id=(SELECT contest_id FROM Contests where contest_name='ILTARASTIT/RR' AND contest_date='%s') LIMIT 1 OFFSET %u);" % (self.route, self.routetag, '%04u-%02u-%02u' % (int(self.date.split(".")[2]), int(self.date.split(".")[1]), int(self.date.split(".")[0])), self.track_bug_count))
                self.track_bug_count += 1
                return 'Routeline'

            except:
                print("error with num at %s: num=%s" % (self.header, num))
                print(line)
                sys.exit()
            routeline = True

        if (self.route != None and line[-16:]=="RASTIVÄLIEN AJAT"):
            self.route = None
            return 'DummyRouteLine'

        #  name line
        columns = line.replace(".","").split()
        if len(columns)>3 and columns[0].isdigit() and columns[1].replace("-","").isalpha() and columns[2].replace("-","").isalpha() and columns[-1].isdigit():
            self.nameline = line
            self.routeline = None
            nameline = True
        if routeline:
            return 'Routeline'
        if nameline:
            return 'Nameline'


class BulkParser(RouteParser):

    def newline(self, line):
        nameline = False
        routeline = False

        if line[-5:].upper()=='TULOS': # and self.route != None:
            try:
                self.intervals = len(line.split())-4
                print("Number of intervals: %i" % self.intervals)
            except:
                self.intervals = 0
            return 'DummyRouteLine'

        line += " ";
        ind = line.replace("_", " ").replace(",", ".").upper().rfind("KM ")
        # separator line
        if ind>=0:
            try:
                self.route = float(line[:ind].split()[-1].replace(",", "."));
                self.routeline = line
                self.routetag = ' '.join(line[:ind].replace("_", " ").split()[:-1])
                self.routetag = "%.2f %s" % (self.route, self.routetag)
                self.track_bug_count += 1
                print("Track length: %.1f km (%s)" % (self.route, self.routetag))
                return 'Routeline'
            except:
                print("error with num at %s: num=%s" % (self.header, num))
                print(line)
                sys.exit()
            routeline = True

        #  name line
        columns = line.replace(".","").split()
        if len(columns)>3 and columns[0].isdigit() and columns[1].replace("-","").isalpha() and columns[2].replace("-","").isalpha() and columns[-1].isdigit():
            self.nameline = line
            self.intervalline = line
            self.routeline = None
            nameline = True

        if routeline:
            return 'Routeline'
        if nameline:
            return 'Nameline'

    def parse(self, urlparser):
        #print self, urlparser
        self.urlparser = urlparser(self.url);
        self.text = self.urlparser.getText().upper().splitlines()
        waitforintervals = False
        lineno = 0
        while lineno<len(self.text):
            line = self.text[lineno].upper()
            if len(line)>0:
                if self.newline(line)=='Nameline' and self.route is not None:
                    self.handleNameline()
                    self.handleintervalline()

            # move to next line
            lineno += 1

    def handleNameline(self):
        line = self.nameline.replace(".","");
        columns = line.split()
        if len(columns)>3 and columns[0].isdigit() and columns[1].replace("-","").isalpha() and columns[2].replace("-","").isalpha() and columns[-1].isdigit():
            self.firstname  = columns[2]
            self.familyname = columns[1]
            self.fulltime   = self.parseseconds(columns[-1])
            return True
        else:
            return False

    def parseintervalline(self):
        line = self.intervalline.replace(".","")
        columns = line.replace("-", " ").split()
        interval_secs = [self.parseseconds(c) for c in columns[4:-1:2]];
        secs = sum(interval_secs)
        return line, columns, interval_secs, secs

class RegexParser(RouteParser):
    def parse(self, urlparser):
        self.printstr("parsing: %s" % self)
        self.urlparser = urlparser(self.url);
        self.text = self.urlparser.getText().upper().splitlines()

        waitforintervals = False
        self.intervals = None
        self.route = None
        self.track_type = 'NORMAL';
        for line in [l.upper() for l in self.text]:
            # Route tags and lengths
            m = re.search(r'(?P<tag>\w*)[\s\:]+?(?P<len>[\d\.\,]+)\s?KM', line)
            if m is not None:
                tag = m.groupdict().get('tag')
                self.routes[tag]=float(m.groupdict().get('len').replace(",", "."));
            # Uninteresting ones
            m = re.findall('TILANNE', line)
            if len(m)>0:
                self.route = None
                self.intervals = None

            # Interesting ones
            m = re.findall('RASTIVÄLIEN', line)
            if len(m)>0:

                # Default track type
                self.track_type='NORMAL';

                # Check out night tracks
                m2 = re.findall('-YÖ', line)
                if len(m2)>0:
                    self.track_type='NIGHT';
                    line = line.replace('-YÖ', '');

                # Check out night tracks
                m2 = re.findall('YÖ-', line)
                if len(m2)>0:
                    self.track_type='NIGHT';
                    line = line.replace('YÖ-', '');

                # Check out sprint tracks
                m2 = re.findall('(SPRINT|SPRT)', line)
                if len(m2)>0:
                    self.track_type='SPRINT';
                    #line = line.replace('YÖ-', '');


                # A RASTIVÄLIEN AJAT
                print("line: ", line)
                route = line.split()[0]
                try:
                    self.route = float(re.sub('[a-zA-Z]', '', route))
                except:
                    self.route = self.routes[route];
                self.routetag = "%.2f (%s)" % (self.route, route)
                print(self.routetag)

            # Intervals line
            m = re.search('.*SIJA.*NIMI.*\.(?P<intervals>.*)\.TULOS', line)
            if m is not None and self.route is not None:
                print(m.groupdict())
                self.intervals = int(m.groupdict().get('intervals')) ## Sometimes add -1
                print(self.route, self.intervals)

            # Seconds parser function
            sep = ':'
            parseseconds = lambda l: 3600*(0 if len(l.split(sep))<3 else int(l.split(sep)[-3]))+60*(0 if len(l.split(sep))<2 else int(l.split(sep)[-2]))+int(l.split(sep)[-1])

            # Names line
            if self.intervals is not None:
                sep = ':';
                #search_string = r'\d+\.(?P<nimi>[A-ZÅÄÖ\xc5\xc4\xd6\\-]* [A-ZÅÄÖ\xc5\xc4\xd6\\-]*)(?:(?:\d+\.)(?P<value>(?:\d+\:)?(?:\d+\:)?\d\d)){0}.*(?P<total>(?:\d+\:)?(?:\d\d\:\d\d))$';
                search_string = r'\d+\.(?P<nimi>[A-ZÀ-ÿÅÄÖ\xc5\xc4\xd6\\-]* [A-ZÀ-ÿÅÄÖ\xc5\xc4\xd6\\-]*)(?:(?:\d+\.)(?P<value>(?:\d+\:)?(?:\d+\:)?\d\d)){0}(?:.*?)(?P<total>(?:\d+\:)?(?:\d\d\:\d\d))$';
                m = re.findall(search_string.replace('{0}', '{%i}' % self.intervals), line);
                if len(m)>0:
                    for n in range(1, self.intervals+1):
                        print(n, re.findall(search_string.replace('{0}', '{%i}' % n), line))
                    self.interval_times_str = [re.findall(search_string.replace('{0}', '{%i}' % n), line)[0][1] for n in range(1, self.intervals+1)];
                    fulltime_sec = sum([parseseconds(t) for t in self.interval_times_str]);
                    # Artificial nameline
                    namestr = re.findall(search_string.replace('{0}', '{%i}' % n), line)[0][0]
                    self.nameline = "0. %s %s %s" % (namestr, " ".join(self.interval_times_str), time.strftime('%H.%M.%S', time.gmtime(fulltime_sec)));
                    print(namestr)
                    print(self.handleNameline())
                    self.intervalline = " ".join(["0-%s" % self.interval_times_str[k] for k in range(self.intervals)]);
                    print(self.handleintervalline())
                    # Artificial intervalline

class RegexParser2(RouteParser):
    def parse(self, urlparser):
        print("RegexParser2...")
        self.printstr("parsing: %s" % self)
        self.urlparser = urlparser(self.url);
        self.text = self.urlparser.getText().upper().splitlines()

        waitforintervals = False
        self.intervals = None
        self.route = None
        self.track_type = 'NORMAL';
        for lcnt in range(len(self.text)):
            line = self.text[lcnt].upper();
            if lcnt<len(self.text)-1:
                nextline = self.text[lcnt+1].upper();

            # Route tags and lengths
            m = re.search(r'(?P<tag>[\S\s]*?)[\s\:]+?(?P<len>[\d\.\,]+)\s?KM', line)
            if m is not None:
                tag = m.groupdict().get('tag')#.replace(' ', '.');
                self.routes[tag]=float(m.groupdict().get('len').replace(",", "."));

            # Uninteresting ones
            m = re.findall('TILANNE', line)
            if len(m)>0:
                self.route = None
                self.intervals = None

            # Interesting ones
            m = re.findall('VÄLIAJAT$', line)

            if len(m)>0:
                print("Found VÄLIAJAT: ", line)
                if line.split()[0] in ['RR', 'TR']:
                    self.route = None
                    self.intervals = None
                else:
                    # B RASTIVÄLIAJAT
                    self.track_type = 'NIGHT' if line.find("YÖ")>=0 else 'SPRINT' if line.find("SPRT")>=0 else 'NORMAL';
                    line = line.replace('-YÖ', '').replace('YÖ-', '');
                    #self.route = self.routes[line.split()[0]];
                    key = ''.join(line.split()[:-1]);
                    if key in self.routes.keys():
                      self.route = self.routes[''.join(line.split()[:-1])];
                      #self.routetag = "%.2f (%s%s)" % (self.route, 'YÖ-' if self.track_type=='NIGHT' else '', line.split()[0])
                      self.routetag = "%.2f (%s%s)" % (self.route, 'YÖ-' if self.track_type=='NIGHT' else '', ''.join(line.split()[:-1]))
                      print("Route: ", self.route, " / ", self.routetag)
                    else:
                      self.route = None
                      self.intervals = None

            # Intervals line
            m = re.search('.*SIJA.*NIMI.*\.(?P<intervals>.*)\.(|RATA)TULOS', line)
            if m is not None and self.route is not None:
                #print("Found SIJA/NIMI/TULOS: ", self.route, " / ", line)
                self.intervals = int(m.groupdict().get('intervals'))
                print('route+intervals: ', self.route, self.intervals, m.groupdict())

            # Seconds parser function
            parseseconds = lambda l: 3600*(0 if len(l.split(':'))<3 else int(l.split(':')[-3]))+60*(0 if len(l.split(':'))<2 else int(l.split(':')[-2]))+int(l.split(':')[-1])

            # Names line
            if self.intervals is not None:
                search_string      = r'\d+\.(?P<nimi>[A-ZÀ-ÿ\-]+ [A-ZÀ-ÿ\-]+)(?:(?:\d+\.)(?P<value>(?:\d+\:)?(?:\d+\:)?(?:\d+\:)?\d\d)){0}.*(?P<total>(?:\d+\:)?(?:\d\d\:\d\d))$';
                #search_string      = r'\d+\.(?P<nimi>[A-ZÅÄÖ\-]+ [A-ZÅÄÖ\-]+)(?:(?:\d+\.)(?P<value>(?:\d+\:)?(?:\d+\:)?(?:\d+\:)?\d\d)){0}.*(?P<total>(?:\d+\:)?(?:\d\d\:\d\d))$';
                #search_string      = r'\d+\.(?P<nimi>[(?i)(?:(?![×Þß÷þø])[a-zÀ-ÿ])\-]+ [(?i)(?:(?![×Þß÷þø])[a-zÀ-ÿ])\-]+)(?:(?:\d+\.)(?P<value>(?:\d+\:)?(?:\d+\:)?(?:\d+\:)?\d\d)){0}.*(?P<total>(?:\d+\:)?(?:\d\d\:\d\d))$';
                search_string_next = r'(?:(?:\d+\.)(?P<value>(?:\d+\:)?(?:\d+\:)?\d\d)){0}.*$';
                try:
                    #print(line)
                    #print("search_string: ", search_string.replace('{0}', '{%i}' % (self.intervals-1)));
                    m = re.findall(search_string.replace('{0}', '{%i}' % (self.intervals-1)), line);
                    if len(m)>0:
                        # Parse intervals from the next line
                        self.interval_times_str = [re.findall(search_string_next.replace('{0}', '{%i}' % n), nextline)[0] for n in range(1, self.intervals+1)];
                        fulltime_sec = sum([parseseconds(t) for t in self.interval_times_str]);
                        # Artificial nameline
                        namestr = re.findall(search_string.replace('{0}', '{%i}' % 1), line)[0][0]
                        self.nameline = "0. %s %s %s" % (namestr, ' '.join(self.interval_times_str), time.strftime('%H.%M.%S', time.gmtime(fulltime_sec)));
                        print('name: ', namestr)
                        print(self.handleNameline())
                        print(self.interval_times_str)
                        # Artificial intervalline
                        self.intervalline = ' '.join(["0-%s" % self.interval_times_str[k] for k in range(self.intervals)]).replace(":", ".");
                        print(self.intervalline)
                        print(self.handleintervalline())
                except:
                    continue

class IltarastitHS3Parser(RouteParser):
    def parse(self, urlparser):
        linecnt = 0;
        self.printstr("parsing: %s" % self)
        self.urlparser = urlparser(self.url);
        self.text = self.urlparser.getText().upper().replace('LOPPUAIKA', 'LOPPUAIKA\n').splitlines()
        #self.text = re.sub(r'([\d-]+)([\p{L}\ ]+)(\d)', '\\1RIVINVAIHTO\\2\\3', self.urlparser.getText().upper().replace('LOPPUAIKA', 'LOPPUAIKA\n')).replace('RIVINVAIHTO', '\n').splitlines()
        #print self.text
 
        waitforintervals = False
        self.intervals = None
        self.route = None
        self.track_type = 'NORMAL';

        # Seconds parser function
        parseseconds = lambda l: 3600*(0 if len(l.split(':'))<3 else int(l.split(':')[-3]))+60*(0 if len(l.split(':'))<2 else int(l.split(':')[-2]))+int(l.split(':')[-1])
    
        for lcnt in range(len(self.text)):
            line = self.text[lcnt].upper();
            if lcnt<len(self.text)-1:
                nextline = self.text[lcnt+1].upper();

            # Route tags and lengths
            if(len(line)>0):
                pattern1 = r'[\d-]+(?P<name>(?:[\p{L}A-ZÅÄÖ\xc4\xc5\xc6\-\ ]*))(?P<alltimes>(?:(?:\d+)\-(?:(?:\d{1,2}\:)?(?:\d{1,2}\:)?(?:\d{1,2}\:)?\d\d)(?:\d+)\-(?:(?:\d{1,2}\:)?(?:\d{1,2}\:)?\d\d))+)(?P<finaltime>(?:\d{1,2}\:)?(?:\d{1,2}\:)?\d\d)'
                #pattern2 = r'(?P<tag>RATA [\.\d]+[VH]?)([\/\ ]*)(?P<length>[\.\d]*)(?:[\ ]*(KM)?)'
                pattern2 = r'(?P<tag>(?:[A-Z]-)?RATA [\.\dABCDEF]*[VH]?)([\/\ ]*)(?P<length>[\.\d]*)(?:[\ ]*(KM)?).*?(?P<intervals>\d+)\(\d+\)LOPPUAIKA'
                #pattern2 = r'(?P<tag>(?:[A-Z]-)?RAT(?:A?) [\.\d]*[VH]?)([\/\ ]*)(?P<length>[\.\d]*)(?:[\ ]*(KM)?).*?(?P<intervals>\d+)\(\d+\)LOPPUAIKA'
                #pattern2 = r'(?P<tag>(?:[A-Z]-)?RAT(?:A?) [\.\d]*[VH]?)([\/\ ]*)(?P<length>[\.\d]*)(?:[\ ]*(KM)?).*?(?P<intervals>\d+)\(\d+\)LOPPUAIKA'
                pattern = '(%s|%s)' % (pattern1, pattern2)
                #print pattern
                #pattern = r'(\d+(?P<name>(?:[A-Z\xc4\xc5\xc6\-\ ]*))(?P<alltimes>(?:(?:\d+)\-(?:(?:\d{1,2}\:)?(?:\d{1,2}\:)?\d\d)(?:\d+)\-(?:(?:\d{1,2}\:)?(?:\d{1,2}\:)?\d\d))+)(?P<finaltime>(?:\d{1,2}\:)?(?:\d{1,2}\:)?\d\d)|RATA(?P<tag>[ \d]*)(?P:\/)(?P<length>[ \.0-9]* KM))'
                #print linecnt, line
                linecnt += 1
                #if linecnt==18:
                #    print linecnt, line
                #    sys.exit()
                #    sys.exit()
                x = re.findall(pattern, line);
                regex = re.compile(pattern, re.IGNORECASE)
                for match in regex.finditer(line):
                    if match.group('tag') is not None:
                        tag = match.group('tag');
                        print("TRACK-TAG! ", tag, linecnt, len(line), line[0:32], len(match.group('length')), len(match.group('intervals')))
                        if match.group('length') is None or len(match.group('length'))==0:
                            self.intervals = None
                            self.route = None
                            ## hack for 2016-08-01
                            if self.url=='http://online.helsinginsuunnistajat.fi/valiajat?c=IR_2016_08_01' and (tag=='RATA 4V' or tag=='RATA 5'):
                                self.route = float(filter(lambda x: x.isdigit(), tag));
                                self.intervals = int(match.group('intervals'))
                                self.track_type = 'NORMAL';
                                self.routetag = tag
                        else:
                            length = match.group('length');
                            self.route = float(length)
                            self.intervals = int(match.group('intervals'))
                            self.track_type = 'NORMAL'
                            self.routetag = tag
                            print(">>> %s (%s km), %i" % (self.routetag, self.route, self.intervals))
                    if match.group('alltimes') is not None and self.route is not None:
                        final_seconds = parseseconds(match.group('finaltime'));
                        interval_times_str = [re.findall('(?P<time>(?:\d+\:)?\d+\:\d\d)\d', x)[0] for x in match.group('alltimes').split('-')[1::2]]
                        if(len(interval_times_str)==self.intervals):
                          self.interval_times_int = [parseseconds(ii) for ii in interval_times_str]
                          print("%s, %s: %s [%s] / final: %s (%i)" % (self.route, self.intervals, match.group('name'), ', '.join(interval_times_str), match.group('finaltime'), final_seconds))
                          if(sum(self.interval_times_int) != final_seconds):
                              print("ERROR: ", interval_times_str, match.group('finaltime'), ":", sum(self.interval_times_int), " != ", final_seconds)
                              #print 'intervals: ', self.intervals
                          namestr = match.group('name')
                          if namestr.find(' JA ')<0:
                              self.nameline = "0. %s %s %s" % (namestr, " ".join(interval_times_str), time.strftime('%H.%M.%S', time.gmtime(sum(self.interval_times_int))));
                              #print 'name: ', namestr
                              dmy=self.handleNameline()
                              #print 'handleNameline: ', dmy 
                              # Artificial interval line
                              if dmy:
                                  self.intervalline = " ".join(["0-%s" % interval_times_str[k] for k in range(self.intervals)]).replace(":", ".");
                                  #print 'intervalline: ', self.intervalline
                                  dmy = self.handleintervalline();
                                  #print 'handleintervalline: ', dmy

