r"""
## Description

Create unicode text rendering of directory structure trees.
"""

import fs
import yaml, json
from regx import Regx

regx = Regx()
regx.split

class StyleBasicUnicode():
    NODE_SPAN_NS   = "|  "
    NODE_CONT_NES  = "├──"
    NODE_CONT_NE   = "└──"
    NODE_BLANK     = "   "
    FILE_PREFIX    = "📄 "
    FOLDER_PREFIX  = "📁 " 
    FILE_SUFFIX    = ""
    FOLDER_SUFFIX  = "/"
    LINE_PREFIX    = ""
    LINE_SUFFIX    = ""

class Tree():

    def __init__(self, dir=dir, hide=None, regexp=True, ign_case=False, style=StyleBasicUnicode):
        me = self 
        me.reset(hide=hide, regexp=regexp, ign_case=ign_case, style=style)

    def reset(self, hide=None, regexp=True, ign_case=False, style=StyleBasicUnicode):
        me = self
        me.hide = hide
        me.regexp = regexp
        me.ign_case = ign_case
        me.style = style
        me.tree = []
        if me.hide is None: me.hide = []
        if type(me.hide) is str: me.hide = [me.hide]

    def from_path(self, dir, hide=None, regexp=True, ign_case=False, style=StyleBasicUnicode):
        me = self
        me.reset(hide=hide, regexp=regexp, ign_case=ign_case, style=style)
        me.__recursive_path_descent(dir)

    def from_yml(self, data, hide=None, regexp=True, ign_case=False, style=StyleBasicUnicode):
        pass

    def __recursive_path_descent(self, dir, indent=''):
        me = self

        regx = Regx()

        dirs = []
        files = []

        if indent == '': me.tree.append(fs.get_file_name(dir))

        groups = [(dirs, fs.get_dirs(dir)), (files, fs.get_files(dir, rec=False))]

        for lst,paths in groups:
            for path in paths:
                name = fs.get_file_name(path)
                if me.ign_case: name = name.lower()
                if len(me.hide) > 0:
                    if me.regexp:
                        omit = False
                        for hide in me.hide:
                            if me.ign_case: hide = hide.lower()
                            if regx.m(name, hide): omit = True
                        if not omit: lst.append(path)
                    else:
                        omit = False
                        for hide in me.hide:
                            if me.ign_case: hide = hide.lower()
                            if hide not in name: omit = True
                        if not omit: lst.append(path)
                else:
                    lst.append(path)
        
        while len(dirs) > 0:
            path = dirs.pop(0)
            name = fs.get_file_name(path)
            last = True if len(dirs) == 0 and len(files) == 0 else False
            pre = me.style.NODE_CONT_NE if last else me.style.NODE_CONT_NES
            this_indent = indent + pre
            me.tree.append(this_indent + me.style.FOLDER_PREFIX + name + me.style.FOLDER_SUFFIX)
            if last: this_indent = indent + me.style.NODE_BLANK
            else: this_indent = indent + me.style.NODE_SPAN_NS
            me.__recursive_path_descent(path, indent=this_indent)
        
        while len(files) > 0:
            path = files.pop(0)
            pre = me.style.NODE_CONT_NES if len(files) > 0 else me.style.NODE_CONT_NE
            name = fs.get_file_name(path)
            me.tree.append(indent + pre + me.style.FILE_PREFIX + name + me.style.FILE_SUFFIX)
        
    def __get_tree_from_path(self, dir):
        me = self
        me.tree = []
        me.__recursive_path_descent(dir)

    def to_str(self):
        me = self
        return('\n'.join(me.tree))

    def print(self):
        me = self
        print('\n'.join(me.tree))

