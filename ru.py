import random

def stype(obj):
    '''
        Get the type of an object as a string.
        # Arguments
        - obj: Object to inspect.
    '''
    return(type(obj).__name__)
string_type = stype

def rint(min, max):
    '''
        Return a random int between min and max integers (inclusive).
        # Arguments
        - min: Min int
        - max: Max int inclusive (i.e. max is a possible return value)
    '''
    return(random.randint(min, max))
rand_int = rint

def ritem(lst):
    '''
        Return a random value from the list.
        # Arguments
        - lst: List of items
    '''
    return(lst[rint(0, len(lst)-1)])
rand_item = ritem

def crange(c1, c2):
    '''
        Return a list of characters in the range c1 to c2.
        # Arguments
        - c1: Start character
        - c2: End character
        # Returns
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
        # Arguments
        - s: String
        # Returns
        The resultant string.
    '''
    from regx import Regx
    regx = Regx()
    s = regx.s(s, r'^\s*(.*?)\s*$', r'\1', '=')
    return(s)

def squote(s):
    r"""
    ## Description
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

    ## Returns
    Single quoted string.
    """
    from regx import Regx
    regx = Regx()
    s = regx.s(s, r"'", r"\\'", 'g=')
    s = "'{}'".format(s)
    return s 

def dquote(s):
    r"""
    ## Description
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

    ## Returns
    Double quoted string.
    """
    from regx import Regx
    regx = Regx()
    s = regx.s(s, r'"', r'\\"', 'g=')
    s = '"{}"'.format(s)
    return s 

def quote(s):
    r"""
    ## Description
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
    - `s` : string value

    ## Returns
    Quoted string.
    """
    from regx import Regx
    regx = Regx()
    if not regx.m(s, r"'"): return squote(s)
    if not regx.m(s, r'"'): return dquote(s)
    return squote(s) 

def join_with_commas(items, last_join='and', quote_items=False):
    r"""
    ## Description
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
    Command (plus "and") joined items string.
    """
    mod = quote if quote_items else str
    copy_items = [mod(item) for item in items]
    l = len(copy_items)
    if l == 0: return ''
    if l == 1: return str(copy_items[0])
    if l == 2: return f' {last_join} '.join(copy_items)
    return ', '.join(copy_items[:-1]) + f' {last_join} ' + str(copy_items[-1])

join = join_with_commas

def c2m(val):
    def r3(m): return "{}_{}{}".format(m[0], m[1], m[2])
    def r2(m): return "{}_{}".format(m[0], m[1])
    from regx import Regx
    regx = Regx()
    val = regx.s(val, r'([A-Z]{1,})([A-Z]{1})([a-z0-9])', r3, 'g=')
    val = regx.s(val, r'([a-z0-9])([A-Z])', r2, 'g=')
    val = val.lower()
    return(val)

class_to_module_namer = c2m

def die(msg, size=95):
    '''
        Printy printing of error messages.
        # Arguments
        - msg: Error message
    '''
    import textwrap
    lines = textwrap.wrap(msg, size-2)
    print()
    print("#" * size)
    print("# " + r" ___  ".ljust(size-4) + " #")               
    print("# " + r"| __|_ _ _ _ ___ _ _ ".ljust(size-4) + " #")
    print("# " + r"| _|| '_| '_/ _ \ '_|".ljust(size-4) + " #")
    print("# " + r"|___|_| |_| \___/_|  ".ljust(size-4) + " #")
    print("# " + "".ljust(size-4) + " #")
    print("# " + ("-" * (size-4)) + " #")
    print("# " + "".ljust(size-4) + " #")
    for line in lines:
        print("# " + line.ljust(size-4) + " #")
    print("# " + "".ljust(size-4) + " #")
    print("#" * size)
    print()
    raise Exception(msg)