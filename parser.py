#!/usr/bin/python3

"""
This module is a parser for chordpro source files. It reads them and builds the content object.
"""

import os
import re

class Song:
    def __init__(self, content):
        pass

class Processor:
    """ Process the input file and collect the information and tags from the chordpro format."""
    def __init__(self, inputfile):
        self.song_content = []
        self.structure = []
        self.header = {}
        self.lyrics = []
        self.chordlist = []
        self.environments = []
        
        # Read the input file and the get the list of lines.
        with open(inputfile) as f:
            content = f.readlines()
        for line in content:
            self.song_content.append(line.strip())

    def chordpro(self):
        """ Return the content of the chordpro file. """
        return self.song_content

    def parse(self, line):
        """ Parse the line, classify the content and return the values. """
        # Some of the directives use similar definition as metadata. The following list
        # holds all the available metadata.
        meta = ["title", "subtitle", "artist", "composer", "lyricist", "copyright", "album", "year", "key",
                "time", "tempo", "duration", "capo", "meta"]
        # Search for the header pattern in the line        
        if re.match(r"{(\w+):\s*(.+)}", line):
            match = re.search(r"{(\w+):\s*(.+)}", line)
            key = match.groups()[0]
            value = match.groups()[1]
            # But change into a directive, if we know that it is not a header.
            if key in meta:
                return ("header", key, value)
            else:               
                return ("directive", key, value)
        # Look for the environments patterns.        
        elif re.match(r"{(\w+)_of_(\w+)}", line):
            match = re.search(r"{(\w+)_of_(\w+)}", line)
            status = match.groups()[0]
            typ = match.groups()[1]
            return ("environment", status, typ)
        # Some environment can be defined via shortcuts, this one looks for chorus
        # definition, soc.
        elif re.match(r"{([se]oc)}", line):
            match = re.search(r"{([se]oc)}", line)
            match = match.groups()[0]
            if match[0] == "s":
                status = "start"
            elif match[0] == "e":
                status = "end"
            typ = "chorus"
            return ("environment", status, typ)
        # Look for short cut for tabs, sot.    
        elif re.match(r"{([se]ot)}", line):
            match = re.search(r"{([se]ot)}", line)
            match = match.groups()[0]
            if match[0] == "s":
                status = "start"
            elif match[0] == "e":
                status = "end"
            typ = "tabulature"
            return ("environment", status, typ)
        # Look for directives keywords.    
        elif re.match(r"{(\w+)}", line):
            match = re.search(r"{(\w+)}", line)
            whole = match.group()
            match = match.groups()[0]
            label = None
            if ":" in whole:
                label = whole.split(":")[1].strip()
            return ("directive", match, label)
        # Look if there are any chords in the line.
        elif re.match(r".+(\[.+\])", line):
            return ("chords", line)
        # If nothing is recognized, just return the clear line.
        else:
            return ("clear", line)
            
        
def main():
    print("Chordpro parser, version 0.1")
    song = Song(["name"])
    processor = Processor("ricka.cho")

    raw = processor.chordpro()
    for i in raw:
        print(i)
        res = processor.parse(i)
        print(res)


if __name__ == "__main__":
    main()
