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
    from rex import Rex
    rex = Rex()
    s = rex.s(s, r'^\s*(.*?)\s*$', r'\1', '=')
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
    from rex import Rex
    rex = Rex()
    s = rex.s(s, r"'", r"\\'", 'g=')
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
    from rex import Rex
    rex = Rex()
    s = rex.s(s, r'"', r'\\"', 'g=')
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
    from rex import Rex
    rex = Rex()
    if not rex.m(s, r"'"): return squote(s)
    if not rex.m(s, r'"'): return dquote(s)
    return squote(s) 

def join_with_commas(items):
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
    Comma (plus "and") joined items string.
    """
    l = len(items)
    if l == 0: return ''
    if l == 1: return str(items[0])
    if l == 2: return ' and '.join(items)
    return ', '.join(items[:-1]) + ' and ' + str(items[-1])

def join_items(items, join_with=", ", last_join=None, quote_items=False):
    r"""
    ## Description
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
    - `quote` : quote items? 
        1. `False` : no quoting
        2. `True` : quote using double quotes e.g. item -> "item"
        3. string value : quote using the string value e.g. item (with quote="'") -> 'item'

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
    ## Description
    Reverses the characters in a string.

    ## Usage
    ```python

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
    most cases well.  When in doubt you can 

    ## Usage
    ```python
    print(ru.pluralize('individual', 1))
    >>> 'individual'

    print(ru.pluralize('individual', 2))
    >>> 'individuals'

    print(ru.pluralize('family', 1, plural='families'))
    >>> 'individual'

    print(ru.pluralize(2, 'individual'))
    >>> 'individuals'
    ```

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

def create_banner(title, subtitle=None, size=98, border='', font="standard", center=False):
    r"""
    Create a text banner (using Figlet).  

    ## Arguments

    - `title` : title to be printed in Figlet font
    - `subtitle` : optional subtitle text; if multi-line, can be a list of lines or a string with carriage returns
    - `size` : total size of banner in characters (default 100)
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

def clone(data):
    import json
    return json.loads(json.dumps(data))

def die(msg):
    '''
        Pretty printing of error messages.
        # Arguments
        - msg: Error message
    '''
    print("\n")
    print(create_banner('ERROR', border='', size=80, font='isometric1'))
    raise Exception(msg)