#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
pplev.py for DP Post-processor's Workbench
license: MIT
version: 2018.03.21
"""

import re
import os
import sys
import pprint
import argparse
from time import gmtime, strftime
from Levenshtein import distance

class Pplev(object):

    def __init__(self, args):
        self.srcfile = args['infile']
        self.outfile = args['outfile']
        self.verbose = args['verbose']
        self.wb = []
        self.wmap = {}  # word map
        self.ddict = {}  # dictionary words
        self.report = []  # report to save in outfile
        self.pnames = {}  # proper names dictionary
        self.encoding = ""
        self.root = os.path.dirname(os.path.realpath(__file__))
        self.pp = pprint.PrettyPrinter(indent=4)
        self.bwlist = []  # words that will be checked
        self.NOW = strftime("%Y-%m-%d %H:%M:%S", gmtime())+" GMT"
        self.VERSION = "2018.03.21"

    # display (fatal) error and exit
    def fatal(self, message):
        sys.stderr.write("fatal: "+message+"\n")
        exit(1)

    # load wb from specified source file
    # accept either UTF-8 or Latin-1 and remember which for output
    def loadFile(self):
        try:
            wbuf = open(self.srcfile, "r", encoding='UTF-8').read()
            self.encoding = "UTF-8"
            self.wb = wbuf.split("\n")
        except UnicodeDecodeError:
            wbuf = open(self.srcfile, "r", encoding='Latin-1').read()
            self.encoding = "Latin-1"
            self.wb = wbuf.split("\n")
        except:
            self.fatal(
                "loadFile: cannot open source file {}".format(self.srcfile))
        self.wb = [s.rstrip() for s in self.wb]

    # load dictionary
    def loadDict(self):
        tmpdict = []
        try:
            wbuf = open(self.root+"/2of12inf.txt",
                        "rU", encoding='UTF-8').read()
            tmpdict = wbuf.split("\n")
        except:
            self.fatal("loadFile: cannot open dictionary")
        tmpdict = [s.rstrip() for s in tmpdict]
        self.ddict = set(tmpdict)

    # this splits the words on each line and populates the wtext map
    # the map is the word and a list; the list is
    #  (bool) T/F if it is a dictionary word
    #  (int) count of how many times it occurs
    #  (string) comma seperated list of the line number(s) where it appears
    def splitWords(self):
        totalwords = 0
        # for each line
        for n, s in enumerate(self.wb):
            # isolate the words using spaces as separator
            s = re.sub(r"--+", ' ', s)  # alternate split separator (Latin-1)
            s = re.sub(r"—+", ' ', s)  # alternate split separator (UTF-8)
            s = re.sub(r"_", ' ', s)  # italic marker
            s = re.sub(r"=", ' ', s)  # bold marker
            s = re.sub(r"\[", ' ', s)  # brackets are word delimiters
            s = re.sub(r"\]", ' ', s)  # bracket
            s = re.sub(r"[,\.\"“”:;\?\)\(!]", "", s)  # drop some punctuation

            # get the words into a short list
            words = s.split(' ')
            totalwords += len(words)
            # go through the list of words and populate the map
            for i, _ in enumerate(words):
                # remove opening quote
                words[i] = re.sub(r"^['‘’]+", "", words[i])
                # remove closing quote
                words[i] = re.sub(r"['’]+$", "", words[i])
                # dictionary uses straight quotes only
                words[i] = re.sub(r"’", "'", words[i])

                # if a word is capitalized, test to see if it's a proper name
                # simple test: if  in lower case it's a dictionary word then
                # don't classify it as a proper name. misses some i.e. "Frank"

                wlower = True
                if words[i].capitalize() == words[i]:
                    # starts with a capital leter
                    if (words[i].lower() not in self.ddict and
                            "'" not in words[i] and len(words[i]) >= 4):
                        wlower = False
                        if words[i] in self.pnames:
                            self.pnames[words[i]] = self.pnames[words[i]] + 1
                        else:
                            self.pnames[words[i]] = 1

                if wlower:
                    words[i] = words[i].lower()

                # create or modify an entry in the map
                # fewer than three letters are ignored completely
                if len(words[i]) > 3:
                    if words[i] not in self.wmap:
                        self.wmap[words[i]] = [
                            False, 0, "{},".format(n)]  # first entry
                    else:
                        self.wmap[words[i]] = [
                            False, 0, self.wmap[words[i]][2] + "{},".format(n)]  # additional entry

        if self.verbose:
            print("total words {}".format(totalwords))

        # map is built with all "False" and 0 for count.
        # once through to fix that an clean up trailing comma
        for key in self.wmap:
                # look up word
            if key in self.ddict:
                self.wmap[key][0] = "True"
            else:
                self.wmap[key][0] = "False"
            # count occurences
            self.wmap[key][1] = self.wmap[key][2].count(',')
            # strip trailing comma
            self.wmap[key][2] = self.wmap[key][2][:-1]

        # create a list of words not in dictionary
        for key in self.wmap:
            if self.wmap[key][0] == "False":
                self.bwlist.append(key)
        # print(self.bwlist, len(self.bwlist), len(self.wmap))
        # now reduce the number of words in bwlist
        for word in self.bwlist:
            # common contractions
            if word.endswith("n't") and word[:-3] in self.ddict:
                self.bwlist.remove(word)
            if word.endswith("'s") and word[:-2] in self.ddict:
                self.bwlist.remove(word)
            if word.endswith("'ve") and word[:-3] in self.ddict:
                self.bwlist.remove(word)
            if word.endswith("'re") and word[:-3] in self.ddict:
                self.bwlist.remove(word)
            # both halves of a hyphenated word are words
            m = re.search(r'(.*?)-(.*?)', word)
            if m and m.group(1) in self.ddict and m.group(2) in self.ddict:
                self.bwlist.remove(word)

    def crunch(self):
        if self.verbose:
            print("words to check: {}".format(len(self.bwlist)))
        for firstword in self.bwlist:
            if len(firstword) <= 5:
                continue
            for secondword in self.wmap:
                if distance(firstword, secondword) == 1:
                    if firstword in self.bwlist:
                        self.bwlist.remove(firstword)
                    if secondword in self.bwlist:
                        self.bwlist.remove(secondword)
                    # limit report
                    fwl = firstword.lower()
                    swl = secondword.lower()
                    # do not report Shoutin shoutin
                    if fwl == swl:
                        continue
                    # do not report equinoctials equinoctial
                    if fwl + 's' == swl or fwl == swl + 's':
                        continue
                    # do not report swimmin swimming
                    if fwl.endswith('g') and fwl[:-1] == swl:
                        continue
                    if swl.endswith('g') and swl[:-1] == fwl:
                        continue
                    # finally make an entry into the report
                    self.report.append("{} ({}) <=> {} ({})"\
                        .format(firstword, self.wmap[firstword][1], \
                        secondword, self.wmap[secondword][1]))
                    line1 = int(self.wmap[firstword][2].split(',')[0])
                    line2 = int(self.wmap[secondword][2].split(',')[0])
                    self.report.append("    {:5d} {}".format(line1, self.wb[line1]))
                    self.report.append("    {:5d} {}".format(line2, self.wb[line2]))

    # write the report in the same encoding as the source file
    #
    def saveReport(self):
        f1 = open(self.outfile, "w", encoding=self.encoding)
        f1.write('\ufeff')  # we want a BOM on the text file 2018.03.22
        f1.write("pplev report\n")
        f1.write("-"*80+"\n")
        for r in self.report:
            f1.write("{:s}\n".format(r))
        f1.write("-"*80+"\n")
        f1.write("generated by pplev version: {}\n".format(self.VERSION))
        f1.write("run completed: {}\n".format(self.NOW))
        f1.close()

    def run(self):
        self.loadFile()
        self.loadDict()
        self.splitWords()
        self.crunch()
        self.saveReport()

    def __str__(self):
        return "pplev"

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--infile', help='input file', required=True)
    parser.add_argument('-o', '--outfile', help='output file', default="log-pplev.txt")
    parser.add_argument('-v', '--verbose', help='verbose', action='store_true')
    args = vars(parser.parse_args())
    return args

def main():
    args = parse_args()
    pplev = Pplev(args)
    pplev.run()

if __name__ == "__main__":
    sys.exit(main())
