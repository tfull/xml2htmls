# coding: UTF-8

import sys
from xml.etree.ElementTree import XMLParser

INDENT = ' '

class XMLError(Exception):
    pass

class XMLTree:
    def __init__(self, etree):
        self.tag = etree.tag
        self.text = None if etree.text == None else etree.text.strip()
        self.children = [XMLTree(child) for child in etree.getchildren()]
        self.attribute = etree.attrib
        self.single = self.text == None and len(self.children) == 0

    def exist(self, name):
        for child in self.children:
            if child.tag == name:
                return True
        return False

    def get(self, name):
        for child in self.children:
            if child.tag == name:
                return child
        raise XMLError("no {0} in {1}".format(name, self.tag))

    def find(self, name):
        for child in self.children:
            if child.tag == name:
                return child
        return None

    def get_all(self, name):
        return [child for child in self.children if child.tag == name]

    def tag_s(self):
        a = " ".join([key + "='" + self.attribute[key] + "'" for key in self.attribute])
        if len(a) > 0:
            a = " " + a
        if self.single:
            return ("<{0}{1} />".format(self.tag, a), None)
        else:
            return ("<{0}{1}>".format(self.tag, a), "</{0}>".format(self.tag))

def main(name):
    with open(name, "r") as f:
        parser = XMLParser()

        for line in f:
            parser.feed(line)

        xml = XMLTree(parser.close())

        run(xml)

def collect_htmls(structure):
    return [(e.get("name").text, e.get("title").text) for e in structure.get_all("html")]

def attribute(xml):
    return " ".join([key + "='" + xml.attribute[key] + "'" for key in xml.attribute])

def run(xml):
    tmp = None;

    template = xml.get("template")

    tmp = int(template.text)
    if tmp in [1]:
        template = tmp 

    structure = xml.get("structure")
    pages = xml.get("pages")

    data = {}
    data["html"] = collect_htmls(structure)
    data["css"] = [e.text for e in structure.get_all("css")]
    data["js"] = [e.text for e in structure.get_all("js")]
    data["title"] = structure.get("title").text
    data["charset"] = structure.get("charset").text if structure.exist("charset") else "UTF-8"
    data["body"] = structure.get("body")
    data["indent"] = INDENT

    method1(data, pages)

def method1(data, pages):
    # [header, nav, article, aside, footer] = [data["body"].get_all(t) for t in ["header", "nav", "article", "aside", "footer"]]

    for p in pages.children:
        with open(p.get("name").text, "w") as f:
            make1(f, data, p)

def make1(f, data, xml):
    title = xml.get("title").text

    f.write("<!DOCTYPE html>\n")
    f.write("<html lang=\"ja\">\n")
    f.write("<head>\n")
    f.write("{0}<title>{1}</title>\n".format(data["indent"], data["title"] + " - " + title))
    f.write("{0}<meta charset=\"{1}\" />\n".format(data["indent"], data["charset"]))
    for css in data["css"]:
        f.write("{0}<link rel=\"stylesheet\" href=\"{1}\" type=\"text/css\" />\n".format(data["indent"], css))
    for js in data["js"]:
        f.write("{0}<script type=\"text/javascript\" src=\"{1}\"></script>\n".format(data["indent"], js))
    f.write("</head>\n")
    f.write("<body>\n")

    def rec(xml, indent):
        (tag0, tag1) = xml.tag_s()
        if tag1 == None: # single
            f.write((data["indent"] * indent) + tag0 + "\n")
        else:
            if len(xml.children) > 0:
                f.write((data["indent"] * indent) + tag0 + "\n")
                for child in xml.children:
                    rec(child, indent + 1)
                f.write((data["indent"] * indent) + tag1 + "\n")
            else:
                f.write("{0}{1}{3}{2}\n".format(data["indent"] * indent, tag0, tag1, xml.text))

    def construct(s):
        def lg(e):
            return int(e.attribute["order"])

        elems = data["body"].get_all(s)
        elems.extend(xml.get_all(s))
        for e in elems:
            if "order" in e.attribute:
                e.attribute["order"] = int(e.attribute["order"])
            else:
                e.attribute["order"] = 0

        if len(elems) > 0:
            elems = sorted(elems, key=lg)
            ors = [e.attribute.pop("order") for e in elems]
            print(s, ors)

            tmp = elems[0].children
            elems[0].children = [c for e in elems for c in e.children]
            rec(elems[0], 1)
            for (e, o) in zip(elems, ors):
                e.attribute["order"] = o
            elems[0].children = tmp

    construct("header")
    construct("nav")
    construct("article")
    construct("aside")
    construct("footer")
    # article = data["body"].get("article")
    # tmp = article.children
    # article.children = xml.get_all("article").children
    # rec(article, 1)
    # article.children = tmp

    f.write("</body>\n")
    f.write("</html>\n")

if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        sys.stderr.write("wrong number of arguments\n")
