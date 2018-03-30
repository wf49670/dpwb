#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ppppv.py for Post-Processing Workbench
license: MIT
version: 2018.03.30
"""

import re
import sys
import os
import argparse
from os import listdir
from os.path import isfile, join
from time import gmtime, strftime

class Ppppv(object):

    def __init__(self, args):
        self.t = []  # report
        self.wb = []  # working (wrapped) text
        self.wb2 = []  # unwrapped text
        self.srcfile = args['infile']
        self.outfile = args['outfile']
        self.root = os.path.dirname(os.path.realpath(__file__))
        self.sdir = "" # to find the images
        self.encoding = ""
        self.NOW = strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " GMT"
        self.VERSION = "2018.03.30"

    # display (fatal) error and exit
    def fatal(self, message):
        sys.stderr.write("fatal: " + message + "\r\n")
        exit(1)

    # appends to report
    def ap(self, s):
        self.t.append(s)

    # load file
    def loadFile(self):
        empty = re.compile("^$")
        try:
            wbuf = open(self.srcfile, "r", encoding='UTF-8').read()
            self.encoding = "UTF-8"
            # remove BOM on first line if present
            t = ":".join("{0:x}".format(ord(c)) for c in wbuf[0])
            if t[0:4] == 'feff':
                self.wb[0] = self.wb[0][1:]
        except UnicodeDecodeError:
            wbuf = open(self.srcfile, "r", encoding='Latin-1').read()
            self.encoding = "Latin-1"
        except:
            self.fatal(
                "loadFile: cannot open source file {}".format(self.srcfile))
        self.wb = wbuf.split("\n")
        self.wb = [s.rstrip() for s in self.wb]
        self.wb.append("") # ensure file end
        while empty.match(self.wb[-1]):
            self.wb.pop()
        self.sdir = os.path.split(self.srcfile)[0] # source directory (./images)
        if self.sdir == "":
            self.sdir = "."  # if we are running this in the same folder


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

    # title check
    # find what's in <title> and compare to what's in <h1>
    #
    def headerChecks(self):
        ast_count = 0
        self.ap("title, headers check")
        c_title = 0
        c_h1 = 0
        t1 = t2 = ""
        i = 0
        while i < len(self.wb):
            line = self.wb[i]

            m1 = re.search(r"<title>", line)
            if m1:
                s = ""
                while "</title>" not in self.wb[i]:
                    s += self.wb[i]
                    i += 1
                s += self.wb[i]
                m1 = re.search(r"<title>(.*?)<\/title>", s)
                if m1:
                    t1 = m1.group(1)
                t1 = re.sub("  +", " ", t1.strip())
                c_title += 1

            m1 = re.search(r"<h1", line)
            if m1:
                s = ""
                while "</h1>" not in self.wb[i]:
                    s += self.wb[i]
                    i += 1
                s += self.wb[i]
                m1 = re.search(r"<h1.*?>(.*?)<\/h1>", s)
                if m1:
                    t2 = m1.group(1)
                    t2 = re.sub("  +", " ", t2.strip())
                    c_h1 += 1
            i += 1

        if c_title == 0:
            self.ap("missing <title> directive")
            ast_count += 1
        if c_h1 == 0:
            self.ap("missing <h1> element")
            ast_count += 1
        if c_title > 1:
            self.ap("too many <title> directives")
            ast_count += 1
        if c_h1 > 1:
            self.ap("too many <h1> elements")
            ast_count += 1

        # clean up title
        t3 = t1.strip()

        # clean up h1
        t4 = re.sub(r"<br.*?>", "#", t2)
        t4 = re.sub(r"<.*?>", "", t4)
        t4 = re.sub(r"\s+", " ", t4)
        t4 = re.sub(r"#", " ", t4)
        self.ap("  title/h1 compare:")
        self.ap("    title: {}\r\n    h1:    {}".format(t3, t4))

        if "Gutenberg" not in t3:
            self.ap("\r\n  warning: title should be of the form")
            self.ap(
                "    The Project Gutenberg eBook of Alice's Adventures in Wonderland,"+
                " by Lewis Carroll")
            # avoid trap in WWer's software (addhd.c)
            if "end" not in t3:
                self.ap("  or")
                self.ap(
                    "    Alice's Adventures in Wonderland, by Lewis Carroll—A"+
                    " Project Gutenberg eBook")

        if t3.endswith('.'):
            self.ap("  WARNING: title ends with full stop")

        self.ap("\r\n  h2 listing:")
        for i, line in enumerate(self.wb):
            m = re.search("<h2.*?>(.*?)</h2>", line)
            if m:
                t = m.group(1)
                t = re.sub("<.*?>", "", t)
                t = re.sub(" +", " ", t)
                self.ap("    {}".format(t))
        self.ap("-" * 80)

    # verify self-closing tags are of the form <XX />
    #
    def spaceClose(self):
        ast_count = 0
        self.ap("self-closing tag format (i.e. <br />)")
        for line in self.wb:
            m = re.search(r"\S/>", line)
            if m:  # report only first five
                if ast_count < 5:
                    self.ap("  " + line)
                    ast_count += 1
                else:
                    self.ap("  ...")
        # if no errors, report
        if ast_count == 0:
            self.ap("  no errors")
        self.ap("-" * 80)

    def imagesCheck(self):
        self.ap("images check")
        # find filenames of all the images
        # allow png, jpg only
        mypath = self.sdir + "/images"
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        # find that each is used once in the text
        # may be special cases used more than once (deorations)
        for filename in onlyfiles:
            eflag = " "
            s = " {}".format(filename)
            if filename != filename.lower():
                s = "* " + s + " filename is not all lower case."
                self.ap(s)
                continue
            if " " in filename:
                s = "* " + s + " filename contains spaces."
                self.ap(s)
                continue

            count = 0
            for line in self.wb:
                m = re.search(filename, line)
                if m:
                    count += 1
            s += "; used:{}".format(count)

            # find image dimensions
            (width, height) = ("", "")
            # note: I could do this with a function instead of popen
            info = os.popen(
                "identify {}/images/{}".format(self.sdir, filename)).read()
            if "JPEG" in info:
                m = re.search(r"(\d+)x(\d+)", info)
                if m:
                    (width, height) = (m.group(1), m.group(2))
            if "PNG" in info:
                m = re.search(r"(\d+)x(\d+)", info)
                if m:
                    (width, height) = (m.group(1), m.group(2))
            s += "; dimensions:{}x{}px".format(width, height)
            if filename == "cover.jpg" and (int(width) < 500 or int(height) > 800):

                if int(width) < 500:
                    s = "*  cover.jpg cover dimension error (width {}px < 500px)".format(
                        width)
                if int(height) > 800:
                    s = "*  cover.jpg cover dimension error (height {}px > 800px)".format(
                        height)
                self.ap(s)
                continue

            # if not the cover, then max dimension must be <= 700px
            if filename != "cover.jpg" and (int(width) > int(height) and int(width) > 700):
                s = "*  {} dimension error {}x{}px (width {}px > 700px)".format(
                    filename, width, height, width)
                self.ap(s)
                continue
            if filename != "cover.jpg" and int(width) < int(height) and int(height) > 700:
                s = "*  {} dimension error {}x{}px (height {}px > 700px)".format(
                    filename, width, height, height)
                self.ap(s)
                continue

            info = os.popen(
                "du -sh {}/images/{}".format(self.sdir, filename)).read()
            m = re.search(r"^(.*?)K", info)
            if m:
                size_in_kb = float(m.group(1))
                if size_in_kb > 100:
                    s = "*  {} file size error {}K > 100K".format(
                        filename, m.group(1))
                    self.ap(s)
                    continue
                s += "; file size:{}K".format(m.group(1))

            self.ap("{} {}".format(eflag, s))
        self.ap("-" * 80)

    def limit(self, s, lnt):
        if len(s) > lnt:
            s = s[:lnt] + "..."
        return s

    def illustrationsCheck(self):
        self.ap("Illustration markup checks")

        # if there is a caption, there should be no alt tag content
        # without a caption, alt tags recommendation:
        #   simple decorative illustration: no alt tag description
        #   text in image: use alt tag description
        #   other image content: PPers choice

        self.ap("  if there is a caption, there should be no alt tag content")
        self.ap("  without a caption, alt tags recommendation:")
        self.ap("    simple decorative illustration: no alt tag description")
        self.ap("    text in image: use alt tag description")
        self.ap("    other image content: PPers choice\r\n")

        self.ap("  non-empty alt tags found:")
        count = 0
        for i, line in enumerate(self.wb):
            m1 = re.search("alt=[\"'](.+?)[\"']", line)
            m2 = re.search("alt=[\"'][\"']", line)
            if m1 and not m2:
                self.ap("    {}".format(self.limit(self.wb[i], 60)))
                count += 1
        if count == 0:
            self.ap("    none")

        self.ap("  empty alt tags found:")
        count = 0
        for i, line in enumerate(self.wb):
            m = re.search("alt=[\"'][\"']", line)
            if m:
                self.ap("    {}".format(self.limit(self.wb[i], 60)))
                count += 1
        if count == 0:
            self.ap("    none")

        self.ap("  missing alt tags:")
        count = 0
        for i, line in enumerate(self.wb):
            m = re.search("(png|jpg)", line)
            if m and "alt" not in line and "href" not in line:
                self.ap("    {}".format(self.limit(self.wb[i], 60)))
                count += 1
        if count == 0:
            self.ap("    none")

        # check there is a link to the cover image for epub
        count = 0
        for line in self.wb:
            if "images/cover.jpg" in line and "link" in line:
                count += 1
        s = "fail"
        if count == 1:
            s = "pass"
        self.ap("  link to cover image: {}".format(s))

        self.ap("-" * 80)

    def linksCheck(self):
        ut = []  # unused targets (with no links pointing to them)
        ul = []  # unused links (having no target)
        for i, _ in enumerate(self.wb):
            m = re.search(r"<a href=[\"']#(.*?)[\"']>", self.wb[i])
            if m:
                target = m.group(1)
                s = "target {} ".format(target)
                re2 = re.compile(r"id=[\"']{}[\"']".format(target))
                for j, _ in enumerate(self.wb):
                    m = re2.search(self.wb[j])
                    if m:
                        s += "ok"
                if "ok" not in s:
                    ul.append(target)

        for i, _ in enumerate(self.wb):
            m = re.search(r"id=[\"'](.*?)[\"']", self.wb[i])
            if m:
                theid = m.group(1)
                s = "id {} ".format(theid)
                re2 = re.compile(r"[\"']#{}[\"']".format(theid))
                for j, _ in enumerate(self.wb):
                    m = re2.search(self.wb[j])
                    if m:
                        s += "used"
                if "used" not in s:
                    ut.append(theid)  # unused targets
        self.ap("Link and target checks")
        nomore = False
        if len(ul) == 0 and len(ut) == 0:
            self.ap("  no errors")
        if len(ul) > 0:
            s = "unused links: "
            for k in ul:
                if not nomore:
                    s += k + " "
                if not nomore and len(s) > 60:
                    s += "..."
                    nomore = True
            self.ap("    {}".format(s))
        if len(ut) > 0:
            s = "unused targets: "
            for k in ut:
                if not nomore:
                    s += k + " "
                if not nomore and len(s) > 60:
                    s += "..."
                    nomore = True
            self.ap("    {}".format(s))
        self.ap("-" * 80)

    def miscChecks(self):
        self.ap("Miscellaneous checks")

        count = 0
        for line in self.wb:
            m = re.search("<table", line)
            if m:
                count += 1
        self.ap("  number of tables: {}".format(count))

        count = 0
        eflag = ""
        for line in self.wb:
            m = re.search("<.*?iv.*?class.*?chapte.*?>", line)
            if m:
                count += 1
        if count == 0:
            eflag = "ERROR: "
        self.ap("  {}number of chapter divs (should be > 0): {}".format(eflag, count))

        count = 0
        for line in self.wb:
            m = re.search("<.*?iv.*?class.*?sectio.*?>", line)
            if m:
                count += 1
        self.ap("  number of section divs (optional): {}".format(count))

        self.ap("  pixels used for sizing (images and borders only):")
        count = 0
        for line in self.wb:
            m = re.search(r"\d ?px", line)
            if m:
                self.ap("    {}".format(line))

        count = 0
        eflag = ""
        for line in self.wb:
            m = re.search("<pre", line)
            if m:
                count += 1
        if count != 0:
            eflag = "ERROR: "
        self.ap("  {}number of <pre> tags (should be 0): {}".format(eflag, count))

        count = 0
        adh = []
        eflag = ""
        for line in self.wb:
                # ignore HTML comments (typically from ppgen)
            if "<!--" not in line and "-->" not in line and "--" in line:
                count += 1
                adh.append(line)
        if count != 0:
            eflag = "WARNING: "
        if count > 0:
            self.ap(
                "  {}lines with \"--\" instead of \"—\" (should be 0): {}".format(eflag, count))
            for line in adh:
                self.ap("  {}".format(line))

        cline = ""
        for line in self.wb:
            if "charset" in line:
                cline = line
        if cline == "":
            self.ap("  ERROR: no charset found")
        else:
            self.ap("  charset should be UTF-8:\r\n      {}".format(cline.strip()))

        cline = ""
        for line in self.wb:
            if "DTD" in line:
                cline = line
        if cline == "":
            self.ap("  ERROR: ")
        else:
            self.ap("  HTML version should be XHTML 1.0 Strict or 1.1:\r\n      {}".format(
                cline.strip()))

    # save report with same encoding as source file
    def saveReport(self):
        # see if we have a qualified name or not
        base = os.path.basename(self.outfile)
        # if they're equal, user gave us an unqualified name (just a file name,
        # no path to it)
        if base == self.outfile:
            # construct path into source directory
            fn = os.path.join(os.path.dirname(
                os.path.realpath(self.srcfile)), self.outfile)
        else:
            fn = self.outfile
        f1 = open(fn, "w", encoding="{}".format(self.encoding))
        if self.encoding == "UTF-8":
            f1.write('\ufeff')  # BOM if UTF-8
        f1.write("ppppv report\r\n")
        f1.write("-"*80+"\r\n")
        for w in self.t:
            f1.write("{:s}\r\n".format(w))
        f1.write("-"*80+"\r\n")
        f1.write("generated by ppppv version: {}\r\n".format(self.VERSION))
        f1.write("run completed: {}\r\n".format(self.NOW))
        f1.close()

    def run(self):
        self.loadFile()
        self.unwrap()
        self.headerChecks()
        self.spaceClose()
        self.imagesCheck()
        self.illustrationsCheck()
        self.linksCheck()
        self.miscChecks()
        self.saveReport()

    def __str__(self):
        return "ppppv"

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--infile', help='input file', required=True)
    parser.add_argument('-o', '--outfile', help='output file', required=True)
    parser.add_argument('-v', '--verbose', help='verbose', action='store_true')
    args = vars(parser.parse_args())
    return args

def main():
    args = parse_args()
    ppppv = Ppppv(args)
    ppppv.run()


if __name__ == "__main__":
    sys.exit(main())
