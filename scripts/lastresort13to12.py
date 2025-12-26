#! /usr/bin/env python3

__version__ = "1.0.0"
__date__ = "2022-08-05"
__author__ = "Dr Ken Lunde (lunde@unicode.org)"
__doc__ = """lastresort13to12 version %s (%s) by %s

This script, which is closely tied to the open source "Last Resort" fonts,
takes as its only argument an XML file that is a ttx-generated Format
13 'cmap' subtable, and generates the following three files:

mergefonts.map
GlyphOrderAndAliasDB2
cmap-f12.ttx

The "mergefonts.map" file is an AFDKO "mergefonts" mapping file that is
used to generate up to 16 instances of each glyph in the original font,
except for the 18 glyphs whose names begin with "lastresortnotaunicode"
that are used to display the 66 noncharacter code points.

The "GlyphOrderAndAliasDB2" file is used by AFDKO "makeotf" to specify
the glyph set and glyph order of the font.

The "cmap-f12.ttx" file is a ttx-based XML file that specifies Format 4
and Format 12 'cmap' subtables that map all 1,114,112 code points to the
glyph names that are specified in "mergefonts.map" file. Note that the
Format 4 'cmap' subtable necessarily excludes a mapping for U+FFFF
(<not a character>) and therefore maps only 65,535 code points.

Dependencies: None""" % (__version__, __date__, __author__)

import re
import sys

def main(args=None):

    ttxfile = open(sys.argv[1], "r")
    cmap = open("cmap-f12.ttx", "w")
    mergeMap = open("mergefonts.map", "w")
    GOADB = open("GlyphOrderAndAliasDB2", "w")

    glyphs = set()

    data, data16 = [""] * 2
    sp = " " * 6
    lr = "lastresort"

    # Special-case the Last Resort "notdef" and "notaunicode" glyphs,
    # to ensure that latter glyphs are not duplicates, and so that
    # both sets of glyphs appear first in the subsequent font

    mergeMap.write(f"mergefonts\n.notdef\t.notdef\n")
    GOADB.write(f".notdef\t.notdef\n")

    notdef = ["notdefplanezero", "notdefplaneone", "notdefplanetwo",
              "notdefplanethree", "notdefplanefour", "notdefplanefive",
              "notdefplanesix", "notdefplaneseven", "notdefplaneeight",
              "notdefplanenine", "notdefplaneten", "notdefplaneeleven",
              "notdefplanetwelve", "notdefplanethirteen",
              "notdefplanefourteen", "privateplane15", "privateplane16"]

    for glyph in notdef:
        for last in range(int("0",16), int("F",16) + 1):
            mergeMap.write(f"{lr}{glyph}_{last:x}\t{lr}{glyph}\n")
            GOADB.write(f"{lr}{glyph}_{last:x}\t{lr}{glyph}_{last:x}\n")
            glyphs.add(lr + glyph + "_" + str(last))

    notaunicode = ["arabic", "", "1", "2", "3", "4", "5", "6", "7", "8",
                   "9", "10", "11", "12", "13", "14", "15", "16"]

    for glyph in notaunicode:
        mergeMap.write(f"{lr}notaunicode{glyph}\t{lr}notaunicode{glyph}\n")
        GOADB.write(f"{lr}notaunicode{glyph}\t{lr}notaunicode{glyph}\n")

    mapRegex = re.compile(r"<map code=\"0x([0-9a-f]+)\" name=\"(.+)\"\/>")

    # Iterate through the Format 13 'cmap' subtable XML file

    for line in map(str.rstrip, ttxfile):
        if mapRegex.search(line):
            code = mapRegex.search(line).group(1)
            glyph = mapRegex.search(line).group(2)
        else:
            continue
        if re.search("notaunicode", line):
            data += f"{line}\n"
            if len(code) <= 4 and code != "ffff":
                data16 += f"{line}\n"
        else:
            last = int(re.search("([0-9a-f])$", code).group(1),16)
            data += f"{sp}<map code=\"0x{code}\" name=\"{glyph}_{last:x}\"/>\n"
            if len(code) <= 4:
                data16 += f"{sp}<map code=\"0x{code}\" name=\"{glyph}_{last:x}\"/>\n"
            if glyph + "_" + str(last) not in glyphs:
                mergeMap.write(f"{glyph}_{last:x}\t{glyph}\n")
                GOADB.write(f"{glyph}_{last:x}\t{glyph}_{last:x}\n")
                glyphs.add(glyph + "_" + str(last))

    # Create the contents of the XML file

    xml = """<?xml version="1.0" encoding="UTF-8"?>
<ttFont sfntVersion="\\x00\\x01\\x00\\x00" ttLibVersion="4.33">

  <cmap>
    <tableVersion version="0"/>
    <cmap_format_4 platformID="3" platEncID="1" language="0">
{}    </cmap_format_4>
    <cmap_format_12 platformID="3" platEncID="10" format="12" reserved="0" length="851536" language="0" nGroups="70960">
{}    </cmap_format_12>
  </cmap>

</ttFont>
""".format(data16, data)

    cmap.write(xml)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
