#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
jeebies.py for DP Post-processor's Workbench
license: MIT
version: 2018.03.28
"""

import sys
import re
from time import gmtime, strftime
import argparse

# jeebies in Python.
# gives similar results to C version.
# Doesn't work with two-word forms. i.e. at start of sentence.
# Doesn't split on sentences.


class Ppjeeb(object):

    # ---------------------------------------------------------------------------
    # create instance
    def __init__(self, args):
        self.srcfile = args['infile']
        self.outfile = args['outfile']
        self.verbose = args['verbose']
        self.wb = []  # from input text file
        self.wbl = []  # lower-case wb
        self.encoding = ""
        self.report = ""  # generated list of suspects
        self.he = []  # from he.jee
        self.hen = []
        self.be = []  # from be.jee
        self.ben = []
        self.count_be = 0 # counts for report
        self.count_he = 0
        self.count_suspects = 0
        self.NOW = strftime("%Y-%m-%d %H:%M:%S", gmtime())+" GMT"
        self.VERSION = "2018.03.28"

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

        # load the he.jee file
        w = open("he.jee", "rU", encoding='UTF-8').read()
        t = w.split("\n")
        for s in t:
            u = s.split()
            if len(u) == 2:
                self.he.append(u[0].strip())
                self.hen.append(u[1].strip())

        # load the be.jee file
        w = open("be.jee", "rU", encoding='UTF-8').read()
        t = w.split("\n")
        for s in t:
            u = s.split()
            if len(u) == 2:
                self.be.append(u[0].strip())
                self.ben.append(u[1].strip())

    # convert wb to a single long string
    def unwrap(self):
        i = 1
        empty = re.compile("^$")
        while i < len(self.wb):
            if (not empty.match(self.wb[i-1])
                    and not empty.match(self.wb[i])):
                self.wb[i-1] = self.wb[i-1] + " " + self.wb[i]
                del self.wb[i]
                i -= 1
            i += 1

    # convert entire wb to lower case
    def lowerline(self):
        for line in self.wb:
            self.wbl.append(line.lower())

    #
    def process(self):

        # p2b = " (be [a-z]+)"  # note leading space
        p3b = "([a-z']+ be [a-z']+)"

        for k, _ in enumerate(self.wbl):

            m3 = re.search(p3b, self.wbl[k])
            while m3:  # have a three-form match
                self.count_be += 1
                b_count = 0
                h_count = 0
                lookb = re.sub(r" ", r"|", m3.group(0))
                lookh = re.sub(r"\|be\|", "|he|", lookb)
                for i, line in enumerate(self.he):
                    if lookh == line:
                        h_count = int(self.hen[i])
                for i, line in enumerate(self.be):
                    if lookb == line:
                        b_count = int(self.ben[i])
                if h_count > 0 and (b_count == 0 or h_count/b_count) > 0.5:
                    m = re.search(m3.group(0), self.wb[k], re.IGNORECASE)
                    if m:
                        theStart = max(m.start()-20, 0)
                        theEnd = min(m.end()+20, len(self.wb[k]))
                        s4 = self.wb[k][theStart:theEnd]
                        while not s4.startswith(" "):
                            s4 = s4[1:]
                        s4 = s4[1:]
                        while not s4.endswith(" "):
                            s4 = s4[:-1]
                        s4 = s4[:-1]
                        if b_count == 0:
                            scary = 2
                        else:
                            scary = h_count/b_count
                        self.report += ("{} ({:.2f})\n   {}\n".format(m3.group(0), scary, s4))
                        self.count_suspects += 1
                self.wbl[k] = re.sub(m3.group(0), " " *
                                     len(m3.group(0)), self.wbl[k], 1)
                self.wb[k] = re.sub(
                    m3.group(0), " " * len(m3.group(0)), self.wb[k], 1, re.IGNORECASE)
                m3 = re.search(p3b, self.wbl[k])

        # p2h = " (he [a-z]+)"  # note leading space
        p3h = "([a-z']+ he [a-z']+)"

        for k, _ in enumerate(self.wbl):

            m3 = re.search(p3h, self.wbl[k])
            while m3:  # have a three-form match
                self.count_he += 1
                b_count = 0
                h_count = 0
                lookh = re.sub(r" ", r"|", m3.group(0))
                lookb = re.sub(r"\|he\|", "|be|", lookh)
                for i, line in enumerate(self.he):
                    if lookh == line:
                        h_count = int(self.hen[i])
                for i, line in enumerate(self.be):
                    if lookb == line:
                        b_count = int(self.ben[i])
                if b_count > 0 and (h_count == 0 or b_count/h_count) > 0.5:
                    m = re.search(m3.group(0), self.wb[k], re.IGNORECASE)
                    if m:
                        theStart = max(m.start()-20, 0)
                        theEnd = min(m.end()+20, len(self.wb[k]))
                        s4 = self.wb[k][theStart:theEnd]
                        if theStart > 0:
                            while not s4.startswith(" "):
                                s4 = s4[1:]
                            s4 = s4[1:]
                        if theEnd < len(self.wb[k]):
                            while not s4.endswith(" "):
                                s4 = s4[:-1]
                            s4 = s4[:-1]
                        if h_count == 0:
                            scary = 2
                        else:
                            scary = b_count/h_count
                        self.report += ("{} ({:.2f})\n   {}\n".format(m3.group(0), scary, s4))
                        self.count_suspects += 1
                self.wbl[k] = re.sub(m3.group(0), " " *
                                     len(m3.group(0)), self.wbl[k], 1)
                self.wb[k] = re.sub(
                    m3.group(0), " " * len(m3.group(0)), self.wb[k], 1, re.IGNORECASE)
                m3 = re.search(p3h, self.wbl[k])

    # ---------------------------------------------------------------------------
    #
    def saveReport(self):
        f1 = open(self.outfile, "w", encoding=self.encoding)
        if self.encoding == "UTF-8":
            f1.write('\ufeff')  # BOM if UTF-8
        f1.write("jeebies report\n")
        f1.write("-"*80+"\n")
        f1.write(self.report)
        f1.write("\nchecked {} \"he\" phrases\n".format(self.count_he))
        f1.write("checked {} \"be\" phrases\n".format(self.count_be))
        f1.write("analysis complete. {} suspects\n".format(self.count_suspects))
        f1.write("-"*80+"\n")
        f1.write("generated by ppjeeb version: {}\n".format(self.VERSION))
        f1.write("run completed: {}\n".format(self.NOW))
        f1.close()

    # ---------------------------------------------------------------------------
    # class entry point
    def run(self):
        self.loadFile()
        self.unwrap()
        self.lowerline()
        self.process()
        self.saveReport()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--infile', help='input file', required=True)
    parser.add_argument('-o', '--outfile', help='output file', required=True)
    parser.add_argument('-v', '--verbose', help='verbose', action='store_true')
    args = vars(parser.parse_args())
    return args


def main():
    args = parse_args()
    ppjeeb = Ppjeeb(args)
    ppjeeb.run()


if __name__ == "__main__":
    sys.exit(main())
