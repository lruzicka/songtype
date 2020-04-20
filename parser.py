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
        self.header = {}
        self.song_structure = []
        self.stanzas = []
        self.choruses = []
        self.chordlist = []
        self.environments = []
        self.tabs = []
        self.directives = []
        
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
        #elif re.match(r".+(\[.+\])", line):
        #    return ("chords", line)
        elif line == "":
            return("environment", "divider", "verse")
        # If nothing is recognized, just return the clear line.
        else:
            return ("lyrics", line)

    def translate(self):
        """ Go through all the content and sort it according to the classification.  """
        envopen = False
        envtype = None
        buff = []
        for line in self.song_content:
            environment = {}
            print(line)
            translation = self.parse(line)
            if translation[0] == "header":
                self.header[translation[1]] = translation[2]
                if "header" not in self.song_structure:
                    self.song_structure.append("header")
            elif translation[0] == "environment":
                status = translation[1]
                envtype = translation[2]
                if status == "start":
                    envopen = True
                    buff = []
                elif status == "divider":
                    if envopen == False:
                        envopen = True
                        buff = []
                        print(f"Opening {envtype}")
                    else:
                        if len(buff) > 0:
                            print(f"Continuing into another {envtype}")
                            l = [x for x in buff]
                            environment[envtype] = l
                            self.song_structure.append(envtype)
                            self.environments.append(environment)
                            del(buff)
                            buff = []
                elif status == "end":
                    envopen = False
                    print(buff)
                    environment[envtype] = buff
                    self.song_structure.append(envtype)
                    self.environments.append(environment)
            elif translation[0] == "directive":
                if len(translation) > 2:
                    directive = {translation[1]:translation[2]}
                else:
                    directive = {translation[1]:"not_specified"}
                self.directives.append(directive)
                self.song_structure.append("directive")
            elif translation[0] == "lyrics":
                line = translation[1]
                parts = line.split()
                newline = []
                for part in parts:
                    match = re.findall(r"(\w*\[\w+\]\w+)", part)
                    if len(match) > 0:
                        for m in match:
                            chordword = {}
                            detail = re.search(r"(\w*)(\[\w+\])(\w+)", m)
                            prefix = detail.groups()[0]
                            chord = re.search(r"\[(\w+)\]", detail.groups()[1])
                            chord = chord.groups()[0]
                            root = detail.groups()[2]
                            chordword = {"prefix":prefix, "chord":chord, "root":root}
                            if chord not in self.chordlist:
                                self.chordlist.append(chord)
                            newline.append(chordword)
                    else:
                        word = {"root":part}
                        newline.append(word)
                buff.append(newline)
            else:
                pass

        # Go through the list of environments and categorize it, too
        for env in self.environments:
            if "verse" in env.keys():
                self.stanzas.append(env)
            elif "chorus" in env.keys():
                self.choruses.append(env)

        print(self.chordlist)

    def songdata(self):
        songdata = {}
        songdata["header"] = self.header
        songdata["stanzas"] = self.stanzas
        songdata["choruses"] = self.choruses
        songdata["allenvs"] = self.environments
        songdata["used_chords"] = self.chordlist
        songdata["structure"] = self.song_structure
        songdata["directives"] = self.directives
        return songdata
            
        
def main():
    print("Chordpro parser, version 0.1")
    song = Song(["name"])
    processor = Processor("cernobile.cho")

    processor.translate()
    print(processor.songdata())

if __name__ == "__main__":
    main()
