r"""
Python "random utilities" library.

## Usage

```python
import ru
```
"""

import random
import sys
import os

class CaptureStdout:
    r'''
    Send STDOUT to a list.

    ## Usage

    ```python
    with ru.CaptureStdout() as stream:
        print('This is a test.')
        print('This is only a test.')
    print(stream.data)
    ```

    This prints `['This is a test.', 'This is only a test.']`.
    '''
    def __init__(self):
        self.data = []
    def write(self, s):
        self.data.append(s)
    def __enter__(self):
        sys.stdout = self
        return self
    def __exit__(self, ext_type, exc_value, traceback):
        sys.stdout = sys.__stdout__  

class CaptureStderr:
    r'''
    Send STDERR to a list.
    '''
    def __init__(self):
        self.data = []
    def write(self, s):
        self.data.append(s)
    def __enter__(self):
        sys.stderr = self
        return self
    def __exit__(self, ext_type, exc_value, traceback):
        sys.stderr = sys.__stderr__  

def load(name, path=None):
    r'''
    Load a module.

    ## Arguments
    - `name`: Module name (e.g. "foo.bar").
    - `path`: Module path (e.g. "C:/Python/foo/bar.py").

    Argument `path` is optional.  If name is a valid module accessible from `sys.path`, no `path` is 
    needed.  If you want to load the module via file path, set `path` to the file path + name 
    (e.g. "C:/Python/foo/bar.py") and name to any arbitrary Python module-like name (e.g. "foo.bar", 
    "foobar", "this.is.foobar", etc., etc.).

    Say you want to import the `Foobar()` class from `C:/Python/foo/bar.py`.  You could do something
    like this:

    ```python
    foobar = ru.load('foo.bar', 'C:/Python/foo/bar.py')
    app = foobar.Foobar()
    ```

    But this also works:

    ```python
    ru.load('foo.bar', 'C:/Python/foo/bar.py')
    from foo.bar import Foobar
    app = Foobar()
    ```

    ## Aliases
    - `load()`
    - `load_module()`
    - `import_module()`
    '''
    if path is None:
        import importlib
        mod = importlib.import_module(name)
    else:
        import importlib.util
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
    return mod    
load_module = load
import_module = load

def stype(obj):
    '''
    Get the type of an object as a string.

    ## Arguments
    - obj: Object to inspect.

    ## Returns
    Object type as string.
    '''
    return(type(obj).__name__)
string_type = stype

def rint(min, max):
    '''
    Return a random int between min and max integers (inclusive).

    ## Arguments
    - min: Min int
    - max: Max int inclusive (i.e. max is a possible return value)

    ## Returns
    Random integer.
    '''
    return(random.randint(min, max))
rand_int = rint

def ritem(lst):
    '''
    Return a random value from the list.

    ## Arguments
    - lst: List of items

    ## Returns
    Random item from list.
    '''
    return(lst[rint(0, len(lst)-1)])
rand_item = ritem

def crange(c1, c2):
    '''
    Return a list of characters in the range c1 to c2.

    ## Arguments
    - c1: Start character
    - c2: End character

    ## Returns
    List of characters.
    '''
    lst = []
    for c in range(ord(c1), ord(c2)+1):
        lst.append(chr(c))
    return lst
char_range = crange

def trim(s):
    '''
    Remove leading and trailing white spaces from string s.

    ## Arguments
    - s: String

    ## Returns
    Resultant string.
    '''
    from rex import Rex
    rex = Rex()
    s = rex.s(s, r'^\s*(.*?)\s*$', r'\1', '=')
    return(s)

def squote(s, type_check=False, enable=True):
    r"""
    Single quote a string for the purpose of embedding in a quote.

    ## Usage
    
    Suppose you have a string that reads: `The captain said, "All hope's lost!".` assigned to a
    variable `s`:
    
    ```python
    print(ru.squote(s))
    >>> 'The captain said, "All hope\'s lost!"'
    ```

    ## Arguments
    - `s` : string value
    - `type_check`: if True, make sure value is type `str`; if it is not of type `str` do not quote
    - `enable`: if True quote string, else don't

    ## Returns
    Single quoted string.
    """
    if not enable: return s
    if type_check and type(s) != str: return s
    from rex import Rex
    rex = Rex()
    s = rex.s(s, r"'", r"\\'", 'g=')
    s = "'{}'".format(s)
    return s 

def dquote(s, type_check=False, enable=True):
    r"""
    Double quote a string for the purpose of embedding in a quote.

    ## Usage
    Suppose you have a string that reads: `The captain said, "All hope's lost!".` assigned to a
    variable `s`:
    
    ```python
    print(ru.dquote(s))
    >>> "The captain said, \"All hope's lost!\""
    ```

    ## Arguments
    - `s` : string value
    - `type_check`: if True, make sure value is type `str`; if it is not of type `str` do not quote
    - `enable`: if True quote string, else don't

    ## Returns
    Double quoted string.
    """
    if not enable: return s
    if type_check and type(s) != str: return s
    from rex import Rex
    rex = Rex()
    s = rex.s(s, r'"', r'\\"', 'g=')
    s = '"{}"'.format(s)
    return s 

def quote(s, type_check=False, enable=True):
    r"""
    Quote a string for the purpose of embedding in a quote using either single or double quotes, 
    whichever form is not already present in string.  If both are present, defaults to single 
    quotes.

    ## Usage
    Suppose you have a string that reads: `The captain said, "All hope's lost!".` assigned to a
    variable `s`:
    
    ```python
    print(ru.quote(s))
    >>> 'The captain said, "All hope\'s lost!"'
    ```

    ## Arguments
    - `s`: string value
    - `type_check`: if True, make sure value is type `str`; if it is not of type `str` do not quote
    - `enable`: if True quote string, else don't

    ## Returns
    Quoted string.
    """
    if not enable: return s
    if type_check and type(s) != str: return s
    from rex import Rex
    rex = Rex()
    s = str(s)
    if not rex.m(s, r"'"): return squote(s)
    if not rex.m(s, r'"'): return dquote(s)
    return squote(s) 

def join_with_commas(items):
    r"""
    Join list items with a comma.  Last item is joined with "and".

    ## Usage
    
    ```python
    items = ["apples", "oranges", "bananas"]
    print(ru.join_with_commas(items))
    >>> 'apples, oranges and bananas'
    ```

    ## Arguments
    - `items` : list of items to be joined

    ## Returns
    Comma (plus "and") joined items string.
    """
    l = len(items)
    if l == 0: return ''
    if l == 1: return str(items[0])
    if l == 2: return ' and '.join(items)
    return ', '.join(items[:-1]) + ' and ' + str(items[-1])

def join_items(items, join_with=", ", last_join=None, quote_items=False):
    r"""
    Join list items.

    ## Usage
    
    ```python
    items = ["apples", "oranges", "bananas"]
    print(ru.join_all(items))
    >>> 'apples, oranges, bananas'
    print(ru.join_all(items, last_join=' or ', quote=True))
    >>> '"apples", "oranges" or "bananas"'
    ```

    ## Arguments
    - `items` : list of items to be joined
    - `join_with` : join items with (default is ", ")
    - `last_join` : use instead of `join_with` for last join e.g. " and " or " or " (default is None, meaning use `join_with`)
    - `quote` : quote items? Valid values are `False`: no quoting, `True`: quote using double quotes e.g. item -> "item", string value: quote using the string value e.g. item (with quote="'") -> 'item'; (default = False.)

    ## Returns
    Modified string.
    """
    quote_str = quote_items
    if quote_items is None:
        quote_str = ''
    elif type(quote_items) == bool:
        if quote_items: quote_str = '"'
        else: quote_str = ''
    last_join_str = last_join
    if last_join is None:
        last_join_str = join_with
    l = len(items)
    items_str = [quote_str + str(item) + quote_str for item in items]
    if l == 0: return ''
    if l == 1: return f'{items_str[0]}'
    if l == 2: return f'{last_join_str}'.join(items_str)
    return f'{join_with}'.join(items_str[:-1]) + f'{last_join_str}{items_str[-1]}'

def reverse_string(val):
    r"""
    Reverses the characters in a string.

    ## Usage
    
    ```python
    s = 'abc'
    print(reverse_string(s))
    
    >>> 'cba'
    ```

    ## Arguments
    - `val` : string value

    ## Returns
    The reversed string.
    """
    return str(val)[::-1]

def similar_words(word, possible_words):
    r"""
    Find similar words to a given word.

    ## Arguments
    - `word`: base word
    - `possible_words`: list of words to check against

    ## Returns
    A list of similar words, often just one, but there may be more.
    """
    def _word_to_vector(word):
        from collections import Counter
        from math import sqrt
        cw = Counter(word)
        sw = set(cw)
        lw = sqrt(sum(c*c for c in cw.values()))
        return cw, sw, lw
    def _cosine_distance(vec1, vec2):
        common = vec1[1].intersection(vec2[1])
        return sum(vec1[0][ch]*vec2[0][ch] for ch in common)/vec1[2]/vec2[2]
    word1 = word
    d2w = {}
    distances = []
    for word2 in possible_words:
        vec1 = _word_to_vector(word1.lower())
        vec2 = _word_to_vector(word2.lower())
        distance = _cosine_distance(vec1, vec2)
        if distance not in d2w: d2w[distance] = []
        d2w[distance].append(word2)
        distances.append(distance)
    distances.sort()
    # for distance in distances:
    #     print(f'{",".join(d2w[distance]):50} : {distance:0.4f}')
    similar_words = d2w[distances[-1]]
    return similar_words

PLURAL_EXCEPTIONS = {
    'roof': ['', 's'],
    'belief': ['', 's'],
    'chef': ['', 's'],
    'chief': ['', 's'],
    'photo': ['', 's'],
    'piano': ['', 's'],
    'halo': ['', 's'],
    'series': ['', ''],
    'species': ['', ''],
    'homework': ['', ''],
    'marketing': ['', ''],
    'livestock': ['', ''],
    'education': ['', ''],
    'courage': ['', ''],
    'bravery': ['', ''],
    'luck': ['', ''],
    'cowardice': ['', ''],
    'greed': ['', ''],
    'clarity': ['', ''],
    'honesty': ['', ''],
    'evidence': ['', ''],
    'insurance': ['', ''],
    'butter': ['', ''],
    'love': ['', ''],
    'news': ['', ''],
    'curiosity': ['', ''],
    'satisfaction': ['', ''],
    'work': ['', ''],
    'mud': ['', ''],
    'weather': ['', ''],
    'racism': ['', ''],
    'sexism': ['', ''],
    'patriotism': ['', ''],
    'chaos': ['', ''],
    'scenery': ['', ''],
    'help': ['', ''],
    'advice': ['', ''],
    'water': ['', ''],
    'fun': ['', ''],
    'wisdom': ['', ''],
    'silence': ['', ''],
    'sugar': ['', ''],
    'coal': ['', ''],
    'spelling': ['', ''],
    'money': ['', ''], 
    'deer': ['', ''],
    'sheep': ['', ''],
    'goose': ['oose', 'eese'],
    'man': ['an', 'en'],
    'tooth': ['ooth', 'eeth'],
    'foot': ['oot', 'eet'],
    'mouse': ['ouse', 'ice'],
    'person': ['rson', 'ople'],
    'fez': ['', 'zes'],
    'gas': ['', 'ses'],
    'cactus': ['us', 'i'],
    'focus': ['us', 'i'],
    'furniture': [None, 'furniture'],
    'information': [None, 'information'],
    'knowledge': [None, 'knowledge'],
    'jewelry': [None, 'jewelry'],
    'homework': [None, 'homework'],
    'marketing': [None, 'marketing'],
    'livestock': [None, 'livestock'],
    'education': [None, 'education'],
    'courage': [None, 'courage'],
    'bravery': [None, 'bravery'],
    'luck': [None, 'luck'],
    'cowardice': [None, 'cowardice'],
    'greed': [None, 'greed'],
    'clarity': [None, 'clarity'],
    'honesty': [None, 'honesty'],
    'evidence': [None, 'evidence'],
    'insurance': [None, 'insurance'],
    'butter': [None, 'butter'],
    'love': [None, 'love'],
    'news': [None, 'news'],
    'curiosity': [None, 'curiosity'],
    'satisfaction': [None, 'satisfaction'],
    'work': [None, 'work'],
    'mud': [None, 'mud'],
    'weather': [None, 'weather'],
    'racism': [None, 'racism'],
    'sexism': [None, 'sexism'],
    'patriotism': [None, 'patriotism'],
    'chaos': [None, 'chaos'],
    'scenery': [None, 'scenery'],
    'help': [None, 'help'],
    'advice': [None, 'advice'],
    'water': [None, 'water'],
    'fun': [None, 'fun'],
    'wisdom': [None, 'wisdom'],
    'silence': [None, 'silence'],
    'sugar': [None, 'sugar'],
    'coal': [None, 'coal'],
    'spelling': [None, 'spelling'],
    'money': [None, 'money'],
}

def pluralize(word, cnt=2, plural=None):
    r"""
    ## Description
    Pluralize word if necessary.  The function makes its best guess at the plural form and handles
    most cases well. 

    ## Usage
    
    ```python
    print(ru.pluralize('individual', 1))
    >>> 'individual'

    print(ru.pluralize('individual', 2))
    >>> 'individuals'
    ```

    You can also explicitly define a plural form to use:

    ```python
    print(ru.pluralize('family', 1, plural='families'))
    >>> 'family'

    print(ru.pluralize('family', 2, plural='families'))
    >>> 'families'
    ```

    This is valid, but at least in this case, `pluralize()` does the right thing.  This is the case 
    for most strings.

    ## Arguments
    - `word` : singular form of the word
    - `cnt` : how many instances (default = 2 i.e. return the plural form)
    - `plural` : optionally specify the plural form

    ## Returns
    The pluralized form of `word` if `cnt` is not 1.
    """
    if cnt == 1: return word
    if plural is not None: return plural
    val = word.lower()
    from rex import Rex
    rex = Rex()
    if val == 'focus':
        i = 0
        pass
    if val in PLURAL_EXCEPTIONS:
        if PLURAL_EXCEPTIONS[val][0] is None: return PLURAL_EXCEPTIONS[val][1]
        size = len(PLURAL_EXCEPTIONS[val][0])
        if size == 0: return word + PLURAL_EXCEPTIONS[val][1]
        return word[:-1*size] + PLURAL_EXCEPTIONS[val][1]
    # if rex.m(val, 'us$'): return word[:-2] + 'es'
    if rex.m(val, '(is)$'): return word[:-2] + 'es'
    if rex.m(val, '(us)$'): return word + 'es'
    if rex.m(val, '(s|ss|sh|ch|x|z)$'): return word + 'es'
    if rex.m(val, '(f|fe)$'): return word[:-1*len(rex.d(1))] + 'ves'
    if rex.m(val, '[aeiou]y$'): return word + 's'
    if rex.m(val, 'y$'): return word[:-1] + 'ies'
    if rex.m(val, 'o$'): return word + 'es'
    if rex.m(val, 'on$'): return word[:-2] + 'a'
    return word + 's'

def create_banner(title, subtitle=None, size=None, border='', font="standard", center=False):
    r"""
    Create a text banner (using Figlet).  

    ## Arguments

    - `title` : title to be printed in Figlet font
    - `subtitle` : optional subtitle text; if multi-line, can be a list of lines or a string with carriage returns
    - `size` : total size of banner in characters (default is the window width)
    - `border` : optional border character(s) e.g. "#' (default is '' i.e. no border)
    - `font` : Figlet font to use for title (default "standard", for more see http://www.figlet.org/examples.html)
    - `center` : center banner if True, left justify if False

    ## Returns

    Banner text, ready to print.
    """
    import pyfiglet
    banner = pyfiglet.figlet_format(title, font=font)
    if border is None: border = ''
    lines = banner.split('\n')
    try:
        if size is None or size == 0:
            size = os.get_terminal_size().columns - 1
    except:
        size = 98
    if center:
        for i in range(0, len(lines)):
            lines[i] = border + lines[i].center(size-2*len(border)) + border
    else:
        if len(border) > 0:
            for i in range(0, len(lines)):
                lines[i] = border + ' ' + lines[i].ljust(size-2*len(border)-2) + ' ' + border
        else:
            for i in range(0, len(lines)):
                lines[i] = lines[i].ljust(size)
    banner = "\n".join(lines) + "\n"
    if subtitle is not None:
        if type(subtitle) == list:
            subtitle = '\n'.join(subtitle)
        subtitle = subtitle.split('\n')
        if len(border) > 0:
            subtitle.append('')
        if center:
            for line in subtitle:
                banner += border + line.center(size-2*len(border)) + border + '\n'
        else:
            if len(border) > 0:
                for line in subtitle:
                    banner += border + ' ' + line.center(size-2*len(border)) + border + '\n'
            else:
                for line in subtitle:
                    banner += line.ljust(size) + '\n'
    if len(border) > 0:
        banner = f'{border*size}\n{banner}{border*size}\n'
    return banner

def sort_alpha_num(items):
    r"""
    Sort values alphanumerically.  This is useful if you have strings that contain numbers as text.

    ## Usage
    ```python
    l = ['b4', 'a100', 'a20', 'a3']

    print(sorted(l))
    >>> ['a100', 'a20', 'a3', 'b4']
    
    print(ru.sort_alpha_num(l))
    >>> ['a3', 'a20', 'a100', 'b4']
    ```

    ## Arguments
    - `items`: list of items to sort

    ## Returns
    Sorted list of items.
    """
    data = {}
    keys = []
    sorted_items = []
    from rex import Rex
    rex = Rex()
    def update_nums(m):
        num = int(m[1])
        num = num + 1000000000000000000
        return str(num)
    for item in items:
        key = rex.s(item, '(\d+)', update_nums, 'g=')
        data[key] = item
        keys.append(key)
    keys.sort()
    for key in keys:
        sorted_items.append(data[key])
    return sorted_items

def clone(data, method='deepcopy'):
    r"""
    Clone data.

    ## Arguments
    - `data`: data to be cloned
    - `method`: one of 'deepcopy' (default), 'pickle', or 'json'

    ## Returns
    Data value as a string.
    """
    if method == 'deepcopy':
        import copy
        return copy.deepcopy(data)
    elif method == 'pickle':
        import pickle
        return pickle.loads(pickle.dumps(data))
    elif method == 'json':
        import json
        return json.loads(json.dumps(data))

def die(msg):
    '''
    Pretty printing of error messages.  Raises an exception.

    ## Arguments
    - msg: Error message

    ## Returns 
    Nothing.  Function raises an exception.  
    '''
    print("\n")
    print(create_banner('ERROR', border='', size=80, font='isometric1'))
    raise Exception(msg)


def print_error():
    '''
    Print error traceback.
    '''
    import traceback
    traceback.print_exc()
    print()
print_errors = print_error
error = print_error

def pprint(obj):
    '''
    Pretty print an object.
    '''
    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(obj)
