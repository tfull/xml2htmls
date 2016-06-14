# coding: UTF-8

import sys
from xml.etree.ElementTree import XMLParser
from XMLData import XMLError
from XMLData import XMLTree
import Method as M

def main(name):
    with open(name, "r") as f:
        parser = XMLParser()

        for line in f:
            parser.feed(line)

        xml = XMLTree(parser.close(), False)

        M.run(xml.get("files"), xml.get("structure"), xml.get("pages"))


if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        sys.stderr.write("wrong number of arguments\n")
