# coding: utf-8

import sys
from XMLData import XMLTree
from XMLData import XMLError

def run(files, structure, pages):
    data = {}

    try:
        data["html"] = collect_all_html(files)
        if len(data["html"]) == 0:
            data["section"] = collect_all_section(files)
            if len(data["section"]) == 0:
                raise XMLError("no files")
        data["css"] = collect_all_css(files)
        data["js"] = collect_all_js(files)
        title = structure.get("title").text
        if title == None:
            raise XMLError("no title")
        data["title"] = title
        data["charset"] = structure.get("charset").text if structure.exist("charset") else "UTF-8"
        if data["charset"] == None:
            raise XMLError("empty charset")
        data["template"] = make_template(structure.get("template"))
        data["body"] = structure.get("body")
        data["navtype"] = get_nav_type(structure)
        data["indent"] = get_indent(structure)
        data["lang"] = get_lang(structure)
    except XMLError as e:
        sys.stderr.write("Error: property")
        sys.stderr.write(e.message + "\n")
        return

    for (i, p) in enumerate(pages.children):
        try:
            path = p.get("path").text

            if path == None:
                raise XMLError("no path")

            with open(path, "w") as f:
                make(f, data, p)
        except XMLError as e:
            sys.stderr.write("Error: page " + str(i) + "\n")
            sys.stderr.write(e.message + "\n")
            return

def get_lang(xml):
    LANG = "ja"
    e = xml.find("lang")
    if e == None:
        return LANG
    s = e.text
    return s if s != None else LANG

def get_indent(xml):
    e = xml.find("indent")
    if e == None:
        return "\t"
    s = e.text
    if s == "tab":
        return "\t"
    elif s == "2":
        return "  "
    elif s == "4":
        return "    "
    else:
        sys.stderr.write("invalid indent, set tab\n")
        return "\t"

def get_nav_type(xml):
    e = xml.find("navtype")
    if e == None:
        return 1
    s = e.text
    if s == "normal":
        return 1
    elif s == "none":
        return 0
    else:
        sys.stderr.write("invalid navtype, set normal\n")
        return 1

def make_template(xml):
    header = xml.get_all("header")
    nav = xml.get_all("nav")
    article = xml.get_all("article")
    aside = xml.get_all("aside")
    footer = xml.get_all("footer")
    return { "header": header, "nav": nav, "article": article, "aside": aside, "footer": footer }

def collect_all_html(xml):
    array = []

    for html in xml.get_all("html"):
        path = html.get("path").text
        title = html.get("title").text

        if path == None:
            raise XMLError("no path in html")
        if title == None:
            raise XMLError("no title in html")

        array.append((path, title))

    return array

def collect_all_section(xml):
    array = []
    
    for section in xml.get_all("section"):
        s_title = section.find("title")
        if s_title != None:
            s_title = s_title.text
            if s_title == None:
                s_title = ""
        one = { "title": s_title, "html": [] }
        for html in section.get_all("html"):
            path = html.get("path").text
            title = html.get("title").text
            
            if path == None:
                raise XMLError("no path in html")
            if title == None:
                raise XMLError("no title in html")
            
            one["html"].append((path, title))

        array.append(one)
    
    return array

def collect_all_css(xml):
    return [e.text for e in xml.get_all("css") if e.text != None]

def collect_all_js(xml):
    return [e.text for e in xml.get_all("js") if e.text != None]

def make_navigation(path, data, navtype):
    if navtype == 0:
        return None
    elif navtype == 1:
        nav = XMLTree("nav")
        nav.attribute["order"] = 1

        ul = XMLTree("ul")
        ul.attribute["id"] = "links"

        nav.children.append(ul)

        for (n, t) in data["html"]:
            d = {}
            c = []
            txt = None
            if n == path:
                d = { "class": "checked" }
                txt = t
            else:
                a = XMLTree("a")
                a.set(t, [], { "href": n })
                c.append(a)
            li = XMLTree("li")
            li.set(txt, c, d)
            ul.children.append(li)
            
        return nav
    else:
        raise XMLError("no such type")

def write_body(f, data, template, xml, indent):
    if xml.tag in template:
        print_xml(f, data, template[xml.tag], indent)
    else:
        (tag0, tag1) = xml.tag_s()
        if tag1 == None:
            f.write((data["indent"] * indent) + tag0 + "\n")
        else:
            if len(xml.children) > 0:
                f.write((data["indent"] * indent) + tag0 + "\n")
                for child in xml.children:
                    write_body(f, data, template, child, indent + 1)
                f.write((data["indent"] * indent) + tag1 + "\n")
            else:
                f.write("{0}{1}{3}{2}\n".format(data["indent"] * indent, tag0, tag1, xml.text))

def make(f, data, page):
    path = page.get("path").text
    title = page.get("title").text
    if title == None:
        raise XMLError("no title in page")
        
    special = { "css": collect_all_css(page), "js": collect_all_js(page) }

    f.write("<!DOCTYPE html>\n")
    f.write("<html lang=\"{0}\">\n".format(data["lang"]))
    print_head(f, data, page, special)
    
    nav = make_navigation(path, data, data["navtype"])
    template = arrange_template(data["template"], page, nav)

    write_body(f, data, template, data["body"], 0)
    
    f.write("</html>\n")

def arrange_template(template, page, nav):
    def order(e):
        if "order" in e.attribute:
            return int(e.attribute["order"])
        else:
            return 0
            
    result = {}
    for t in template:
        xs = template[t] + page.get_all(t)
        if t == "nav" and nav != None:
            xs.append(nav)
        elems = sorted(xs, key=order)
        xml = XMLTree(t)
        xml.children = [child for elem in elems for child in elem.children]
        
        result[t] = xml
    
    return result

def print_head(f, data, xml, special):
    title = xml.get("title").text

    f.write("<head>\n")
    f.write("{0}<meta charset=\"{1}\" />\n".format(data["indent"], data["charset"]))
    f.write("{0}<title>{1}</title>\n".format(data["indent"], data["title"] + " - " + title))
    tmp = xml.find("keywords")
    if tmp != None and tmp.text != None:
        f.write("{0}<meta name=\"keywords\" content=\"{1}\" />\n".format(data["indent"], tmp.text))
    tmp = xml.find("description")
    if tmp != None and tmp.text != None:
        f.write("{0}<meta name=\"description\" content=\"{1}\" />\n".format(data["indent"], tmp.text))
    for css in data["css"] + special["css"]:
        f.write("{0}<link rel=\"stylesheet\" href=\"{1}\" type=\"text/css\" />\n".format(data["indent"], css))
    for js in data["js"] + special["js"]:
        f.write("{0}<script type=\"text/javascript\" src=\"{1}\"></script>\n".format(data["indent"], js))
    f.write("</head>\n")

def print_xml(f, data, xml, indent):
    (tag0, tag1) = xml.tag_s()
    if xml.tag == "codefile": # code
        if "path" not in xml.attribute:
            raise XMLError("no path in codefile")
        with open(xml.attribute["path"], "r") as codefile:
            for line in codefile:
                f.write(line.rstrip().replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") + "\n")
    elif tag1 == None: # single
        f.write((data["indent"] * indent) + tag0 + "\n")
    else:
        if len(xml.children) > 0:
            f.write((data["indent"] * indent) + tag0 + "\n")
            for child in xml.children:
                print_xml(f, data, child, indent + 1)
            f.write((data["indent"] * indent) + tag1 + "\n")
        else:
            f.write("{0}{1}{3}{2}\n".format(data["indent"] * indent, tag0, tag1, xml.text))
