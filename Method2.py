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
    value = []

    sections = structure.get_all("section")

    for sec in sections:
        value.append((sec.get("title").text, [(html.get("name").text, html.get("title").text) for html in sec.get_all("html")]))

    return value

def make(f, data, xml):
    name = xml.get("name").text
    title = xml.get("title").text

    f.write("<!DOCTYPE html>\n")
    f.write("<html lang=\"ja\">\n")
    T.print_head(f, data, xml)
    f.write("<body>\n")

    nav = XMLTree("nav")
    nav.attribute["order"] = 1

    div = XMLTree("div")
    div.attribute["id"] = "links"

    nav.children.append(div)

    data["body"].children.append(nav)

    for sec in data["html"]:
        div_p = XMLTree("div")
        div_c = XMLTree("div")
        ul = XMLTree("ul")

        div_p.children.append(div_c)
        div_p.children.append(ul)

        div_c.set(sec[0], [], {})

        for (n, t) in sec[1]:
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
        div.children.append(div_p)

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
