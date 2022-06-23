r"""
## Description

Create unicode text rendering of directory structure trees.
"""

import fs
import yaml, json
from rex import Rex

rex = Rex()
rex.split

class StyleBasicUnicode():
    NODE_SPAN_NS   = "│  "
    NODE_CONT_NES  = "├──"
    NODE_CONT_NE   = "└──"
    NODE_BLANK     = "   "
    ROOT_PREFIX    = "💻 "
    FILE_PREFIX    = "📄 "
    FOLDER_PREFIX  = "📁 " 
    ROOT_SUFFIX    = "/"
    FILE_SUFFIX    = ""
    FOLDER_SUFFIX  = "/"
    LINE_PREFIX    = ""
    LINE_SUFFIX    = ""

class StyleBasicASCII():
    NODE_SPAN_NS   = " |  "
    NODE_CONT_NES  = " |--"
    NODE_CONT_NE   = " +--"
    NODE_BLANK     = " "
    ROOT_PREFIX    = " "
    FILE_PREFIX    = " "
    FOLDER_PREFIX  = " " 
    ROOT_SUFFIX    = "/"
    FILE_SUFFIX    = ""
    FOLDER_SUFFIX  = "/"
    LINE_PREFIX    = ""
    LINE_SUFFIX    = ""

class Tree():

    def __init__(self, dir=dir, hide=None, regexp=True, ign_case=False, style=None):
        me = self 
        me.style = style if style is not None else StyleBasicUnicode
        me.reset(hide=hide, regexp=regexp, ign_case=ign_case, style=style)

    def reset(self, hide=None, regexp=True, ign_case=False, style=None):
        me = self
        me.hide = hide
        me.regexp = regexp
        me.ign_case = ign_case
        me.style = style if style is not None else StyleBasicUnicode
        me.tree = []
        if me.hide is None: me.hide = []
        if type(me.hide) is str: me.hide = [me.hide]

    def from_path(self, dir, hide=None, regexp=True, ign_case=False, style=None):
        me = self
        me.reset(hide=hide, regexp=regexp, ign_case=ign_case, style=me.style)
        me.__recursive_path_descent(dir)

    def from_dict(self, data, name='Top', hide=None, regexp=True, ign_case=False, style=None):
        me = self
        me.name = name
        me.reset(hide=hide, regexp=regexp, ign_case=ign_case, style=me.style)
        me.__recursive_data_descent(data)

    def __recursive_path_descent(self, dir, indent=''):
        me = self

        # Initialize variables.
        rex = Rex()
        dirs = []
        files = []

        # If indent is nothing, we are at the top level.  
        if indent == '': me.tree.append(me.style.ROOT_PREFIX + fs.get_file_name(dir)  + me.style.ROOT_SUFFIX)
        # Given `dir` file path, we first process folders in the the target directory, then 
        # files.
        groups = [(dirs, fs.get_dirs(dir)), (files, fs.get_files(dir, rec=False))]
        # List `lst` is originally empty, referring to `dirs` and `files` respectively on 
        # first and second passes.  List `paths` will be the subfolders and files found in the
        # current directory.
        for lst,paths in groups:
            for path in paths:
                # Get the base name from the path of either the subfolder or file.
                name = fs.get_file_name(path)
                # If `ign_case` is True, then convert `name` to lower case.
                if me.ign_case: name = name.lower()
                # If `hide` parameter list has elements, process them ...
                if len(me.hide) > 0:
                    # Hide elements are regular expressions if `regexp` is True ...
                    if me.regexp:
                        omit = False
                        for hide in me.hide:
                            if me.ign_case: hide = hide.lower()
                            if rex.m(name, hide): omit = True
                        # If subfolder or file is not omitted, push onto `lst`.
                        if not omit: lst.append(path)
                    # ... otherwise hide elements are literals.  
                    else:
                        omit = False
                        for hide in me.hide:
                            if me.ign_case: hide = hide.lower()
                            if hide not in name: omit = True
                        # If subfolder or file is not omitted, push onto `lst`.
                        if not omit: lst.append(path)
                # ... automatically push onto `lst`.
                else:
                    lst.append(path)
        
        # Cycle through all dirs ...
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
        
        # Files are listed after ...
        while len(files) > 0:
            path = files.pop(0)
            pre = me.style.NODE_CONT_NES if len(files) > 0 else me.style.NODE_CONT_NE
            name = fs.get_file_name(path)
            me.tree.append(indent + pre + me.style.FILE_PREFIX + name + me.style.FILE_SUFFIX)
        
    def __recursive_data_descent(self, data, indent=''):
        me = self

        # Initialize variables.
        rex = Rex()
        dirs = []
        files = []

        # If indent is nothing, we are at the top level.  
        if indent == '': me.tree.append(me.style.ROOT_PREFIX + me.name  + me.style.ROOT_SUFFIX)
        d = []
        f = []
        for key in data:
            if data[key] is not None and type(data[key]) == dict:
                d.append(key)
            else:
                f.append(key)

        groups = [(dirs, d), (files, f)]
        # List `lst` is originally empty, referring to `dirs` and `files` respectively on 
        # first and second passes.  List `paths` will be the subfolders and files found in the
        # current directory.
        for lst,paths in groups:
            for path in paths:
                # Get the base name from the path of either the subfolder or file.
                name = path
                # If `ign_case` is True, then convert `name` to lower case.
                if me.ign_case: name = name.lower()
                # If `hide` parameter list has elements, process them ...
                if len(me.hide) > 0:
                    # Hide elements are regular expressions if `regexp` is True ...
                    if me.regexp:
                        omit = False
                        for hide in me.hide:
                            if me.ign_case: hide = hide.lower()
                            if rex.m(name, hide): omit = True
                        # If subfolder or file is not omitted, push onto `lst`.
                        if not omit: lst.append(path)
                    # ... otherwise hide elements are literals.  
                    else:
                        omit = False
                        for hide in me.hide:
                            if me.ign_case: hide = hide.lower()
                            if hide not in name: omit = True
                        # If subfolder or file is not omitted, push onto `lst`.
                        if not omit: lst.append(path)
                # ... automatically push onto `lst`.
                else:
                    lst.append(path)
        
        # Cycle through all dirs ...
        while len(dirs) > 0:
            path = dirs.pop(0)
            name = path
            last = True if len(dirs) == 0 and len(files) == 0 else False
            pre = me.style.NODE_CONT_NE if last else me.style.NODE_CONT_NES
            this_indent = indent + pre
            me.tree.append(this_indent + me.style.FOLDER_PREFIX + name + me.style.FOLDER_SUFFIX)
            if last: this_indent = indent + me.style.NODE_BLANK
            else: this_indent = indent + me.style.NODE_SPAN_NS
            me.__recursive_data_descent(data[name], indent=this_indent)
        
        # Files are listed after ...
        while len(files) > 0:
            path = files.pop(0)
            pre = me.style.NODE_CONT_NES if len(files) > 0 else me.style.NODE_CONT_NE
            name = fs.get_file_name(path)
            me.tree.append(indent + pre + me.style.FILE_PREFIX + name + me.style.FILE_SUFFIX)
        
    def to_str(self):
        me = self
        return('\n'.join(me.tree))

    def __str__(self):
        me = self
        return('\n'.join(me.tree))

    def __repr__(self): 
        me = self
        return('\n'.join(me.tree))
