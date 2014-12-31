# coding: utf-8

from XMLData import XMLTree
from XMLData import XMLError
import Tool as T


def run(structure, pages):
    data = {}

    data["html"] = collect_htmls(structure)
    data["css"] = [e.text for e in structure.get_all("css")]
    data["js"] = [e.text for e in structure.get_all("js")]
    data["title"] = structure.get("title").text
    data["charset"] = structure.get("charset").text if structure.exist("charset") else "UTF-8"
    data["body"] = structure.get("body")
    data["indent"] = "\t"

    for p in pages.children:
        with open(p.get("name").text, "w") as f:
            make(f, data, p)

def collect_htmls(structure):
    return [(e.get("name").text, e.get("title").text) for e in structure.get_all("html")]

def make(f, data, xml):
    name = xml.get("name").text
    title = xml.get("title").text

    f.write("<!DOCTYPE html>\n")
    f.write("<html lang=\"ja\">\n")
    T.print_head(f, data, xml)
    f.write("<body>\n")

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

    T.construct_part(f, data, xml, "header", 1)
    f.write(data["indent"] + "<div id=\"main\">\n")
    f.write(data["indent"] * 2 + "<div id=\"side\">\n")
    T.construct_part(f, data, xml, "nav", 3)
    T.construct_part(f, data, xml, "aside", 3)
    f.write(data["indent"] * 2 + "</div>\n" )
    T.construct_part(f, data, xml, "article", 2)
    f.write(data["indent"] + "</div>\n")
    T.construct_part(f, data, xml, "footer", 1)

    data["body"].children.remove(nav)

    f.write("</body>\n")
    f.write("</html>\n")
