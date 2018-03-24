#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ppspell.py for DP Post-processor's Workbench
license: MIT
version: 2018.03.23
"""

import re
import sys
import os
import argparse
from time import gmtime, strftime

class Ppspell(object):

    def __init__(self, args):
        self.srcfile = args['infile']
        self.outfile = args['outfile']
        self.debug = args['debug']
        self.goodfile = args['goodfile']
        self.wfile = args['wfile']
        self.NOW = strftime("%Y-%m-%d %H:%M:%S", gmtime())+" GMT"
        self.VERSION = "2018.03.23"
        self.root = os.path.dirname(os.path.realpath(__file__))
        self.wb = []
        self.encoding = ""
        self.wtext = {}  # words in the text
        self.wtext2 = {}  # unreduced words in the text
        self.ddict = {}  # good words (dict+supp)
        self.hyplist = []  # suspect hyphenation

    # display (fatal) error and exit
    def fatal(self, message):
        sys.stderr.write("fatal: "+message+"\n")
        exit(1)

    # print if options.debug is True
    def dprint(self, msg):
        if self.debug:
            print("DEBUG: {}".format(msg))

    # load file from specified source file
    def loadFile(self):
        try:
            wbuf = open(self.srcfile, "r", encoding='UTF-8').read()
            self.dprint("loaded UTF-8 file")
            self.encoding = "UTF-8"
            self.wb = wbuf.split("\n")
        except UnicodeDecodeError:
            wbuf = open(self.srcfile, "r", encoding='Latin-1').read()
            self.encoding = "Latin-1"
            self.dprint("loaded Latin-1 file")
            self.wb = wbuf.split("\n")
        except:
            self.fatal(
                "loadFile: cannot open source file {}".format(self.srcfile))
        self.wb = [s.rstrip() for s in self.wb]

    # load dictionary
    def loadDict(self):
        mdict = []
        try:
            wbuf = open(self.root+'/'+self.wfile,
                        "rU", encoding='UTF-8').read()
            mdict = wbuf.split("\n")
            self.dprint("loaded dictionary ({} words)".format(len(mdict)))
        except Exception as e:
            print(e)
            self.fatal("loadFile: cannot open dictionary")
        mdict = [s.rstrip() for s in mdict]
        self.ddict = set(mdict)

    # load good-words from specified source file
    def loadGood(self):
        gb = []
        gwloaded = False
        if self.goodfile == "":  # no filename specified
            return

        try:
            wbuf = open(self.goodfile, "r", encoding='ASCII').read()
            if len(wbuf) == 0:
                return  # we read it but it waw an empty file
            else:
                gwloaded = True
        except:
            pass  # it wasn't ASCII

        if not gwloaded:
            try:
                wbuf = open(self.goodfile, "r", encoding='UTF-8').read()
                if len(wbuf) == 0:
                    return
                # we opened the goodwords file successfully as UTF-8. We need the
                # file we are checking to be in UTF-8 also.
                if self.encoding != "UTF-8":
                    self.fatal(
                        "encoding conflict: good-words (UTF-8) and text (Latin-1)")
            except UnicodeDecodeError:
                # okay, the good words file isn't UTF-8. See if it's Latin-1
                wbuf = open(self.goodfile, "r", encoding='Latin-1').read()
                if len(wbuf) == 0:
                    return
                # good words file is Latin-1. The text file needs to be the
                # same.
                if self.encoding != "Latin-1":
                    self.fatal(
                        "encoding conflict: good-words (Latin-1) and text (UTF-8)")
                self.dprint("loaded Latin-1 file")
            except:
                self.fatal(
                    "loadFile: cannot open goodwords file {}".format(self.goodfile))

        gb = wbuf.split("\n")
        gb = [s.rstrip() for s in gb]
        self.ddict = self.ddict.union(set(gb))

    # this splits the words and populates the wtext map
    # the map is the word and the line number(s) where it appears
    def splitWords(self):
        for n, s in enumerate(self.wb):
            s = re.sub(r"--+", ' ', s)  # alternate split separator (Latin-1)
            s = re.sub(r"—", ' ', s)  # alternate split separator (UTF-8)
            s = re.sub(r"_", ' ', s)  # italic marker
            s = re.sub(r"=", ' ', s)  # bold marker
            s = re.sub(r"\[", ' ', s)  # brackets are word delimiters
            s = re.sub(r"]", ' ', s)  # bracket
            words = s.split(' ')
            for i, s in enumerate(words):
                words[i] = re.sub(r"[,.\"“”:;?)(!]", "", words[i])
                words[i] = re.sub(r"--", "", words[i])  # Latin-1
                words[i] = re.sub(r"—", "", words[i])  # UTF-8
                words[i] = re.sub(r"^['‘]", "", words[i])  # opening quote
                words[i] = re.sub(r"['’]$", "", words[i])  # closing quote
                words[i] = re.sub(r"’", "'", words[i])  # internal apostrophe
            for word in words:
                if word not in self.wtext:
                    self.wtext[word] = str(n)
                else:
                    if len(self.wtext[word].split(',')) < 10:
                        self.wtext[word] = self.wtext[word]+","+str(n)
                    if len(self.wtext[word].split(',')) == 10:
                        self.wtext[word] = self.wtext[word]+",..."
        self.wtext2 = self.wtext.copy()  # copy original words

    # straighten quote marks
    def sQuotes(self):
        for i, _ in enumerate(self.wb):
            self.wb[i] = re.sub("’", "'", self.wb[i])

    def okByFreq(self):
        self.dprint("candidates: {} words".format(len(self.wtext)))
        t = []
        u = []
        for word in self.wtext:  # get all the words in the text
            t.append(word)
        for word in t:  # if more than four times, accept it
            if len(self.wtext[word].split(',')) >= 4:
                u.append(word)
                self.wtext.pop(word, None)
        # self.pp.pprint(u)
        self.dprint("candidates: {} words; ok by freq: {} words".format(
            len(self.wtext), len(u)))

    def okByDict(self):
        u = []
        for word in self.wtext:
            if word in self.ddict or word.title() in self.ddict:
                u.append(word)
        for word in u:
            self.wtext.pop(word, None)
        # self.pp.pprint(u)
        self.dprint("candidates: {} words; ok by dictionary: {} words".format(
            len(self.wtext), len(u)))

    # attempt transforms on the word and then check in dictionary
    def okByTransform(self):
        u = []
        for word in self.wtext:
            # PUBLISHER -> publisher
            if word.lower() in self.ddict:  # uncapitalize
                u.append(word)
            # lemon -> lemons
            if re.search("s$", word) and (word+"%") in self.ddict:  # plural
                u.append(word)
        for word in u:
            self.wtext.pop(word, None)
        # self.pp.pprint(u)
        self.dprint("candidates: {} words; ok by transform: {} words".format(
            len(self.wtext), len(u)))

    def okByDehyphenate(self):
        u = []
        for word in self.wtext:
            t = word.split("-")  # try to split
            if len(t) > 1:  # it was hyphenated. assume it is okay
                wordOk = True
                for s in t:  # all parts must be words on their own
                    if s not in self.ddict and s.lower() not in self.ddict:
                        wordOk = False
                if wordOk:
                    u.append(word)
        for word in u:
            self.wtext.pop(word, None)
        # self.pp.pprint(u)
        self.dprint("candidates: {} words; ok by dehyphenate: {} words".format(
            len(self.wtext), len(u)))

    def okByDepossessive(self):
        u = []
        for word in self.wtext:
            if re.search("['’]s$", word):
                s = re.sub("['’]s", "", word)
                if s in self.ddict or s.lower() in self.ddict:
                    u.append(word)
        for word in u:
            self.wtext.pop(word, None)
        # self.pp.pprint(u)
        self.dprint("candidates: {} words; ok by depossessive: {} words".format(
            len(self.wtext), len(u)))

    def okByNumeral(self):
        u = []
        for word in self.wtext:
            if re.match(r"^\d+$", word):  # all digits
                u.append(word)
            if re.match(r"^\d+%$", word):  # percentages
                u.append(word)
            if re.match(r"^[I|V|X|L]+$", word):  # Roman numerals
                u.append(word)
        for word in u:
            self.wtext.pop(word, None)
        # self.pp.pprint(u)
        self.dprint("candidates: {} words; ok by numeral: {} words".format(
            len(self.wtext), len(u)))
        # self.pp.pprint(self.wtext)

    def makeReport(self):
        t = []
        # see if we have a qualified name or not
        base = os.path.basename(self.outfile)
        # if they're equal, user gave us an unqualified name (just a file name, no path to it)
        if base == self.outfile:
            # construct path into source directory
            fn = os.path.join(os.path.dirname(
                os.path.realpath(self.srcfile)), self.outfile)
        else:
            fn = self.outfile
        f1 = open(fn, "w", encoding=self.encoding)
        f1.write('\ufeff')  # BOM mark

        # if a word remains in wtext, it has not been approved
        for key in self.wtext:
            t.append(key)
        t.sort()
        f1.write("Suspect words:\n")
        for w in t:
            f1.write("{:s}\n".format(w))  # write the word
            u = self.wtext[w].split(',')
            for line_num in u:
                s = self.wb[int(line_num)].strip()
                f1.write("  {}: {:s}\n".format(line_num, s))
        f1.write("-"*80+"\n")
        f1.write("generated by ppspell: {}\n".format(self.VERSION))
        f1.write("run completed: {}\n".format(self.NOW))

        # s = ""
        # for line in sys.argv:
        #   s += line+" "
        # f1.write("command: {}\n".format(s.strip()))

        f1.close()

    # util: save specified list to specified dstfile
    def saveFile(self, a, fn):
        f1 = open(fn, "w", encoding=self.encoding)
        f1.write("DING")
        for t in a:
            f1.write("{:s}\n".format(t))
        f1.close()

    def run(self):
        self.loadFile() # file to check
        self.loadDict() # dictionary (word list) to use
        self.loadGood() # user-supplied good word list
        self.splitWords()
        self.sQuotes()
        self.okByFreq()
        self.okByDict()
        self.okByTransform()
        self.okByDehyphenate()
        self.okByDepossessive()
        self.okByNumeral()
        self.makeReport()

    def __str__(self):
        return "ppspell"


# process command line
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--infile', help='input file', required=True)
    parser.add_argument('-o', '--outfile', help='output file', required=True)
    parser.add_argument('-g', '--goodfile', help='good word list', default="")
    parser.add_argument('-w', '--wfile', help='dictionary wordlist', default="master.en")
    parser.add_argument(
        '-d', '--debug', help='debug (developer only)', action='store_true')
    args = vars(parser.parse_args())
    return args

def main():
    args = parse_args()
    ppspell = Ppspell(args)
    ppspell.run()

if __name__ == "__main__":
    sys.exit(main())