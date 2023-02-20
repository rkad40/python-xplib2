r"""
Display a document tree.  

## Usage

```python
tree = Tree(r'C:\Work\Top', skip=[r'^\.', r'\.bak$'], regx=True) 
print(str(tree))
```

Or on the command line:

```
python .\tree.py --path . --skip "^__" "\.pyc$"
```
"""

import fs
from rex import Rex

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

    def __init__(self, data=None, skip=None, regx=True, ign_case=False, style=None):
        r'''
        Display a document tree.  

        ## Usage

        ```python
        tree = Tree(r'C:\Work\Top', skip=[r'^\.', r'\.bak$'], regx=True) 
        print(str(tree))
        ```

        ## Arguments
        - `data`: String directory path from which the document tree begins or a dictionary object.
        - `skip`: Single str file name or iterable object of file names to skip (default=None).
        - `regx`: If True, `skip` items are treated as regular expressions (default=True).
        - `ign_case`: If True, `skip` ignores case.
        - `style`: `StyleBasicUnicode` or `StyleBasicASCII` (default=`StyleBasicUnicode`).
        '''
        me = self 
        me.style = style if style is not None else StyleBasicUnicode
        me.reset(skip=skip, regx=regx, ign_case=ign_case, style=style)
        if data is not None:
            t = type(data)
            if t == dict:
                self.from_dict(data, skip, regx, ign_case, style)
            elif t == str:
                self.from_path(data, skip, regx, ign_case, style)

    def reset(self, skip=None, regx=True, ign_case=False, style=None):
        me = self
        me.skip = skip
        me.regx = regx
        me.ign_case = ign_case
        me.style = style if style is not None else StyleBasicUnicode
        me.tree = []
        if me.skip is None: me.skip = []
        if type(me.skip) is str: me.skip = [me.skip]

    def from_path(self, dir, skip=None, regx=True, ign_case=False, style=None):
        me = self
        me.reset(skip=skip, regx=regx, ign_case=ign_case, style=me.style)
        me.__recursive_path_descent(dir)

    def from_dict(self, data, name='Top', skip=None, regx=True, ign_case=False, style=None):
        me = self
        me.name = name
        me.reset(skip=skip, regx=regx, ign_case=ign_case, style=me.style)
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
                # If `skip` parameter list has elements, process them ...
                if len(me.skip) > 0:
                    # Skip elements are regular expressions if `regx` is True ...
                    if me.regx:
                        omit = False
                        for skip in me.skip:
                            if me.ign_case: skip = skip.lower()
                            if rex.m(name, skip): omit = True
                        # If subfolder or file is not omitted, push onto `lst`.
                        if not omit: lst.append(path)
                    # ... otherwise skip elements are literals.  
                    else:
                        omit = False
                        for skip in me.skip:
                            if me.ign_case: skip = skip.lower()
                            if skip not in name: omit = True
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
                # If `skip` parameter list has elements, process them ...
                if len(me.skip) > 0:
                    # Skip elements are regular expressions if `regx` is True ...
                    if me.regx:
                        omit = False
                        for skip in me.skip:
                            if me.ign_case: skip = skip.lower()
                            if rex.m(name, skip): omit = True
                        # If subfolder or file is not omitted, push onto `lst`.
                        if not omit: lst.append(path)
                    # ... otherwise skip elements are literals.  
                    else:
                        omit = False
                        for skip in me.skip:
                            if me.ign_case: skip = skip.lower()
                            if skip not in name: omit = True
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

if __name__ == '__main__':
    import argparse
    import pyperclip
    import ru

    print(ru.create_banner('Directory Tree', border="#", center=True))

    parser = argparse.ArgumentParser(description='Copy Tree to Clipboard')
    parser.add_argument('--skip', '-s', dest='skip', default=[], nargs="*", type=str, help='Single str file name or iterable object of file names to skip (default=None).')
    parser.add_argument('--no-regx', '-R', dest='no_regx', action='store_true', default=False, help='Treat skip items as literals instead of regular expressions (default=False)')
    parser.add_argument('--ign-case', '--icase', '--ign', '-i', dest='ign_case', action='store_true', default=False, help='Ignore case for skip items (default=True)')
    parser.add_argument('--path', dest='path', help='Directory path.')
    args = parser.parse_args()

    tree = str(Tree(args.path, skip=args.skip, regx=not(args.no_regx), ign_case=args.ign_case))
    print(tree)
    print('')
    pyperclip.copy(tree)

    print('NOTE: Tree copied to clipboard.')


