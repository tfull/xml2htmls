# coding: UTF-8

import sys
from xml.etree.ElementTree import XMLParser
from XMLData import XMLError
from XMLData import XMLTree
import Method1 as M1
import Method2 as M2

def main(name):
    with open(name, "r") as f:
        parser = XMLParser()

        for line in f:
            parser.feed(line)

        xml = XMLTree(parser.close(), False)

        run(xml)

def run(xml):
    template = int(xml.get("template").text)
    structure = xml.get("structure")
    pages = xml.get("pages")

    if template == 1:
        M1.run(structure, pages)
    elif template == 2:
        M2.run(structure, pages)
    else:
        raise XMLError("no such template")

if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        sys.stderr.write("wrong number of arguments\n")
