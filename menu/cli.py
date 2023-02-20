from rex import Rex
import fs

VERBOSITY = 1
class DEBUG:
    enable = False
    inputs = []
    
"""
Create interactive command line interface menus.

# Usage

```python
from menu.simple import get_input, select_one, select_mult

print()
vals = select_mult('Choose from the list:', ['one', 'two', 'three', 'four', 'five'], ['two', 'four'])
print(vals)

print()
val = get_input('Please enter a number.', 2)
print(val)

print()
val = select_one('Choose from the list:', ['one', 'two', 'three', 'four'], 'two')
print(val)
```

"""

def get_input(message, default=None):
    """
    Get user defined input.
    
    # Arguments
    - message : message to print
    - default : optional default value
    
    # Returns
    User specified value.
    """
    rex = Rex()
    message = rex.s(message, r'\s*$', r'', '=')
    print(message + "\n")
    if default is not None: print("Default is \"{}\".\n".format(default))
    value = input("INPUT: ")
    print()
    value = rex.s(value, r'^\s*(.*?)\s*$', r'\1', '=')
    if default is not None and len(value) == 0: return(default)
    return(value)

def file(message, default=None):
    """
    Get user file input.
    
    # Arguments
    - message : message to print
    - default : optional default value
    
    # Returns
    User specified value.
    """
    rex = Rex()
    message = rex.s(message, r'\s*$', r'', '=')
    print(message + "\n")
    print("HINT: You can drag and drop the file from Windows Explorer.\n")
    if default is not None: print("Default is \"{}\".\n".format(default))
    value = input("INPUT: ")
    print()
    value = rex.s(value, r'^\s*(.*?)\s*$', r'\1', '=')
    if default is not None and len(value) == 0: return(default)
    return(value)




        

def select_one(message, options, default=None):
    """
    Select an option from a list.
    
    # Arguments
    - message : message to print
    - options : list of options
    - default : optional default value
    
    # Returns
    User selected value.
    """
    rex = Rex()
    message = rex.s(message, r'\s*$', r'', '=')
    print(message + "\n")
    i_max = len(options)
    for i in range(0, i_max):
        n = i + 1
        print("{:4d}. {}".format(n, options[i]))
    print()
    if default is not None: print("Default is \"{}\".\n".format(default))
    value = None
    selected = None
    use_default = False
    while True:
        value = input('SELECTION: ')
        print()
        value = rex.s(value, r'^\s*(.*?)\s*$', r'\1', '=')
        if default is not None and len(value) == 0:
            use_default = True
            break
        if not rex.m(value, r'^\d+$'):
            print("ERROR: Value \"{}\" is not a number.\n".format(value))
            continue
        value = int(value)
        if value < 1 or value > i_max:
            print("ERROR: Value \"{}\" is not in the specified range.\n".format(value))
            continue
        break
    if use_default: selected = default
    else: selected = options[value - 1]
    return(selected)

def select_mult(message, options, default=[]):
    """
    Select an option from a list.
    
    # Arguments
    - message : message to print
    - options : list of options
    - default : optional default list, set, or dict (basically any object that supports *in*)
    
    # Returns
    The list of selected values.
    """
    rex = Rex()
    if default is None: default = []
    checked = {item: True for item in default}
    selected = {}
    i_max = len(options)
    for i in range(0, i_max):
        item = options[i]
        if item in checked: selected[i] = True
    message = rex.s(message, r'\s*$', r'', '=')
    def replace_range(m):
        nums = []
        for r in range(int(m[1]), int(m[3])+1): nums.append(str(r))
        return(', '.join(nums))
    while True:
        print(message + "\n")
        for i in range(0, i_max):
            n = i + 1
            icon = '[x]' if i in selected else '[ ]'
            print("{:4d}. {} {}".format(n, icon, options[i]))
        print()
        print("Select space delimited options and/or actions: A=All, C=Clear, T=Toggle.\n\nHit <Enter> by itself, or D=Done, to continue.\n")
        if DEBUG.enable:
            values = DEBUG.inputs.pop(0)
            print(values)
        else:
            values = input('SELECTION: ')
        print()
        values = rex.s(values, r'(\d+)\s*(\.\.|to|-)\s*(\d+)', replace_range, 'g=')
        values = rex.s(values, r'^\s*(.*?)\s*$', r'\1', 'g=')
        values = rex.s(values, r',', r' ', 'g=')
        if len(values) == 0: break
        values = rex.split(values, r'\s+')
        done = False
        for value in values:
            if rex.m(value, r'^\d+$'):
                value = int(value)
                if value < 1 or value > i_max:
                    print("ERROR: Value \"{}\" is not in the specified range.\n".format(value))
                    continue
                else:
                    i = value - 1
                    if i in selected:
                        del selected[i]
                    else:
                        selected[i] = True
            else:
                value = str(value).upper()
                if value == 'A':
                    for i in range(0, i_max): 
                        selected[i] = True
                if value == 'C':
                    for i in range(0, i_max): 
                        if i in selected: del(selected[i])
                if value == 'T':
                    for i in range(0, i_max): 
                        if i in selected: del(selected[i])
                        else: selected[i] = True
                if value == 'D':
                    done = True
        if done: break
    all = []
    for i in range(0, i_max):
        if i in selected:
            all.append(options[i])
    return(all)

def files(message, default=None):
    rex = Rex()
    message = rex.s(message, r'\s*$', r'', '=')
    all_files = []
    if default is not None:
        t = type(default)
        if t == str:
            all_files.append(default)
        elif t == list:
            all_files.extend(default)
    print(message + "\n")
    print("INSTRUCTIONS:")
    print("- Enter files and/or folders, one per line, hitting <Enter> after each entry.")
    print("- If you specify a folder, all files in the folder will be selected.  You can, however, use wildcards to constrain file selections (e.g. \"C:\\\\Temp\\*.yml\").")
    print("- Type \"?\" + <Enter> to see the current list of selected files.")
    print("- Hit <Enter> by itself to terminate file/folder input.  This will display a editable menu of all selected files.")
    print()
    print("HINT: Instead of typing or using copy+paste, you can drag and drop files/folders from Windows Explorer.")
    print()
    if default is not None: 
        n = len(all_files)
        print(f'[{n} file{"" if n == 1 else "s"} initially selected]')
    print("INPUT:")
    enable = True
    while enable:
        if DEBUG.enable:
            value = DEBUG.inputs.pop(0)
            print(value)
        else:
            value = input().strip()
        new_files = []
        if value == "":
            break
        elif value == '?':
            print('')
            for i, path in enumerate(all_files):
                print(f"{i+1:4d}. {path}")
            print('')
        elif '*' in value or '?' in value or '[' in value:
            import glob
            new_files = [fs.fix(fs.abs(f)) for f in glob.glob(value)]
        elif fs.isdir(value):
            new_files = [fs.fix(fs.abs(f)) for f in fs.files(value)]
        else:
            new_files.append(fs.fix(fs.abs(value)))
        add_files = []
        for f in new_files:
            if f not in all_files:
                all_files.append(f)
                add_files.append(f)
        n = len(all_files)
        m = len(add_files)
        print(f'[{n} file{"" if n == 1 else "s"} selected, +{m}]')

    return select_mult('Select files.', all_files, all_files)

        
