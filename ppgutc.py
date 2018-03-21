#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ppgutc.py for DP Post-processor's Workbench
license: MIT
version: 2018.03.21
"""

import re
import sys
import os
import collections
import argparse
from time import gmtime, strftime


class Ppgutc(object):

    def __init__(self, args):
        self.srcfile = args['infile']
        self.outfile = args['outfile']
        self.debug = args['debug']
        # particular to ppgutc
        self.wb = []
        self.encoding = ""
        self.showall = args['showall']  # show all output
        self.skiptests = args['skiptests'].split(',')
        for i, _ in enumerate(self.skiptests):
            self.skiptests[i] = self.skiptests[i].strip()
        self.report = ""  # the generated report
        self.text = ""  # the entire book in one string
        self.NOW = strftime("%Y-%m-%d %H:%M:%S", gmtime())+" GMT"
        self.VERSION = "2018.03.21"
        # definitions matching those in gutcheck.c
        self.LONGEST_PG_LINE = 75
        self.WAY_TOO_LONG = 80
        self.SHORTEST_PG_LINE = 55
        # where I am running this from
        self.root = os.path.dirname(os.path.realpath(__file__))

        # actionlist lists actions, either evaluations with a RE or
        # more complicated actions requiring named functions.
        # some of the actionlist is borrowed from guiguts regex.rc
        self.actionlist = (

            (1, "r", "2,2", "opening square bracket followed by anything but F, S, I, G or number",
             r'\[[^FSIG\d].*?\]'),
            (2, "r", "2,2", "dates that are missing a space between the month and year",
             r'([0-9]),([0-9]{4})'),
            (3, "r", "2,2", "string \"uess\" not preceded by a g",
             r'([^gG])uess'),
            (4, "r", "2,2",
             "string that contains hl preceded by one of (a,b,i,m,o or u) followed by i or e",
             r'([abimou])hl([ie])'),
            (5, "m", "2,2", "adjacent white-space characters", "check_adjws"),
            # (6, "r", "2,2", "initials without a space between them", r'([A-Z])\.([A-Z])\.'),
            (7, "r", "2,2", "paragraph that ends in a comma", r',(?=\n\n)'),
            (8, "r", "2,2", "string containing at least 5 consonants in a row",
             r'[b-df-hj-np-tv-xz]{5,}'),
            (9, "r", "2,2",
             "full stop (period) with the following word starting with a lower case character",
             r'\.("?\n\s*"?\p{Lower})'),
            (10, "r", "2,2", "period followed by a space and a lower-case letter",
             r'\.(\s\p{IsLower})'),
            (11, "r", "2,2", "string that starts with hl", r'\bhl'),
            (12, "r", "2,2", "string that starts with hr", r'\bhr'),
            (13, "r", "2,2", "string that starts with rn", r'\brn'),
            (14, "r", "2,2", "string ii not at the beginning of a word", r'\Bii'),
            (15, "r", "2,2", "repeated words or word sequences", r'\b(\S\S+)\s\1\b'),
            (16, "r", "2,2",
             "spaced single (curly) quote dangling on the end of a line", r'\s’$'),
            (17, "r", "2,2",
             "spaced single straight quote dangling on the end of a line", r'\s\'$'),
            (18, "r", "2,0", "trailing spaces", r' $'),
            (19, "r", "2,2", "string that contains cb", r'cb'),
            (20, "r", "2,2", "string that ends in cl", r'cl\b'),
            (21, "r", "2,2", "string that contains gbt", r'gbt'),
            (22, "r", "2,2",
             "character strings that end with j (s/b semicolon)", r'(\w+)j\b'),
            (23, "r", "2,2", "string containing mcnt (s/b ment)", r'mcnt'),
            (24, "r", "2,2",
             "string that contains rnb, rnm or rnp", r'rn([bmp])'),
            (25, "r", "2,2", "string that contains tb", r'tb'),
            (26, "r", "2,2", "string that contains tii", r'tii'),
            (27, "r", "2,2", "string that contains tli", r'tli'),
            (28, "r", "2,2", "string that ends with a v (s/b y)", r'(\w+)v\b'),
            (29, "r", "2,2",
             "pairs of guillemots (across several lines)", r'«[^»]+»\n?'),
            (30, "r", "2,2",
             "the abreviation \"&c.\" that doesn\'t have a period after it", r'&c(,| |$)'),
            (31, "r", "2,2",
             "line that starts with selected punctuation", r'^[!;:,.?]'),
            (32, "r", "2,2",
             "line that starts with hyphen and then non-hyphen", r'^-[^-]'),
            (33, "r", "2,2", "tabs", r'\t'),
            (34, "r", "2,2", "soft hyphens", r'\xAD'),
            (35, "r", "2,2", "mixed dashes/hyphens", r'(—-)|(-—)'),
            (36, "r", "2,2", "non-breaking spaces", r' '),
            (37, "r", "2,2",
             "I masquerading as an exclamation point", r'I[”"]'),
            (38, "r", "2,2", "disjointed contractions", r'\s[\'’](m|ve|ll|t)\b'),
            (39, "r", "2,2", "abandoned Blank Page flags", r'Blank Page'),
            (40, "r", "2,2", "title abbreviation punctuation errors", r'Mr,|Mrs,|Dr,'),
            (41, "r", "2,2", "spaced punctuation", r'\s[\?!,]'),
            (42, "r", "2,2", "floating quotes",
             r'(^["\'“‘’"]\s)|(\s["\'“‘’"]\s)|(\s["\'“‘’"]$)'),
            #(43, "r", "2,2", "comma spacing errors", r'(\w,\w)|(\s,\D)|(\s,\s)|(^,)|(\s,$)'),
            (43, "m", "2,2", "comma spacing errors", "check_commas"),
            (44, "r", "2,2", "mid-sentence stop", r'[^\.]\.\s?[a-z]'),
            (45, "r", "2,2", "period space non-capital letter, punct or italic",
             r'[^\.]\. [^A-Z‘’“"„_]'),
            (46, "r", "2,2", "ellipsis check",
             r'([^\.]\.\.\. )|(\.\.\.\.[^\s])|([^\.]\.\.[^\.])|(\.\.\.\.\.+)'),
            (47, "r", "2,2", "floating quotes", r'( [“”] )|(^[“”] )|( [“”]$)'),
            (48, "r", "2,2", "HTML tags in text version", r'<\/?.*?>'),
            (49, "r", "2,2", "dash check", r'(—— )|(— )|( —)|(———)'),
            (50, "r", "2,2", "missing paragraph break", r'(” +“)|(" +")'),
            (51, "r", "2,2", "quote direction",
             r'([\.,;!?]+[‘“])|([A-Za-z]+[‘“])|(“ )|( ”)'),
            (52, "r", "2,2",
             "a string that starts with one of c, s or w, li, then a vowel excluding 'client'",
             r'(?!client)\b([csw])li([aeiou])'),
            (53, "m", "0,0",
             "Check for American and British abbreviation conventions", "check_ambrit"),
            (54, "m", "0,0", "Check for mixed curly/straight quotation marks", "check_qmarks"),
            (55, "m", "0,0", "Short line check", "check_short"),
            (56, "m", "0,0", "Long line check", "check_long"),
            (57, "m", "0,0", "Asterisk check", "check_ast"),
            (58, "m", "0,0", "Letter frequency", "check_letfreq"),
            (59, "m", "0,0", "To-day/Today consistency", "check_today"),
            (60, "r", "2,2", "punctuation after \"the\"",
             r'\b[Tt]he[\.\,\?\'\"\;\:\!\@\#\$\%\^\&\(\)]'),
            (61, "r", "2,2", "standalone numeral zero in text", r'\s0\s'),
            (62, "r", "2,2", "standalone numeral one in text", r'\b1\b'),
            (63, "r", "2,2", "mixed numereral and alphabetic",
             r'([A-Za-z]\d)|(\d[A-Za-z])'),
            (64, "r", "2,2", "ampersand in text", r'&'),
            (65, "r", "2,2", "unconverted \"--\" to \"—\"", r'(\w--\w)|(\w--)|(--\w)'),
            (66, "r", "2,2", "white space at end of line", r' $'),
            (67, "r", "2,2", "dot + comma", r'\.,'),
            (68, "r", "2,2", "double dash broken at line end", r'—\n—'),
            (69, "r", "2,2", "single character line", r'^.$'),
            (70, "m", "0,0", "Check common he/be errors", "check_hebe"),
            (71, "m", "0,0", "Check common had/bad errors", "check_hadbad"),
            (72, "m", "0,0", "Check common hut/but errors", "check_hutbut"),
            (73, "r", "2,2", "incorrectly split paragraphs", r'\n\n[a-z]'),
            (74, "r", "2,2", "double punctuation",
             r'(,\.)|(\.,)|(,,)|([^\.]\.\.[^\.])'),
            (76, "m", "2,2", "words usually not followed by a comma", "check_wordsnc"),
            (77, "m", "2,2", "words usually not followed by a period", "check_wordsnp"),
            (78, "m", "2,2", "two letter combination not expected at word end",
             "check_words2e"),
            (79, "m", "2,2", "two letter combination not expected at word start",
             "check_words2s"),
            (80, "r", "2,2", "unexpected HTML entity", r'&\w+;'),
            (81, "m", "0,0", "Common scannos check", "check_scannos"),
            (82, "r", "2,2", "special case of 'S instead of 's at end of word",
             r"[a-z]['’]S\b"),
            (83, "r", "2,2", "unexpected standalone letter",
             r" [^AIa„à\|0-9=\-+×÷\* ] "),
            (84, "r", "2,2", "mixed case",
             r"(\b[A-Z]\w*?[A-Z][a-z]\w*\b)|(\b[A-Z]\w*?[a-z][A-Z]\w*\b)|(\b\w*?[a-z][A-Z]\w*\b)"),
            (85, "r", "2,2", "broken hyphen",
             r'([A-Za-z]\- [A-Za-z])|([A-Za-z] \-[A-Za-z])'),
            (86, "m", "0,0", "Check mixed turned-comma and apostrophe",
             "check_turnedcomma"),
            (87, "m", "0,0", "Unexpected/ususual paragraph end", "check_paraend"),
            (88, "r", "3,3", "Apostrophe outside italic markup", r"_’")
        )

        # still to code:
        # a comma, space or newline, upper case character not a common name in text

        # from en-common.rc
        self.scannoslist = (
            '111', 'ail', 'arc', 'arid', 'bad', 'ball', 'band', 'bar', 'bat', 'bead',
            'beads', 'bear', 'bit', 'bo', 'boon', 'borne', 'bow', 'bumbled', 'car', 'carnage',
            'carne', 'cast', 'cat', 'CHATTER', 'CHARTER', 'cheek', 'clay', 'coining', 'comer',
            'die', 'docs', 'ease', 'fail', 'fax', 'fee', 'ha', 'hare', 'haying', 'hie', 'ho',
            'hut', 'lie', 'lime', 'loth', 'm', 'mall', 'modem', 'meat', 'Ms', 'OP',
            'ray', 'ringer', 'ringers', 'rioted', 'tho', 'tie', 'tier', 'tight', 'tile',
            'tiling', 'tip', 'tor', 'tram', 'tune', 'wen', 'yon'
        )

        # from gutcheck.typ
        self.gcscannoslist = (
            '11', '44', 'ms', 'ail', 'alien', 'arc', 'arid', 'bar', 'bat', 'bo', 'borne',
            'bow', 'bum', 'bumbled', 'carnage', 'carne', 'cither', 'coining', 'comer',
            'cur', 'docs', 'eve', 'eves', 'gaming', 'gram', 'guru', 'hag', 'hare', 'haying',
            'ho', 'lime', 'loth', 'm', 'modem', 'nave', 'ringer', 'ringers', 'riot', 'rioted',
            'signer', 'snore', 'spam', 'tho', 'tier', 'tile', 'tiling', 'tram', 'tum', 'tune',
            'u', 'vas', 'wag', 'wen', 'yon'
        )

        # commas should not occur after these words
        self.nocomma = ("the", "it's", "their", "an", "mrs", "a", "our", "that's",
                        "its", "whose", "every", "i'll", "your", "my",
                        "mr", "mrs", "mss", "mssrs", "ft", "pm", "st", "dr", "rd",
                        "pp", "cf", "jr", "sr", "vs", "lb", "lbs", "ltd",
                        "i'm", "during", "let", "toward", "among")

        # periods should not occur after these words
        self.noperiod = ("every", "i'm", "during", "that's", "their", "your", "our", "my", "or",
                         "and", "but", "as", "if", "the", "its", "it's", "until", "than", "whether",
                         "i'll", "whose", "who", "because", "when", "let", "till", "very",
                         "an", "among", "those", "into", "whom", "having", "thence")

        # Common abbreviations and other OK words not to query as typos.
        self.okword = ("mr", "mrs", "mss", "mssrs", "ft", "pm", "st", "dr", "hmm", "h'm",
                       "hmmm", "rd", "sh", "br", "pp", "hm", "cf", "jr", "sr", "vs", "lb",
                       "lbs", "ltd", "pompeii", "hawaii", "hawaiian", "hotbed", "heartbeat",
                       "heartbeats", "outbid", "outbids", "frostbite", "frostbitten")

        # Common abbreviations that cause otherwise unexplained periods.
        self.abbrev = ("cent", "cents", "viz", "vol", "vols", "vid", "ed", "al", "etc",
                       "op", "cit", "deg", "min", "chap", "oz", "mme", "mlle", "mssrs")

        # Two-Letter combinations that rarely if ever start words,
        # but are common scannos or otherwise common letter combinations.
        self.nostart = ("hr", "hl", "cb", "sb", "tb",
                        "wb", "tl", "tn", "rn", "lt", "tj")

        # Two-Letter combinations that rarely if ever end words
        # but are common scannos or otherwise common letter combinations
        self.noend = ("cb", "gb", "pb", "sb", "tb", "wh", "fr", "br", "qu",
                      "tw", "gl", "fl", "sw", "gr", "sl", "cl", "iy")

    # display (fatal) error and exit
    def fatal(self, message):
        sys.stderr.write("fatal: " + message + "\n")
        exit(1)

    def check_commas(self, tn, td):
        s = ""
        reported = False
        count = 0
        for i, line in enumerate(self.wb):

            usem = None

            m1 = re.search(r"^,", line)  # no comma starts a line
            m2 = re.search(r"\s,", line)  # no space before a comma
            m3 = re.search(r"\s,\s", line)  # no floating comma
            # always a space after a comma unless a digit
            m4 = re.search(r",\w", line)

            if m1:
                usem = m1

            elif m2:
                usem = m2

            elif m3:
                usem = m3

            elif m4:
                if m4.group(0)[1] in "0123456789":  # 100,000
                    continue
                usem = m4

            if usem:
                if not reported:
                    reported = True
                    s += "specific comma checks\n"
                if not self.showall and count == 5:
                    s += "          ..... more"
                    count += 1
                if self.showall or count < 5:
                    llim = max(0, usem.span()[0] - 19)
                    rlim = min(len(self.wb[i]), usem.span()[1] + 20)
                    t = self.wb[i][llim:rlim]
                    if llim != 0:
                        llim = t.find(" ")
                    if rlim != len(self.wb[i]):
                        rlim = t.rfind(" ")
                    t = t[llim:rlim].strip()
                    s += "{:6d} {:s}\n".format(i, t)
                    count += 1

        if self.showall and not reported:
            self.areport("test {}: {} [no reports]".format(tn, td))
        return s

    # check words not usually followed by punctuation
    # handle periods and commas separately

    def check_wordsnc(self, tn, td):
        s = ""
        reported = False
        count = 0

        # first, the words that should not have a following comma
        for theword in self.nocomma:
            searchfor = r"\b{},".format(theword)
            hits = re.finditer(searchfor, self.text,
                               re.MULTILINE+re.IGNORECASE)
            # each hit is a match to a word+comma to flag
            for hit in hits:
                if not reported:
                    reported = True
                    s += "unexpected comma after word\n"
                if not self.showall and count == 5:
                    s += "          ..... more"
                    count += 1
                if self.showall or count < 5:
                    # s += "  " + self.add_report_s(hit.span(), "3,3", "")
                    s += "  " + self.add_report_s(hit.span(), "3,3")
                    count += 1
        if self.showall and not reported:
            self.areport("test {}: {} [no reports]".format(tn, td))
        return s

    def check_wordsnp(self, tn, td):
        s = ""
        reported = False
        count = 0

        # second, the words that should not have a following period
        for theword in self.noperiod:
            searchfor = r"\b{}\.".format(theword)
            hits = re.finditer(searchfor, self.text,
                               re.MULTILINE+re.IGNORECASE)
            # each hit is a match to a word+comma to flag
            for hit in hits:
                if not reported:
                    reported = True
                    s += "unexpected period after word\n"
                if not self.showall and count == 5:
                    s += "          ..... more"
                    count += 1
                if self.showall or count < 5:
                    # s += "  " + self.add_report_s(hit.span(), "3,3", "")
                    s += "  " + self.add_report_s(hit.span(), "3,3")
                    count += 1
        if self.showall and not reported:
            self.areport("test {}: {} [no reports]".format(tn, td))
        return s

    # Two-Letter combinations that rarely if ever end words,
    # but are common scannos or otherwise common letter combinations
    def check_words2e(self, tn, td):
        s = ""
        reported = False
        count = 0

        for thetwo in self.noend:
            searchfor = r"\b.*?{}\b".format(thetwo)
            hits = re.finditer(searchfor, self.text,
                               re.MULTILINE+re.IGNORECASE)
            for hit in hits:
                if not reported:
                    reported = True
                    s += "unexpected two letter combination ending word\n"
                if not self.showall and count == 5:
                    s += "          ..... more"
                    count += 1
                if self.showall or count < 5:
                    # s += "  " + self.add_report_s(hit.span(), "3,3", "")
                    s += "  " + self.add_report_s(hit.span(), "3,3")
                    count += 1
        if self.showall and not reported:
            self.areport("test {}: {} [no reports]".format(tn, td))
        return s

    # Check paragraph end for reasonable punctuation
    # For now, a "paragraph" is two lines, left justified, with the first being
    # > 50 characters and the second being non-blank.
    # A comma ending a paragraph is already tested and more frequently allowed
    def check_paraend(self, tn, td):  # test number and description
        s = ""
        empty = re.compile("^$")
        reported = False
        count = 0

        # decide is this is American or British punctuation
        cbrit = camer = 0
        for line in self.wb:
            if ".’" in line:
                cbrit += 1
            if ".”" in line:
                camer += 1

        # find start of text
        i = 0
        textstart = 0
        while textstart == 0 and i < len(self.wb)-3:
            if ((len(self.wb[i]) > 50 and not self.wb[i].startswith(' ')) and
                    not (self.wb[i+1].startswith(' ') or empty.match(self.wb[i+1]))):
                textstart = i
            i += 1
        # look for paragraph end
        i = textstart + 1
        while i < len(self.wb) - 3:
            if (len(self.wb[i-1]) > 50                   # long line before me
                    and not self.wb[i-1].startswith(' ') # not a block quote or poetry
                    and not self.wb[i].startswith(' ')   # doesn't start with a blank either
                    and not empty.match(self.wb[i])      # nor is it empty
                    and empty.match(self.wb[i+1])):      # but the one after me is
                # self.wb[i] is the last line of a traditional paragraph
                okend = False
                if (self.wb[i].endswith(".") or
                        self.wb[i].endswith(":") or
                        self.wb[i].endswith('?') or
                        self.wb[i].endswith('!') or
                        self.wb[i].endswith('_') or
                        self.wb[i].endswith('—')):
                    okend = True
                if (self.wb[i].endswith('."') or
                        self.wb[i].endswith('?"') or
                        self.wb[i].endswith("'\"") or
                        self.wb[i].endswith("--") or
                        self.wb[i].endswith('!"')):
                    okend = True
                if camer > cbrit:
                    if (self.wb[i].endswith(".”") or
                            self.wb[i].endswith("?”") or
                            self.wb[i].endswith("!”") or
                            self.wb[i].endswith("--”") or
                            self.wb[i].endswith("—”") or
                            self.wb[i].endswith("_”") or
                            self.wb[i].endswith("’”")):
                        okend = True
                else:
                    if (self.wb[i].endswith(".’") or
                            self.wb[i].endswith("?’") or
                            self.wb[i].endswith("!’") or
                            self.wb[i].endswith("--’") or
                            self.wb[i].endswith("—’") or
                            self.wb[i].endswith("_’") or
                            self.wb[i].endswith("”’")):
                        okend = True
                if not okend:
                    if not reported:
                        reported = True
                        s += "{}\n".format(td)
                    if not self.showall and count == 20:
                        s += "          ..... more"
                        count += 1
                    if self.showall or count < 5:
                        s += "{:6d} {:s}\n".format(i, self.wb[i])
                        count += 1
            i += 1
        if self.showall and not reported:
            self.areport("test {}: {} [no reports]".format(tn, td))
        return s

    # Two-Letter combinations that rarely if ever start words,
    # but are common scannos or otherwise common letter combinations
    def check_words2s(self, tn, td):
        s = ""
        reported = False
        count = 0

        for thetwo in self.nostart:
            searchfor = r"\b{}.*?\b".format(thetwo)
            hits = re.finditer(searchfor, self.text,
                               re.MULTILINE+re.IGNORECASE)
            for hit in hits:
                if not reported:
                    reported = True
                    s += "unexpected two letter combination starting word\n"
                if not self.showall and count == 5:
                    s += "          ..... more"
                    count += 1
                if self.showall or count < 5:
                    # s += "  " + self.add_report_s(hit.span(), "3,3", "")
                    s += "  " + self.add_report_s(hit.span(), "3,3")
                    count += 1
        if self.showall and not reported:
            self.areport("test {}: {} [no reports]".format(tn, td))
        return s

    # simple he/be checks from gutcheck.c
    # user should always run jeebies
    # this flags a few common ones
    def check_hebe(self, tn, td):
        s = ""
        reported = False
        count = 0

        common_hebe = (
            "to he", "is be", "be is", "was be", "be would", "be could")
        for hb in common_hebe:
            for i, line in enumerate(self.wb):
                if re.search(r"\b{}\b".format(hb), line):
                    if not reported:
                        s += "Common he/be suspects (please run jeebies)\n\n"
                        reported = True
                    if not self.showall and count == 5:
                        s += "       ..... more"
                        count += 1
                    if self.showall or count < 5:
                        line = re.sub("({})".format(hb), r"<\1>", line)
                        s += "{:>6} {}\n".format(i, line)
                        count += 1
        if self.showall and not reported:
            self.areport("test {}: {} [no reports]".format(tn, td))
        return s

    # simple had/bad checks from gutcheck.c
    # this flags a few common ones
    def check_hadbad(self, tn, td):
        s = ""
        reported = False
        count = 0

        common_hadbad = (
            "i bad", "you bad", "he bad", "she bad", "they bad", "a had", "the had")

        for hb in common_hadbad:
            for i, line in enumerate(self.wb):
                if re.search(r"\b{}\b".format(hb), line):
                    if not reported:
                        s += "Common had/bad suspects\n\n"
                        reported = True
                    if not self.showall and count == 5:
                        s += "       ..... more"
                        count += 1
                    if self.showall or count < 5:
                        line = re.sub("({})".format(hb), r"<\1>", line)
                        s += "{:>6} {}\n".format(i, line)
                        count += 1
        if self.showall and not reported:
            self.areport("test {}: {} [no reports]".format(tn, td))
        return s

    # simple hut/but checks from gutcheck.c
    # this flags two common ones
    def check_hutbut(self, tn, td):
        s = ""
        reported = False
        count = 0

        common_hutbut = (", hut", "; hut")

        for hb in common_hutbut:
            for i, line in enumerate(self.wb):
                if re.search(r"\b{}\b".format(hb), line):
                    if not reported:
                        s += "Common hut/but suspects\n\n"
                        reported = True
                    if not self.showall and count == 5:
                        s += "       ..... more"
                        count += 1
                    if self.showall or count < 5:
                        line = re.sub("({})".format(hb), r"<\1>", line)
                        s += "{:>6} {}\n".format(i, line)
                        count += 1
        if self.showall and not reported:
            self.areport("test {}: {} [no reports]".format(tn, td))
        return s

    # always -a all reports
    def check_letfreq(self, *_):
        s = ""
        reported = report1 = report2 = report3 = False
        d = collections.defaultdict(int)
        for c in self.text:
            d[c] += 1
        for key in d.keys():
            if d[key] == 1:
                if not reported:
                    s += "Letter frequency checks\n\n"
                    reported = True
                if not report1:
                    s += "  singletons:\n"
                    report1 = True
                for i, line in enumerate(self.wb):
                    where = line.find(key)
                    if where != -1:
                        s += "{:>6} {:6} {}\n".format(key, i, line)
        for key in d.keys():
            if d[key] == 2:
                if not reported:
                    s += "Letter frequency checks\n\n"
                    reported = True
                if not report2:
                    s += "  doubletons:\n"
                    report2 = True
                for i, line in enumerate(self.wb):
                    where = line.find(key)
                    if where != -1:
                        s += "{:>6} {:6} {}\n".format(key, i, line)
        for key in d.keys():
            if d[key] > 2 and d[key] < 10:
                if not reported:
                    s += "Letter frequency checks\n\n"
                    reported = True
                if not report3:
                    s += "  characters with three to ten occurrences:\n"
                    report3 = True
                    s += "     "
                s += "{} ".format(key)
        return s

    def check_adjws(self, tn, td):
        s = ""
        reported = False
        count = 0

        for i, line in enumerate(self.wb):
            tmp = line.lstrip()  # ignore leading spaces
            if "  " in tmp:
                if not reported:
                    s += "Adjacent spaces check\n\n"
                    reported = True
                if not self.showall and count == 5:
                    s += "       ..... more"
                    count += 1
                if self.showall or count < 5:
                    s += "{:>6} {}\n".format(i+1, line)
                    count += 1
        if self.showall and not reported:
            self.areport("test {}: {} [no reports]".format(tn, td))
        return s

    def check_ast(self, tn, td):
        s = ""
        reported = False
        count = 0

        for i, line in enumerate(self.wb):
            if "*" in line:
                if line.count("*") == 5:  # do not show thought breaks
                    continue
            if "*" in line:
                if not reported:
                    s += "Asterisk check\n\n"
                    reported = True
                if not self.showall and count == 5:
                    s += "       ..... more"
                    count += 1
                if self.showall or count < 5:
                    s += "{:>6} {}\n".format(i+1, line)
                    count += 1
        if self.showall and not reported:
            self.areport("test {}: {} [no reports]".format(tn, td))

        return s

    # always -a all reports
    def check_ambrit(self, tn, td):
        s = ""
        c1 = re.search(r"\bMr\.", self.text)
        c2 = re.search(r"\bMr\s", self.text)
        c3 = re.search(r"\bMrs\.", self.text)
        c4 = re.search(r"\bMrs\s", self.text)
        c5 = re.search(r"\bDr\.", self.text)
        c6 = re.search(r"\bDr\s", self.text)
        has_Am = (c1 != None or c3 != None or c5 != None)
        has_Br = (c2 != None or c4 != None or c6 != None)
        if has_Am and has_Br:
            s = "both American and British abbreviations conventions found\n"
        if s != "":
            nmrp = self.text.count("Mr.")
            nmr = self.text.count("Mr") - nmrp  # account for double counting
            nmrsp = self.text.count("Mrs.")
            nmrs = self.text.count("Mrs") - nmrsp
            ndrp = self.text.count("Dr.")
            ndr = self.text.count("Dr") - ndrp
            s += "  Count of occurrences: Mr={} Mr.={} Mrs={} Mrs.={} Dr={} Dr.={}".format(
                nmr, nmrp, nmrs, nmrsp, ndr, ndrp)

        if self.showall and not (has_Am or has_Br):
            self.areport("test {}: {} [no reports]".format(tn, td))
        return s

    # always a limited representative display.
    def check_today(self, *_):
        s = ""
        s += "Today/To-day checks\n"
        ntoday = nto_day = ntomorrow = nto_morrow = 0
        c1 = re.search(r"\bto-day", self.text, flags=re.IGNORECASE)
        c2 = re.search(r"\bto-morrow", self.text, flags=re.IGNORECASE)
        c3 = re.search(r"\btoday", self.text, flags=re.IGNORECASE)
        c4 = re.search(r"\btomorrow", self.text, flags=re.IGNORECASE)
        mixed_today = (c1 != None and c3 != None)
        mixed_tomorrow = (c2 != None and c4 != None)

        if mixed_today:
            reported_today = reported_to_day = False
            s += "  Mixed \"today\" and \"to-day\" found in text.\n"
            for line in self.wb:
                if not reported_today and re.search("today", line, flags=re.IGNORECASE):
                    s += "    {}\n".format(line)
                    reported_today = True
                if not reported_to_day and re.search("to-day", line, flags=re.IGNORECASE):
                    s += "    {}\n".format(line)
                    reported_to_day = True

        if mixed_tomorrow:
            reported_tomorrow = reported_to_morrow = False
            s += "  Mixed \"tomorrow\" and \"to-morrow\" found in text.\n"
            for line in self.wb:
                if not reported_tomorrow and re.search("tomorrow", line, flags=re.IGNORECASE):
                    s += "    {}\n".format(line)
                    reported_today = True
                if not reported_to_morrow and re.search("to-morrow", line, flags=re.IGNORECASE):
                    s += "    {}\n".format(line)
                    reported_to_morrow = True

        if not mixed_tomorrow and not mixed_today:
            s += "     no errors found.\n"
        ntoday = self.text.count("today")
        ntoday += self.text.count("Today")
        nto_day = self.text.count("to-day")
        nto_day += self.text.count("To-day")
        ntomorrow = self.text.count("tomorrow")
        ntomorrow += self.text.count("Tomorrow")
        nto_morrow = self.text.count("to-morrow")
        nto_morrow += self.text.count("To-morrow")
        s += "     occurrences: today={} to-day={} tomorrow={} to-morrow={}".format(
            ntoday, nto_day, ntomorrow, nto_morrow)
        return s

    # check for turned comma (M‘Donnell) and normal apostrophe (M’Donnell)
    # should not have both forms
    def check_turnedcomma(self, tn, td):
        s = ""
        has_tc = has_ap = False
        for line in self.wb:
            if "M‘" in line:
                has_tc = True
                break
        for line in self.wb:
            if "M’" in line:
                has_ap = True
                break

        if self.showall and not (has_tc and has_ap):
            self.areport("\ntest {}: {} [no reports]".format(tn, td))

        if has_tc and has_ap:
            s = "both turned comma and apostrophe name contractions found."
        return s

    # if document has all straight or all curly quotes, there is no error.
    # if it has some of both, report it.
    def check_qmarks(self, tn, td):
        s = ""
        has_curly = re.search("[‘“’”]", self.text)
        has_straight = re.search("[\"']", self.text)

        if self.showall and not (has_curly and has_straight):
            self.areport("test {}: {} [no reports]".format(tn, td))

        if has_straight and has_curly:
            s = "both straight and curly quotes found in text"
        return s

    # check for line shorter than SHORTEST_PG_LINE that are not followed by
    # a blank line (i.e. the last line of a paragraph)
    #
    # 31-Dec-2017 if there are a *lot* of short lines, don't report them
    # individually.
    def check_short(self, tn, td):
        s = stmp = ""
        reported = False
        count = 0

        for i, line in enumerate(self.wb):
            if i == len(self.wb) - 1:
                continue  # no tests on last line
            if len(line) == 0:
                continue  # empty line
            if line.startswith(" "):
                continue  # no checks on centered lines
            if len(self.wb[i]) < self.SHORTEST_PG_LINE and len(self.wb[i+1]) > 0:
                if not reported:
                    stmp += "Short lines check\n\n"
                    reported = True
                if not self.showall and count == 5:
                    stmp += "       ..... more"
                if self.showall or count < 5:
                    stmp += "{:>6} {}\n".format(i+1, line)
                    stmp += "       {}\n".format(self.wb[i+1])
                count += 1

        if self.showall and not reported:
            self.areport("test {}: {} [no reports]".format(tn, td))

        # if there were a lot, put a short message
        # else report the short lines
        if count > 20:
            s += "Short lines check\n\n"
            s += "      more that 20 short lines detected ({}). Not reporting them.".format(
                count)
        else:
            s = stmp
        return s

    def check_long(self, tn, td):
        s = ""
        reported = False
        count = 0

        very_long_count = 0
        for i, line in enumerate(self.wb):
            if i == len(self.wb) - 1:
                continue  # no tests on last line
            if len(self.wb[i]) > self.WAY_TOO_LONG:
                very_long_count += 1
            if len(self.wb[i]) > self.LONGEST_PG_LINE:
                if not reported:
                    s += "Long lines check\n\n"
                    reported = True
                if not self.showall and count == 5:
                    s += "       ..... more"
                    count += 1
                if self.showall or count < 5:
                    s += "{:>6} ({}) {}\n".format(i+1, len(line), line)
                    s += "       {}\n".format(self.wb[i+1])
                    count += 1
        if very_long_count > 0:
            s += "       {} lines are very long\n".format(very_long_count)

        if self.showall and not reported:
            self.areport("test {}: {} [no reports]".format(tn, td))

        return s

    # currently has no limit (-a behaviour)
    def check_scannos(self, *_):
        s = ""
        reported = False
        # combine scannos lists
        cscannos = list(set(self.scannoslist + self.gcscannoslist))
        for t1 in cscannos:
            word_reported = False
            report_count = 0
            # re8 = regex.compile("[ ^“‘\(]{}[$ :;\?\.”’!\),]".format(t3))
            re8 = re.compile(r"[ ^“‘\(]{}[$ :;\?\.”’!\),]".format(t1))
            hits = re8.finditer(self.text)
            for hit in hits:
                if not reported:
                    reported = True
                    s += "Common scannos check:\n"
                if report_count < 5:
                    if not word_reported:
                        word_reported = True
                        s += "  " + t1 + "\n"  # the word
                    # s += "  " + self.add_report_s(hit.span(), "3,3", t1) old
                    s += "  " + self.add_report_s(hit.span(), "3,3")
                    if not self.showall:
                        report_count += 1
                    continue
                if report_count >= 5:
                    report_count += 1
            if report_count > 5:
                s += "          ..... ({} more)\n".format(report_count - 5)
        return s

    ####################################################################
    # file operations                                                  #
    ####################################################################

    # load file from specified source file into working buffer
    # accepts UTF-8 with or without BOM, Latin-1 or plain ASCII
    # on input, even if cr/lf found it is converted to \n
    def loadFile(self, fn):

        # try UTF-8
        # if it works, it's either UTF-8 or it's ASCII
        try:
            self.text = open(fn, "rU", encoding='UTF-8').read()
            self.encoding = "UTF-8"
            # remove BOM on first line if present
            t = ":".join("{0:x}".format(ord(c)) for c in self.text)
            if t[0:4] == 'feff':
                self.text = self.text[1:]
        except UnicodeDecodeError:
            # hope that it's readable as Latin-1
            try:
                self.text = open(self.srcfile, "r",
                                 encoding='iso-8859-1').read()
                self.encoding = "iso-8859-1"
            except UnicodeDecodeError:
                self.fatal(
                    "loadFile: cannot open source file {}".format(self.srcfile))

        self.wb = self.text.split("\n")
        self.wb = [s.rstrip() for s in self.wb]

    # save specified buffer (list) to named file
    # if user only gives a filename, put it in the same folder
    #    as the source file.
    # if user gives a full path, then use that.
    def saveFile(self, buffer, fn):
        # see if we have a qualified name or not
        base = os.path.basename(fn)
        # if they're equal, user gave us an unqualified name (just a file name,
        # no path to it)
        if base == fn:
                # construct path into source directory
            fn = os.path.join(os.path.dirname(
                os.path.realpath(self.srcfile)), fn)
        if self.debug:
            print("save filename: {}".format(fn))
        f1 = open(fn, "w", encoding="UTF-8")
        # if using cr/lf
        # buffer = re.sub(r"\n", r"\r\n", buffer)
        f1.write('\ufeff')  # BOM mark
        f1.write("generated by ppgutc (version {})\n".format(self.VERSION))
        # f1.write("source file: {}".format(options.infile.split('/')[-1]))
        f1.write("run completed: {}\n".format(self.NOW))
        f1.write("note: ⤶ represents a line break\n")
        f1.write("\n")
        f1.write(buffer)
        f1.close()

    ####################################################################
    # reporting operations                                             #
    ####################################################################

    def areport(self, s):
        self.report += s.rstrip() + "\n"

    # return s a string
    def add_report_s(self, thespan, how):
        if "," in how:
            theline = self.text[:thespan[0]].count("\n")+1
            howt = how.split(',')
            leftwords = int(howt[0])
            rightwords = int(howt[1])
            lloc = int(thespan[0])
            rloc = int(thespan[1])
            while leftwords > 0:
                lloc = self.text.rfind(" ", 0, lloc-1)
                leftwords -= 1
            while rightwords > 0:
                rloc = self.text.find(" ", rloc+1, -1)
                rightwords -= 1
            s = self.text[lloc:rloc].strip()
            s = re.sub(r"\n", "⤶", s)
            s = (s[:75] + ' ...') if len(s) > 75 else s
            # if self.highlight and word != "":
            #    s = re.sub(word, '\033[31;49m{}\033[m'.format(word), s)
            result = "{:6d}  {}\n".format(theline, s)
            return result

    # adds report directly
    def add_report(self, thespan, how):
        if "," in how:
            theline = self.text[:thespan[0]].count("\n")+1
            howt = how.split(',')
            leftwords = int(howt[0])
            rightwords = int(howt[1])
            lloc = int(thespan[0])
            rloc = int(thespan[1])
            while leftwords > 0:
                lloc = self.text.rfind(" ", 0, lloc-1)
                leftwords -= 1
            while rightwords > 0:
                rloc = self.text.find(" ", rloc+1, -1)
                rightwords -= 1
            s = self.text[lloc:rloc].strip()
            s = re.sub(r"\n", "⤶", s)
            s = (s[:75] + ' ...') if len(s) > 75 else s
            # if self.highlight and word != "":
            #    s = re.sub(word, '\033[31;49m{}\033[m'.format(word), s)
            self.areport("{:6d}  {}".format(theline, s))
            # self.areport("-----")

    ####################################################################
    # entry point for main program                                     #
    ####################################################################

    def run(self):

        self.loadFile(self.srcfile)

        # run the regular expression or call the named routine
        # t3 has five components:
        #  t3[0] test number
        #  t3[1] whether it's a re or a function
        #  t3[2] how to disply the results
        #  t3[3] a description of the check
        #  t3[4] the re or the function name
        # for each entry in actionlist
        for t3 in self.actionlist:
            if self.debug:
                print(t3[0], t3[3])
            if str(t3[0]) in self.skiptests:
                self.areport("\ntest {} skipped: {}".format(t3[0], t3[3]))
                continue
            # 'r' means run a regular expression
            if t3[1] == "r":
                reported = False
                count = 0
                hits = re.finditer(t3[4], self.text, re.MULTILINE)
                if hits:
                    for hit in hits:
                        if not reported:
                            reported = True
                            self.areport("\ntest {}: {}".format(t3[0], t3[3]))
                        if not self.showall and count == 5:
                            self.areport("        ..... more")
                            count += 1
                        if self.showall or count < 5:
                            self.add_report(hit.span(), t3[2])
                            count += 1
                if self.showall and not reported:
                    self.areport(
                        "test {}: {} [no reports]".format(t3[0], t3[3]))
            # 'm' means call a method
            if t3[1] == "m":
                method_name = t3[4]
                method_to_call = getattr(self, method_name)
                result = method_to_call(t3[0], t3[3])
                if len(result) > 0:
                    self.areport("\ntest {}: {}".format(t3[0], result))

        self.saveFile(self.report, self.outfile)

    def __str__(self):
        return "ppgutc"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--infile', help='input file', required=True)
    parser.add_argument('-o', '--outfile', help='output file', required=True)
    parser.add_argument(
        '-d', '--debug', help='debug (developer only)', action='store_true')
    parser.add_argument('-s', '--skiptests',
                        help='skip indicated tests', default="")
    parser.add_argument('-a', '--showall',
                        help='show all results', action='store_true')
    args = vars(parser.parse_args())
    return args


def main():
    args = parse_args()
    ppgutc = Ppgutc(args)
    ppgutc.run()


if __name__ == "__main__":
    sys.exit(main())
