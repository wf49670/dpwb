#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
  ppscan.py
  MIT license (c) 2018 Asylum Computer Services LLC
"""
import re
import sys
import os
import argparse
from time import gmtime, strftime

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# class Cget
# gets a character at a time from the working buffer.
# at EOL with some text, returns a space
# at EOL with no text, returns '\n'
# at EOF returns -1
class Cget(object):
    def __init__(self, buf):
        self.wb = buf
        self.cp = 0
        self.ln = 0
        self.pcp = 0
        self.pln = 0
    # getc returns one character and advances
    def getc(self):
        if self.ln == len(self.wb):
            return -1  # no more text
        # are we at the end of a line?
        if self.cp == len(self.wb[self.ln]):
            # yes. was there some text already on this line
            if self.cp > 0:
                # yes there was. return a space
                ch = " "
            else:
                # nope. this is a blank line
                ch = '\n'
            self.ln += 1
            self.cp = 0
        else:
            ch = self.wb[self.ln][self.cp]
            self.cp += 1
        self.pcp = self.cp  # in case there is peek-ahead,
        self.pln = self.ln  # start here
        return ch
    # peeks ahead independently of the main ln, cp
    # can be called repeatedly
    def peekc(self):
        if self.pln == len(self.wb):
            return -1  # no more text
        # are we at the end of a line?
        if self.pcp == len(self.wb[self.pln]):
            # yes. was there some text already on this line
            if self.pcp > 0:
                # yes there was. return a space
                ch = " "
            else:
                # nope. this is a blank line
                ch = '\n'
            self.pln += 1
            self.pcp = 0
        else:
            ch = self.wb[self.pln][self.pcp]
            self.pcp += 1
        return ch
    # zero based
    def where(self):
        w = (self.ln, self.cp)  # line and character position
        return w
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# class Stack. traditional FIFO stack
class Stack:
    def __init__(self):
        self.items = []
    def isEmpty(self):
        return self.items == []
    def push(self, item):
        self.items.append(item)
    def pop(self):
        return self.items.pop()
    def peek(self):
        return self.items[len(self.items) - 1]
    def size(self):
        return len(self.items)
    def show(self):
        return self.items
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
class Ppscan(object):

    def __init__(self, args):
        self.srcfile = args['infile']
        self.outfile = args['outfile']
        self.desc = args['desc']
        self.verbose = args['verbose']
        self.VERSION = "2018.04.02"
        self.encoding = ""
        self.wb = []  # list: one entry per line of source file
        self.wl = {}  # wordlist in a map, from wordfile.txt
        self.wlf = {}  # first letter removed
        self.wll = {}  # last letter removed
        self.msgs = []  # messages file
        self.rp = []  # report list
        self.OSQ = '\u231c'
        self.CSQ = '\u231d'
        self.bothsq = False # true if both straight and curly quotes found
        self.OP = r"(?:^|[\s‘“—\-_])"  # define left edge of word
        self.CP = r"(?:[ !;:'\".,\?'’—\-\s]|$)" # define right edge of a word
        self.wfile = args['lang']
        self.dictloc = "wordlists/master." + self.wfile # dictonary wordlist file
        self.tcqlocs = []  # temporary close quote locations
        self.stcqlocs = []  # saved temporary close quote locations

    # display (fatal) error and exit
    def fatal(self, message):
        sys.stderr.write("fatal: " + message + "\n")
        exit(1)

    # load file from specified source file into working buffer
    # accepts UTF-8 with or without BOM
    # list of lines has no terminators (LF/CR)
    def loadFile(self):
        try:
            wbuf = open(self.srcfile, "r", encoding='UTF-8').read()
            self.encoding = "UTF-8"
            self.wb = wbuf.split("\n")
            # remove BOM on first line if present
            t = ":".join("{0:x}".format(ord(c)) for c in self.wb[0])
            if t[0:4] == 'feff':
                self.wb[0] = self.wb[0][1:]
        except UnicodeDecodeError:
            wbuf = open(self.srcfile, "r", encoding='Latin-1').read()
            self.encoding = "Latin-1"
            wbuf = wbuf.encode('utf8').decode('latin-1')
            self.wb = wbuf.split("\n")
        except Exception as e:
            self.fatal(
                "loadFile: cannot open source file {}\n{}".format(self.srcfile, e))
        self.wb = [s.rstrip() for s in self.wb]

    # load a wordlist from an available dictionary
    def loadDict(self):
        my_file = os.path.abspath(self.dictloc)
        if os.path.isfile(my_file):
            tmp = open(my_file, "r", encoding="utf-8").read()
            twl = tmp.split("\n")
            twl = [s.rstrip() for s in twl]
            # build dictionaries:
            #  wl   complete words
            #  wlf  words with first letter removed
            #  wll  words with last letter removed
            for word in twl:
                if not word.startswith('#'):  # comments, if any
                    self.wl[word] = '1'
                    self.wlf[word[1:]] = '1'
                    self.wll[word[:-1]] = '1'
        else:
            self.fatal("no dictionary file found at {}".format(my_file))

    def check_mixed(self):
        curly = False
        straight = False
        for line in self.wb:
            if re.search(r"[\"']", line):
                straight = True
            if re.search(r"[“”‘’]", line):
                curly = True
        if straight and curly:
            self.bothsq = True

    def internal_contractions(self):
        re1 = re.compile(r"([a-z])’([a-z])", re.IGNORECASE)
        re2 = re.compile(r"([a-z])’([a-z])’([a-z])", re.IGNORECASE)
        re3 = re.compile(r"([a-z])’([a-z])’([a-z])’([a-z])", re.IGNORECASE)
        for i, _ in enumerate(self.wb):
            self.wb[i] = re3.sub(r"\1"+self.CSQ+r"\2" +
                                 self.CSQ+r"\3"+self.CSQ+r"\4", self.wb[i])
            self.wb[i] = re2.sub(r"\1"+self.CSQ+r"\2" +
                                 self.CSQ+r"\3", self.wb[i])
            self.wb[i] = re1.sub(r"\1"+self.CSQ+r"\2", self.wb[i])
        return

    def closing_accept(self):
        fmap = {}
        rlist = []
        re1 = re.compile(r"{}(\w+’){}".format(self.OP, self.CP))
        for i, line in enumerate(self.wb):
            m = re1.finditer(line)
            if m:
                # keep track of how frequently the word occurs
                for _, t in enumerate(m):
                    wd = t.group(1)
                    if wd in fmap:
                        fmap[wd] += 1
                    else:
                        fmap[wd] = 1
        # go through the map and find entries for which if the final apostrophe
        # is dropped, it is not a word (∴ it must be a contraction)
        for tw in fmap:
            if tw[:-1].lower() in self.wl:
                # base in in dictionary. It might be a close single quote
                # print("in dict: {} {}".format(tw, fmap[tw]))
                # accept if used very frequently
                if fmap[tw] > 5:
                    # print(tw, fmap[tw])
                    rlist.append(tw)
            else:
                # it is not in dictionary. add to replace list
                # print("not in dict: {} {}".format(tw, fmap[tw]))
                rlist.append(tw)
        for i, _ in enumerate(self.wb):
            for wd in rlist:
                wd1 = wd[:-1]+self.CSQ
                self.wb[i] = re.sub("({}){}({})".format(
                    self.OP, wd, self.CP), r"\1{}\2".format(wd1), self.wb[i])

    def opening_accept(self):
        fmap = {}
        rlist = []
        re1 = re.compile(r"{}(’\w+){}".format(self.OP, self.CP))
        for i, line in enumerate(self.wb):
            m = re1.finditer(line)
            if m:
                # keep track of how frequently the word occurs
                for _, t in enumerate(m):
                    wd = t.group(1)
                    if wd in fmap:
                        fmap[wd] += 1
                    else:
                        fmap[wd] = 1
        # go through the map and find entries for which if the lead apostrophe
        # is dropped, it is not a word (∴ it must be a contraction)
        for tw in fmap:
            if tw[1:].lower() in self.wl:
                # base in in dictionary. It might be an open single quote
                # print("in dict: {} {}".format(tw, fmap[tw]))
                # accept if used very frequently
                if fmap[tw] > 5:
                    # print(tw, fmap[tw])
                    rlist.append(tw)
            else:
                # it is not in dictionary. add to replace list
                # print("not in dict: {} {}".format(tw, fmap[tw]))
                rlist.append(tw)
        for i, _ in enumerate(self.wb):
            for wd in rlist:
                wd1 = self.CSQ+wd[1:]
                self.wb[i] = re.sub("({}){}({})".format(
                    self.OP, wd, self.CP), r"\1{}\2".format(wd1), self.wb[i])

    # limit common forms to those that do not become a word when the
    # apostrophe is removed. It might be the start or end of a single quoted phrase
    def common_forms(self):
        commons_lead = {
            "’em", "’a’", "’n’", "’twill", "’twon’t", "’twas", "’tain’t", "’taint", "’twouldn’t",
            "’twasn’t", "’twere", "’twould", "’tis", "’twarn’t", "’tisn’t", "’twixt", "’till",
            "’bout", "’casion", "’shamed", "’lowance", "’n", "’s", "’d", "’m", "’ave",
            "’cordingly", "’baccy", "’cept", "’stead", "’spose", "’chute", "’im",
            "’u’d", "’tend", "’rickshaw", "’appen", "’oo", "’urt", "’ud", "’ope", "’ow",
            # higher risk follows
            "’cause", "’way"
        }
        commons_tail = {
            "especial’", "o’", "t’", "ag’in’", "ol’", "tha’", "canna’", "an’", "d’",
            "G’-by", "ha’", "tak’", "th’", "i’", "wi’", "yo’", "ver’", "don’", "jes’",
            "aroun’", "wan’", "M’sieu’", "nuthin’"
        }
        commons_both = {
            "’cordin’"
        }
        for i, _ in enumerate(self.wb):
            for _, common in enumerate(commons_lead):
                c2 = re.sub("’", self.CSQ, common)
                self.wb[i] = re.sub(r"({}){}({})".format(
                    self.OP, common, self.CP), r"\1{}\2".format(c2), self.wb[i])
                # leading capital tests
                common = "{}{}{}".format(
                    common[0], common[1].upper(), common[2:])
                c2 = re.sub("’", self.CSQ, common)
                self.wb[i] = re.sub(r"({}){}({})".format(
                    self.OP, common, self.CP), r"\1{}\2".format(c2), self.wb[i])
            for _, common in enumerate(commons_tail):
                c2 = re.sub("’", self.CSQ, common)
                self.wb[i] = re.sub(r"({}){}({})".format(
                    self.OP, common, self.CP), r"\1{}\2".format(c2), self.wb[i])
                # leading capital tests
                common = "{}{}".format(common[0].upper(), common[1:])
                c2 = re.sub("’", self.CSQ, common)
                self.wb[i] = re.sub(r"({}){}({})".format(
                    self.OP, common, self.CP), r"\1{}\2".format(c2), self.wb[i])
            for _, common in enumerate(commons_both):
                c2 = re.sub("’", self.CSQ, common)
                self.wb[i] = re.sub(r"({}){}({})".format(
                    self.OP, common, self.CP), r"\1{}\2".format(c2), self.wb[i])
                # leading capital tests
                common = "{}{}{}".format(
                    common[0], common[1].upper(), common[2:])
                c2 = re.sub("’", self.CSQ, common)
                self.wb[i] = re.sub(r"({}){}({})".format(
                    self.OP, common, self.CP), r"\1{}\2".format(c2), self.wb[i])

    # proper names
    #
    def proper_names(self):
        nmap = {}
        pnlist = []
        # capitalized word that ends in an apostrophe
        re0 = re.compile(r"{}([A-Z]\w+’){}".format(self.OP, self.CP))
        for i, line in enumerate(self.wb):
            hits = re0.finditer(line)
            for _, t in enumerate(hits):
                # keep track of how frequently the word+apost occurs
                wd = t.group(1)
                if wd not in self.wl and wd.lower() not in self.wl:
                    if wd in nmap:
                        nmap[wd] += 1
                    else:
                        nmap[wd] = 1
        for z in nmap:
            if nmap[z] >= 4:
                pnlist.append(z)
        for z in pnlist:
            for i, line in enumerate(self.wb):
                rz = re.sub("’", self.CSQ, z)
                self.wb[i] = re.sub(z, rz, self.wb[i])

    # logic here is to strip off the last two characters
    # if what's left is a dictionary word, then conclude it is
    # plural possessive
    def plural_possessive(self):
        re9 = re.compile(r"{}(\w+)s’{}".format(self.OP, self.CP))
        for i, line in enumerate(self.wb):
            hits = re9.finditer(line)
            for _, hit in enumerate(hits):
                if hit.group(1) in self.wl or hit.group(1).lower() in self.wl:
                    self.wb[i] = re.sub(hit.group(1)+"s’",
                                        hit.group(1)+"s"+self.CSQ, self.wb[i])

    # logic here is if it's a word with an opening and closing quote, then
    # conclude that they are quotes.
    def single_words(self):
        re9 = re.compile(r"(‘\w+’)")
        for i, line in enumerate(self.wb):
            hits = re9.finditer(line)
            for _, hit in enumerate(hits):
                self.wb[i] = re.sub(hit.group(1), self.OSQ +
                                    hit.group(1)[1:-1] + self.CSQ, self.wb[i])

    # logic here is if it's two words with an opening and closing quote, then
    # conclude that they are in single quotes.
    # doesn't work if two words split over two lines, which generates a false positive
    def double_words(self):
        re9 = re.compile(r"(‘\w+\s\w+’)")
        for i, line in enumerate(self.wb):
            hits = re9.finditer(line)
            for _, hit in enumerate(hits):
                self.wb[i] = re.sub(hit.group(1), self.OSQ +
                                    hit.group(1)[1:-1] + self.CSQ, self.wb[i])

    def cont_quotes(self):
        empty = re.compile("^$")
        state = 0  # consider starting on a blank line
        lqc = rqc = 0
        for i, line in enumerate(self.wb):
            if state == 0 and not empty.match(line):
                # transition to non-blank line, i.e. first line of paragraph
                state = 1
                lqc = rqc = 0
                lqc = line.count("“")
                rqc = line.count("”")
                continue
            # another line in the paragraph
            if state == 1 and not empty.match(line):
                lqc += line.count("“")
                rqc += line.count("”")
                continue
            if state == 1 and empty.match(line):
                # transition from non-blank line to blank line
                lqc += line.count("“")
                rqc += line.count("”")
                if lqc == rqc:
                    # leaving a balanced paragraph
                    # look to see it this is closing a continued quote
                    if len(self.tcqlocs) >= 2:
                        for _, j in enumerate(self.tcqlocs):
                            self.wb[j] += "”"
                            # save those to be removed at end
                            self.stcqlocs.append(j)
                    del self.tcqlocs[:]  # temporary locs cleared
                    continue
                if lqc == rqc + 1:  # one more open than close double quote
                    self.tcqlocs.append(i-1)
                state = 0

    def undo_cont_quotes(self):
        for _, loc in enumerate(self.stcqlocs):
            where = self.wb[loc].rfind("”")  # take back the one we put on
            self.wb[loc] = self.wb[loc][:where] + self.wb[loc][where+1:]

    def deobfuscate(self):
        for i, _ in enumerate(self.wb):
            self.wb[i] = re.sub(self.OSQ, "‘", self.wb[i])
            self.wb[i] = re.sub(self.CSQ, "’", self.wb[i])

    # the bizarre code in this is to handle consecutive -ing replacements
    # without resorting to overlap=True in regex
    def truncated_g(self):
        gmap = {}
        re9 = re.compile(r"{}(\w+?in)’{}".format(self.OP, self.CP))
        for i, _ in enumerate(self.wb):
            m = re9.search(self.wb[i])
            while m:
                hg1 = m.group(1)
                testword = hg1 + 'g'
                if testword.lower() in self.wl:
                    self.wb[i] = re.sub(hg1+'’', hg1+self.CSQ, self.wb[i], 1)
                else:
                    # it isn't an -ing word but does it occur a lot?
                    if hg1 in gmap:
                        gmap[hg1] += 1
                    else:
                        gmap[hg1] = 1
                    # knock it out of the regex match
                    self.wb[i] = re.sub(hg1+'’', hg1+'\u274f', self.wb[i], 1)
                m = re9.search(self.wb[i])
            self.wb[i] = re.sub('\u274f', '’', self.wb[i])
        # print(gmap)
        # if a potential -ing word occurs 5 or more times, accept it.
        for k in gmap.keys():
            if gmap[k] >= 5:
                # we have something like "figgerin" or "gittin"
                # protect it (ouch)
                for i, _ in enumerate(self.wb):
                    self.wb[i] = re.sub(k+"’", k+self.CSQ, self.wb[i])
        return

    # main scanning routine
    def scan(self):
        sk = Stack()
        cg = Cget(self.wb)
        ch = cg.getc()
        while ch != -1: # EOF
            if ch == '“':  # open double quote
                if sk.size() > 0 and sk.peek() == '“':
                    # consecutive open dq
                    self.rp.append(
                        "[CODQ] consec open double quote {}".format(cg.where()))
                    ch = cg.getc()
                    continue
                sk.push(ch)
            if ch == '”':  # close double quote
                if sk.size() > 0 and sk.peek() == '“':
                    sk.pop()  # normal behavior
                else:
                    # close double quote without matching open quote
                    self.rp.append(
                        "[UCDQ] unbalanced close double quote {}".format(cg.where()))
                    ch = cg.getc()
                    continue
            if ch == '‘':  # open single quote
                if sk.size() > 0 and sk.peek() == '‘':
                    # consecutive open sq
                    self.rp.append(
                        "[COSQ] consec open single quote {}".format(cg.where()))
                    ch = cg.getc()
                    continue
                sk.push(ch)
            if ch == '’':  # close single quote
                if sk.size() > 0 and sk.peek() == '‘':
                    sk.pop()  # normal behavior
                else:
                    # close single quote without matching open quote
                    self.rp.append(
                        "[UCSQ] unbalanced close single quote {}".format(cg.where()))
                    ch = cg.getc()
                    continue
            if ch == '[':  # open brace
                if sk.size() > 0 and sk.peek == '[':
                    self.rp.append(
                        "[COPB] consecutive open brace {}".format(cg.where()))
                    ch = cg.getc()
                    continue
                sk.push(ch)
            if ch == ']':  # close brace
                if sk.size() > 0 and sk.peek() == '[':
                    sk.pop()  # the correct closing brace
                else:
                    self.rp.append(
                        "[CCLB] consecutive closing brace {}".format(cg.where()))
                    ch = cg.getc()
                    continue
            if ch == '(':  # open parenthesis
                if sk.size() > 0 and sk.peek() == '(':
                    self.rp.append(
                        "[COPN] consecutive open parenthesis {}".format(cg.where()))
                    ch = cg.getc()
                    continue
                sk.push(ch)
            if ch == ')':  # close parenthesis
                if sk.size() > 0 and sk.peek() == '(':
                    sk.pop()
                else:
                    self.rp.append(
                        "[CCPN] consecutive closing parenthesis {}".format(cg.where()))
                    ch = cg.getc()
                    continue
            # we are at the end of a paragraph
            # the stack should be empty
            # originally allowed for continued quotes but that can hide an unclosed
            # first speaker quote. retrieve that code with commit "master 470ce18"
            if ch == '\n':
                if sk.size() > 0:
                    ln, cp = cg.where()
                    ln -= 2
                    cp = len(self.wb[ln])
                    w2 = (ln, cp)
                    self.rp.append(
                        "[UNCP] unclosed punctuation {} {}".format(sk.show(), w2))
                    while sk.size() > 0:
                        sk.pop()
            ch = cg.getc()
        # here we have recorded all potential errors in list "rp"
        # now populate the working buffer
        rpr = list(reversed(self.rp))
        for _, item in enumerate(rpr):
            m = re.search(r"^\[(....)\] (.*?) \((\d+), (\d+)\)", item)
            if m:
                ac = m.group(1)
                tl = int(m.group(3))  # the line
                tp = int(m.group(4))  # the position on the line
                if self.desc:
                    self.wb[tl] = self.wb[tl][:tp] + \
                        '[@{}]'.format(ac) + self.wb[tl][tp:]
                else:
                    self.wb[tl] = self.wb[tl][:tp] + '@' + self.wb[tl][tp:]
        return

    # save wb to self.outfile
    def saveFile(self):
        empty = re.compile("^$")
        while empty.match(self.wb[-1]):
            del self.wb[-1]
        f1 = open(self.outfile, "w", encoding=self.encoding)
        if self.encoding == "UTF-8":
            f1.write('\ufeff')  # BOM mark
        f1.write("PP Workbench report generated by ppscan (version {})\r\n".format(self.VERSION))
        f1.write("source file: {}\r\n".format(os.path.basename(self.srcfile)))
        f1.write("using wordlist: {}\r\n".format(self.wfile))
        if self.bothsq:
            f1.write("WARNING: both straight and curly quotes found in text\r\n")
        f1.write("-"*80+"\r\n")
        for t in self.wb:
            f1.write("{:s}\r\n".format(t))  # use CR/LF
        # printout of errors
        if self.verbose:
            f1.write("-"*80+"\r\n")
            f1.write("\r\nerror details:\r\n")
            f1.write("   line  cp description\r\n")
            for _, item in enumerate(self.rp):
                m = re.search(r"^\[(....)\] (.*?)\((\d+), (\d+)\)", item)
                if m:
                    # mnemonic = m.group(1)
                    msg = m.group(2)
                    line = int(m.group(3))+1
                    cpos = int(m.group(4))
                    f1.write("  {:5d} {:3d} {:s}\r\n".format(line, cpos, msg))
            f1.write("-"*80+"\r\n")
            f1.write("\r\nmnemonic description within [@....] markup:\r\n")
            f1.write("  CODQ: consec open double quote\r\n")
            f1.write("  UCDQ: unbalanced close double quote\r\n")
            f1.write("  COSQ: consec open single quote\r\n")
            f1.write("  UCSQ: unbalanced close double quote\r\n")
            f1.write("  COPB: consecutive open brace\r\n")
            f1.write("  CCLB: consecutive closing brace\r\n")
            f1.write("  COPN: consecutive open parenthesis\r\n")
            f1.write("  CCPN: consecutive closing parenthesis\r\n")
            f1.write("  UNCP: unclosed punctuation\r\n")
        f1.write("-"*80+"\r\n")
        NOW = strftime("%Y-%m-%d %H:%M:%S", gmtime())+" GMT"
        f1.write("run completed: {}\r\n".format(NOW))
        f1.close()

    def run(self):
        self.loadFile()
        self.loadDict()
        self.common_forms()
        self.single_words()  # single words in single quotes
        self.double_words()  # two words in single quotes
        self.opening_accept()
        self.closing_accept()
        self.internal_contractions()
        self.cont_quotes()  # discover and protect continued quotes
        self.check_mixed()  # convert apostrophes as best we can
        self.proper_names()
        self.plural_possessive()
        self.truncated_g()
        self.scan()  # scan using the state machine
        self.undo_cont_quotes()
        self.deobfuscate()
        self.saveFile()

    def __str__(self):
        return "ppscan"

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--infile', help='input file', required=True)
    parser.add_argument('-o', '--outfile', help='output file', required=True)
    parser.add_argument('-d', '--desc',
                        help='described results flag', action='store_true')
    parser.add_argument('-v', '--verbose',
                        help='append list of errors', action='store_true')
    parser.add_argument('-l', '--lang', help='language specific wordlist', default='en_us')    
    args = vars(parser.parse_args())
    return args

def main():
    args = parse_args()
    ppscan = Ppscan(args)
    ppscan.run()

if __name__ == "__main__":
    sys.exit(main())
