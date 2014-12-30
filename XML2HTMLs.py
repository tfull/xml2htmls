# coding: UTF-8

import sys
from xml.etree.ElementTree import XMLParser

INDENT = ' '

class XMLError(Exception):
    pass

class XMLTree:
    def __init__(self, tag_or_tree, flag=True):
        if flag:
            self.tag = tag_or_tree
            self.text = None
            self.children = []
            self.attribute = {}
        else:
            self.tag = tag_or_tree.tag
            self.text = None if tag_or_tree.text == None else tag_or_tree.text.strip()
            self.children = [XMLTree(child, False) for child in tag_or_tree.getchildren()]
            self.attribute = tag_or_tree.attrib

    def set(self, text, children, attribute):
        self.text = None if text == None else text.strip()
        self.children = children
        self.attribute = attribute

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
        if self.text == None and len(self.children) == 0:
            return ("<{0}{1} />".format(self.tag, a), None)
        else:
            return ("<{0}{1}>".format(self.tag, a), "</{0}>".format(self.tag))

def main(name):
    with open(name, "r") as f:
        parser = XMLParser()

        for line in f:
            parser.feed(line)

        xml = XMLTree(parser.close(), False)

        run(xml)

def collect_htmls(structure):
    return [(e.get("name").text, e.get("title").text) for e in structure.get_all("html")]

def attribute(xml):
    return " ".join([key + "='" + xml.attribute[key] + "'" for key in xml.attribute])

def run(xml):
    tmp = None;

    template = int(xml.get("template").text)

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

    if template == 1:
        method1(data, pages)
    else:
        raise XMLError("no such template")

def method1(data, pages):
    # [header, nav, article, aside, footer] = [data["body"].get_all(t) for t in ["header", "nav", "article", "aside", "footer"]]

    for p in pages.children:
        with open(p.get("name").text, "w") as f:
            make1(f, data, p)

def make1(f, data, xml):
    name = xml.get("name").text
    title = xml.get("title").text

    f.write("<!DOCTYPE html>\n")
    f.write("<html lang=\"ja\">\n")
    f.write("<head>\n")
    f.write("{0}<title>{1}</title>\n".format(data["indent"], data["title"] + " - " + title))
    f.write("{0}<meta charset=\"{1}\" />\n".format(data["indent"], data["charset"]))
    tmp = xml.find("keywords")
    if tmp:
        f.write("{0}<meta name=\"keywords\" content=\"{1}\" />\n".format(data["indent"], tmp.text))
    tmp = xml.find("description")
    if tmp:
        f.write("{0}<meta name=\"description\" content=\"{1}\" />\n".format(data["indent"], tmp.text))
    for css in data["css"]:
        f.write("{0}<link rel=\"stylesheet\" href=\"{1}\" type=\"text/css\" />\n".format(data["indent"], css))
    for js in data["js"]:
        f.write("{0}<script type=\"text/javascript\" src=\"{1}\"></script>\n".format(data["indent"], js))
    f.write("</head>\n")
    f.write("<body>\n")

    def rec(xml, indent):
        (tag0, tag1) = xml.tag_s()
        if xml.tag == "codefile": # code
            if "name" not in xml.attribute:
                raise XMLError("no name in codefile")
            with open(xml.attribute["name"]) as codefile:
                for line in codefile:
                    f.write(line.rstrip() + "\n")
        elif tag1 == None: # single
            f.write((data["indent"] * indent) + tag0 + "\n")
        else:
            if len(xml.children) > 0:
                f.write((data["indent"] * indent) + tag0 + "\n")
                for child in xml.children:
                    rec(child, indent + 1)
                f.write((data["indent"] * indent) + tag1 + "\n")
            else:
                f.write("{0}{1}{3}{2}\n".format(data["indent"] * indent, tag0, tag1, xml.text))

    def construct(s, indent):
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
            tmp = elems[0].children
            elems[0].children = [c for e in elems for c in e.children]
            rec(elems[0], indent)
            for (e, o) in zip(elems, ors):
                e.attribute["order"] = o
            elems[0].children = tmp

    nav = XMLTree("nav")
    nav.attribute["order"] = 1

    ul = XMLTree("ul")
    ul.attribute["id"] = "links"

    nav.children.append(ul)

    for (n, t) in data["html"]:
        d = {}
        c = []
        txt = None
        if n == name:
            d = { "class": "checked" }
            txt = t
        else:
            a = XMLTree("a")
            a.set(t, [], { "href": n })
            c.append(a)
        li = XMLTree("li")
        li.set(txt, c, d)
        ul.children.append(li)

    data["body"].children.append(nav)

    construct("header", 1)
    f.write(data["indent"] + "<div id=\"main\">\n")
    f.write(data["indent"] * 2 + "<div id=\"side\">\n")
    construct("nav", 3)
    construct("aside", 3)
    f.write(data["indent"] * 2 + "</div>\n" )
    construct("article", 2)
    f.write(data["indent"] + "</div>\n")
    construct("footer", 1)

    data["body"].children.remove(nav)

    f.write("</body>\n")
    f.write("</html>\n")

if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        sys.stderr.write("wrong number of arguments\n")
