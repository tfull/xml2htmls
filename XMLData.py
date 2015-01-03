# coding: utf-8

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
            self.text = None if tag_or_tree.text == None else tag_or_tree.text.strip().replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
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
        a = " ".join([key + "=\"" + self.attribute[key] + "\"" for key in self.attribute])
        if len(a) > 0:
            a = " " + a
        if self.text == None and len(self.children) == 0:
            return ("<{0}{1} />".format(self.tag, a), None)
        else:
            return ("<{0}{1}>".format(self.tag, a), "</{0}>".format(self.tag))