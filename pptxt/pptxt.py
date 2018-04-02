#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
  pptxt.py
  MIT license (c) 2018 Asylum Computer Services LLC
"""

import sys
import re
import os
from time import gmtime, strftime
import argparse
import collections

class Pptxt(object):

    def __init__(self, args):
        self.srcfile = args['infile']
        self.outfile = args['outfile']
        self.verbose = args['verbose']
        self.t = []  # report
        self.wb = []  # working (wrapped) text
        self.wb2 = []  # unwrapped text
        self.encoding = ""
        self.VERSION = "2018.03.30"
        self.NOW = strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " GMT"

    # display (fatal) error and exit
    def fatal(self, message):
        sys.stderr.write("fatal: " + message + "\r\n")
        exit(1)

    # appends to report
    def report(self, s):
        self.t.append(s)

    # load file
    def loadFile(self):
        empty = re.compile("^$")
        try:
            wbuf = open(self.srcfile, "rU", encoding="UTF-8").read()
            self.encoding = "UTF-8"
            self.wb = wbuf.split("\n")
            self.wb.append("")
            while empty.match(self.wb[-1]):
                self.wb.pop()
            # remove BOM on first line if present
            t = ":".join("{0:x}".format(ord(c)) for c in self.wb[0])
            if t[0:4] == 'feff':
                self.wb[0] = self.wb[0][1:]
        except UnicodeDecodeError:
            wbuf = open(self.srcfile, "r", encoding='Latin-1').read()
            self.encoding = "Latin-1"
            self.wb = wbuf.split("\n")
        except:
            self.fatal(
                "loadFile: cannot open source file {}".format(self.srcfile))
        self.wb = [s.rstrip() for s in self.wb]

    # puts entire book into wb2 with paragraphs unwrapped
    def unwrap(self):
        empty = re.compile("^$")
        # unwrap paragraphs
        s = ""
        self.wb.append("")  # force empty line at EOF
        for line in self.wb:
            if not empty.match(s) and not empty.match(line):
                # join line to current paragraph
                s += " " + line
                continue
            if not empty.match(s) and empty.match(line):
                # paragraph ends
                while "  " in s:
                    s = re.sub("  ", " ", s)
                self.wb2.append(s)
                s = ""
            if empty.match(s) and not empty.match(line):
                # paragraph starts
                s = line
                continue

    def asteriskCheck(self):
        self.report("asterisk check")
        ast_count = 0
        for i, line in enumerate(self.wb):
            if re.search(r"\*\s+\*\s+\*\s+\*\s+\*", line):
                continue
            if re.search(r"\*", line):
                self.report("  {}: {}".format(i+1, line))
                ast_count += 1
        if ast_count == 0:
            self.report("  no unexpected asterisks found in text.")
        self.report("-" * 80)

    def adjacentSpaces(self):
        self.report("adjacent spaces check")
        ast_count = 0
        for i, line in enumerate(self.wb):
            if re.search(r"\S  \S", line):
                self.report("  {}: {}".format(i+1, line))
                ast_count += 1
        if ast_count == 0:
            self.report("  no adjacent spaces found in text.")
        self.report("-" * 80)

    def trailingSpaces(self):
        self.report("trailing spaces check")
        ast_count = 0
        for i, line in enumerate(self.wb):
            if re.search(" $", line):
                self.report("  {}: {}".format(i+1, line))
                ast_count += 1
        if ast_count == 0:
            self.report("  no trailing spaces found in text.")
        self.report("-" * 80)

    def letterFrequency(self):
        self.report("letter frequency check")
        d = collections.defaultdict(int)
        for line in self.wb:
            for c in line:
                d[c] += 1
        s = "  1:"
        printme = False
        for key in d.keys():
            if d[key] == 1:
                s += " {}".format(key)
                printme = True
        if printme:
            self.report(s)

        s = "  2:"
        printme = False
        for key in d.keys():
            if d[key] == 2:
                s += " {}".format(key)
                printme = True
        if printme:
            self.report(s)

        s = "  3:"
        printme = False
        for key in d.keys():
            if d[key] == 3:
                s += " {}".format(key)
                printme = True
        if printme:
            self.report(s)

        self.report("-" * 80)

    def unusualCharacters(self):
        self.report("unusual characters")
        ast_count = 0
        for i, line in enumerate(self.wb):
            # ampersands set off by a space are ok
            line = re.sub(r"\s&\s", "", line)
            line = re.sub(r"[a-zA-Z0-9 .,?!:;\"\'_-]", "", line)  # common ASCII
            line = re.sub(r"[”“’‘—]", "", line)  # common UTF-8
            line = re.sub(r"\*", "", line)  # already flagged
            # allow, but check separately
            line = re.sub(r"[()[\]]", "", line)
            # line = line.strip()
            if len(line) > 0:  # anything left?
                self.report("  {}: {} {}".format(i+1, line, self.wb[i]))
                ast_count += 1
        if ast_count == 0:
            self.report("  no unusual characters found in text.")
        self.report("-" * 80)

    def spacingCheck(self):
        empty = re.compile("^$")
        self.report("line spacing check")
        ast_count = 0
        consec_blank_lines = 0
        s = ""
        overflow = False
        for line in self.wb:
            if empty.match(line):
                consec_blank_lines += 1
            else:
                if consec_blank_lines > 0:
                    # 3 or more, start of new text division
                    if consec_blank_lines >= 3:
                        if overflow:
                            s += " ..."
                            overflow = False
                        if s != "":
                            t = s[:]
                            t = re.sub(r"1|2|4|\.", "", t)
                            t = t.strip()
                            if len(t) > 0:
                                self.report("*" + s[1:])
                                ast_count += 1
                            # else:
                                # self.report(s)
                        s = "  {}".format(consec_blank_lines)
                    else:
                        if len(s) <= 75:
                            s += " {}".format(consec_blank_lines)
                        else:
                            overflow = True
                    consec_blank_lines = 0
        if ast_count == 0:
            self.report("  no suspect spacing.")
        self.report("-" * 80)

    def longLinesCheck(self):
        self.report("long lines check")
        ast_count = 0
        for i, line in enumerate(self.wb):
            if len(line) > 72:
                try:
                    where = self.wb[i].rindex(" ", 1, 65)
                    s = self.wb[i][:where]  # display part of line
                except:
                    s = self.wb[i]  # display entire line
                self.report("  {} ({}): {}...".format(len(line), i, s))
                ast_count += 1
        if ast_count == 0:
            self.report("  no long lines found in text.")
        self.report("-" * 80)

    def shortLinesCheck(self):
        self.report("short lines check")
        ast_count = 0
        # find the start postition of text and line length of each line in the file
        lineld = []   # leading space count, per line
        lineln = []   # line length, per line
        for i, line in enumerate(self.wb):
            leadsp = 0
            m = re.match(r"(\s+)", line)
            if m:
                leadsp = len(m.group(1))
            lineld.append(leadsp)
            lineln.append(len(line))
        # report all short lines
        i = 0
        while i < len(lineln)-1:
            if lineld[i] == 0 and lineln[i] > 0 and lineln[i] < 55 and lineln[i+1] > 0:
                self.report("  {} ({}): {}".format(i+1, lineln[i], self.wb[i]))
                self.report("  {}     : {}".format(i+2, self.wb[i+1]))
                ast_count += 1
            i += 1
        if ast_count == 0:
            self.report("  no short lines found in text.")
        self.report("-" * 80)

    def repeatedWordCheck(self):
        self.report("repeated word check")
        ast_count = 0

        pattern = re.compile(r"(?i)\b(\w+)\s+\1\b")
        for line in self.wb2:
            startpos = 0
            m = pattern.search(line, startpos)
            while m:
                if m.start() >= 15:
                    spos = m.start()-15
                    mtc = 15
                    while mtc > 0 and line[spos] != " ":
                        mtc -= 1
                        spos += 1
                else:
                    spos = 0
                if m.end() <= len(line) - 15:
                    epos = m.end()+14
                    mtc = 15
                    while mtc > 0 and line[epos] != " ":
                        mtc -= 1
                        epos -= 1
                else:
                    epos = len(line)
                ast_count += 1
                self.report("  repeated word: \"{}\":".format(m.group(1)))
                self.report("    {}".format(line[spos:epos].strip()))
                startpos = m.end()
                m = pattern.search(line, startpos)
        if ast_count == 0:
            self.report("  no repeated words found in text.")
        self.report("-" * 80)

    def htmlChecks(self):
        self.report("abandoned tag check")
        ast_count = 0
        for i, line in enumerate(self.wb):
            if re.search(r"<\/?.*?>", line):
                self.report("  {}: {}".format(i+1, line))
                ast_count += 1
        if ast_count == 0:
            self.report("  no html tags found in text.")
        self.report("-" * 80)

    def ellipsisCheck(self):
        self.report("ellipsis check")
        ast_count = 0
        for i, line in enumerate(self.wb):
            suspect = False
            if re.search(r"[^.]\.\.\. ", line):  # give... us some pudding
                suspect = True
            if re.search(r"\.\.\.\.[^\s]", line):  # give....us some pudding
                suspect = True
            if re.search(r"[^.]\.\.[^.]", line):  # give .. us some pudding
                suspect = True
            if re.search(r"\.\.\.\.\.+", line):  # give.....us some pudding
                suspect = True
            if suspect:
                self.report("  {}: {}".format(i+1, line))
                ast_count += 1
        if ast_count == 0:
            self.report("  no ellipsis suspects found.")
        self.report("-" * 80)

    def dashCheck(self):
        self.report("dash check")
        ast_count = 0
        for i, line in enumerate(self.wb):
            suspect = False
            if re.search("— ", line):  # em-dash, space
                suspect = True
            if re.search(" —", line):  # space, then em-dash
                suspect = True
            if re.search("—— ", line):  # double em-dash, space
                suspect = True
            if suspect:
                self.report("  {}: {}".format(i+1, line))
                ast_count += 1
        if ast_count == 0:
            self.report("  no dash suspects found.")
        self.report("-" * 80)

    # from https://www.pgdp.net/c/faq/stealth_scannos_eng_common.txt
    def scannoCheck(self):
        SLIMIT = 30  # how many scanno lines for each potential scanno are shown
        self.report("scanno check")

        # sa is a default list of scanno words
        sa = ['lie', 'arid', 'yon', 'bad', 'tip', 'tho', 'arc', 'hut', 'tiling', 'bat', 'Ms',
              'tune', 'coining', 'hi', 'ho', 'tor', 'hack', 'tie', 'tinder', 'ail', 'tier',
              'fee', 'die', 'docs', 'lime', 'ease', 'ray', 'ringers', 'fail', 'bow', 'clay',
              'borne', 'modem', 'cast', 'bar', 'bear', 'cheek', 'carnage', 'boon', 'car',
              'band', 'ball', 'carne', 'tile', 'ho', 'bo', 'tight', 'bit', 'wen', 'haying',
              'rioted', 'cat', 'tie', 'ringer', 'ray', 'loth', 'comer', 'cat', 'tram',
              'bumbled', 'bead', 'beads']

        ast_count = 0
        h = {}
        for item in sa:
            h[item] = 0
        scannolist = []
        for line in self.wb:
            for key in h:
                if re.search(r"\b{}\b".format(key), line):
                    line = re.sub("\b{}\b".format(key), "", line)
                    s = "  {} | {}".format(key, line)
                    h[key] += 1
                    scannolist.append(s)
        scannolist.sort()
        reporting = ""
        count = 0
        for item in scannolist:
            ast_count += 1
            tmp = item.split("|")
            scanno = tmp[0].strip()
            if scanno == reporting:
                if count == 0:
                    self.report("")
                if count <= SLIMIT-1:
                    self.report("{:<8} {}".format(tmp[0], tmp[1]))
                if count == SLIMIT:
                    additional = int(h[scanno]) - SLIMIT
                    self.report("          ... {} additional occurrences of {}".format(
                        additional, scanno))
                count += 1
            else:
                reporting = scanno
                count = 0
        if ast_count == 0:
            self.report("  no suspected scannos detected")
        self.report("-" * 80)

    def curlyQuoteCheck(self):
        self.report("curly quotes check")
        ast_count = 0

        # regex for punctuation
        rp1 = re.compile(r'[\.,;!?]+[‘“]')
        rp2 = re.compile(r'[A-Za-z]+[‘“]')

        i = 0
        while i < len(self.wb):

            if (re.search(r" [“”] ", self.wb[i]) or
                    re.search(r"^[“”] ", self.wb[i]) or
                    re.search(r" [“”]$", self.wb[i])
               ):
                self.report("  {:>20} | {}".format("floating quote", self.wb[i]))
                self.wb[i] = "..."  # report line only once
                ast_count += 1

            if (rp1.search(self.wb[i]) or
                    rp2.search(self.wb[i]) or
                    re.search(r"“ ", self.wb[i]) or
                    re.search(r" ”", self.wb[i])
               ):
                self.report("  {:>20} | {}".format("quote direction", self.wb[i]))
                self.wb[i] = "..."
                ast_count += 1

            if i > 0 and self.wb[i-1] == "" and re.search(r"^[^“]+”", self.wb[i]):
                self.report("  {:>20} | {}".format(
                    "missing open quote", self.wb[i]))
                self.wb[i] = "..."
                ast_count += 1

            i += 1

        if ast_count == 0:
            self.report("  no curly quote errors detected")
        self.report("-" * 80)

    def specialSituationsCheck(self):
        self.report("special situations check")
        ast_count = 0
        for line in self.wb:

            if "—-" in line:
                self.report("  {:>20} | {}".format("mixed hyphen/dash", line))
                ast_count += 1

            if " " in line:
                self.report("  {:>20} | {}".format("non-breaking space", line))
                ast_count += 1

            if re.search(r"\t", line):
                self.report("  {:>20} | {}".format("tab character", line))
                ast_count += 1

            if re.search(r",\d\d\d\d", line):
                self.report("  {:>20} | {}".format("date format", line))
                ast_count += 1

            if re.search(r"I[\"”]", line):
                self.report("  {:>20} | {}".format("I/! check", line))
                ast_count += 1

            if re.search(r"\s['’](m|ve|ll|t)\b", line):
                self.report("  {:>20} | {}".format("disjointed", line))
                ast_count += 1

            if re.search(r"Blank Page", line):
                self.report("  {:>20} | {}".format("blank page", line))
                ast_count += 1

            if re.search(r"Mr,|Mrs,|Dr,", line):
                self.report("  {:>20} | {}".format("abbreviation", line))
                ast_count += 1

            if re.search(r"\s[\?!,]", line):
                self.report("  {:>20} | {}".format("spaced punctuation", line))
                ast_count += 1

            if (re.search(r"^[\"] ", line)
                    or re.search(r" [\"]$", line)
                    or re.search(r" [\"] ", line)
               ):
                self.report("  {:>20} | {}".format("floating quote", line))
                ast_count += 1

            if (re.search(r"[a-zA-Z_],[a-zA-Z_]", line)
                    or re.search(r"[a-zA-Z_],[a-zA-Z_]", line)
                    or re.search(r"\s,\D", line)
                    or re.search(r"\s,\s", line)
                    or re.search(r"^,", line)
                    or re.search(r"\s,$", line)
               ):
                self.report("  {:>20} | {}".format("comma spacing", line))
                ast_count += 1

            # new Nov, 2017 (version 1.28)
            if re.search(r"\.\s?[a-z]", line):
                self.report("  {:>20} | {}".format("mid-sentence stop", line))
                ast_count += 1

        if ast_count == 0:
            self.report("  no special situation errors detected")
        self.report("-" * 80)

    def ppvChecks(self):
        self.report("PPV checks")
        ast_count = 0

        mrpc = mrc = mrpcs = mrcs = 0
        for line in self.wb:
            if "Mr. " in line:
                mrpc += 1
            if "Mr " in line:
                mrc += 1
            if "Mrs. " in line:
                mrpcs += 1
            if "Mrs " in line:
                mrcs += 1
        if mrpc > 0 and mrc > 0:
            self.report("  both Mr. and Mr found in text")
            ast_count += 1
        if mrpcs > 0 and mrcs > 0:
            self.report("  both Mrs. and Mrs found in text")
            ast_count += 1

        if ast_count == 0:
            self.report("  no special PPV checks failed")
        self.report("-" * 80)

    # save report with same encoding as source file
    def saveReport(self):
        f1 = open(self.outfile, "w", encoding=self.encoding)
        if self.encoding == "UTF-8":
            f1.write('\ufeff')  # BOM if UTF-8
        f1.write("PP Workbench report generated by pptxt (version {})\r\n".format(self.VERSION))
        f1.write("source file: {}\r\n".format(os.path.basename(self.srcfile)))
        f1.write("-"*80+"\r\n")       
        for w in self.t:
            f1.write("{:s}\r\n".format(w))
        f1.write("run completed: {}\r\n".format(self.NOW))
        f1.close()

    def run(self):
        self.loadFile()
        self.unwrap()
        self.asteriskCheck()
        self.adjacentSpaces()
        self.trailingSpaces()
        self.letterFrequency()
        self.unusualCharacters()
        self.spacingCheck()
        self.longLinesCheck()
        self.shortLinesCheck()
        self.repeatedWordCheck()
        self.htmlChecks()
        self.ellipsisCheck()
        self.dashCheck()
        self.scannoCheck()
        self.curlyQuoteCheck()
        self.specialSituationsCheck()
        self.ppvChecks()
        self.saveReport()

    def __str__(self):
        return "pptxt"

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--infile', help='input file', required=True)
    parser.add_argument('-o', '--outfile', help='output file', required=True)
    parser.add_argument('-v', '--verbose', help='verbose', action='store_true')
    args = vars(parser.parse_args())
    return args

def main():
    args = parse_args()
    pptxt = Pptxt(args)
    pptxt.run()

if __name__ == "__main__":
    sys.exit(main())
