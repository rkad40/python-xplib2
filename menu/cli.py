from rex import Rex

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
    The set of selected values.
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
        for r in range(int(m[0]), int(m[2])+1): nums.append(str(r))
        return(', '.join(nums))
    while True:
        print(message + "\n")
        for i in range(0, i_max):
            n = i + 1
            icon = '[x]' if i in selected else '[ ]'
            print("{:4d}. {} {}".format(n, icon, options[i]))
        print()
        print("Select space delimited options and/or actions: A=All, C=Clear, T=Toggle.\n\nHit <Enter> by itself, or D=Done, to continue.\n")
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
    hash = []
    for i in range(0, i_max):
        if i in selected:
            hash.append(options[i])
    return(hash)


