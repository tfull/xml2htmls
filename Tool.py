# coding: utf-8

def print_head(f, data, xml):
    title = xml.get("title").text

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

def print_xml(f, data, xml, indent):
    (tag0, tag1) = xml.tag_s()
    if xml.tag == "codefile": # code
        if "name" not in xml.attribute:
            raise XMLError("no name in codefile")
        with open(xml.attribute["name"]) as codefile:
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

def construct_part(f, data, xml, s, indent):
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
        print_xml(f, data, elems[0], indent)
        for (e, o) in zip(elems, ors):
            e.attribute["order"] = o
        elems[0].children = tmp
