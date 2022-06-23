'''
An intuitive regular expression class wrapper for Python's often confusing `re`
regular expression module.

## Usage

```python
from rex import Rex
rex = Rex()
...
# Reformat lines of phone numbers.  
val = rex.s(val, r'^\s*(\d{3})(\d{3})(\d{4})\s*$', r'\1-\2-\3', '=gm')
```

'''

import re

VERSION = '1.001'

class Rex():
    r"""
    An intuitive regular expression class wrapper for Python's often confusing `re`
    regular expression module.

    ## Usage

    ```python
    from rex import Rex
    rex = Rex()
    ...
    # Reformat lines of phone numbers.  
    val = rex.s(val, r'^\s*(\d{3})(\d{3})(\d{4})\s*$', r'\1-\2-\3', '=gm')
    ```
    """
    def __init__(self): 
        self.clear()
    
    def clear(self):
        r'''
            Reset `rex` object.
            
            ## Usage
            
            ```python
            rex.clear()
            ```
            
            ## Arguments
            - `path`: file as str
            - `mode='r'`: 'r' for read, 'w' for write
            
            ## Returns
            file stream (use `close()` to close when done)
        '''
        self.old = ''
        self.new = ''
        self.group = []
        self.result = False
        self.opt = []
        self.matrix = []
        self.i = 0

    def d(self, i, j=None):
        r'''
            Access group `dollar` sign data (equivalently `data`, shortcut `d`).  The designation 
            `rex.dollar(1)` (or `rex.data(1)` or `rex.d(1)`) would be equivalent to $1 as implemented 
            in other scripting languages like Perl.  
            
            If the global `g` option is applied to the `match()` or `sub()` regular expression 
            methods, the group data will consist of one or more *group sets*.  In such cases, 
            `dollar()` and its equivalent forms accept two index values.  The first is the group set, 
            the second is the group e.g. `rex.dollar(2, 1)` would get $1 from the third group set.  
            Passing one index value is still valid even if `g` flag is used.  If only one index is 
            specified with the `g` flag option in use, the first group set is accessed by default.  
            Thus `rex.dollar(0, 1)` is always equivalent to `rex.dollar(1)`.

            There is one exception to this rule.  The group set can be iterated by calling 
            `rex.next()`.  So iterating through group sets is as simple as doing:

            ```python
            while rex.d(0) is not None:
                ...
                regx.next()
            ``` 

            Internally, doing a `regx.m()` or `regx.s()` sets the internal instance attribute 
            `regx.i` to 0 while `regx.next()` increments it.  When only one index is passed to 
            `regx.d()`, `regx.i` is used as the group set index.  It iterate through the data a 
            second time, set `self.i` to 0 first.

            The above works because out-of-range group set index passed or implicitly used by 
            `dollar()` does not raise an exception.  Rather, it returns `None`.  Note, it is 
            possible to match an empty string "".  This is not the same thing as `None`.  

            The `rex.dollar()` method call is a wrapper interface to the `rex.matrix` data hash.  You 
            can access or edit `rex.matrix` directly if the need arises.

            ## Usage
            
            ```python
            rex = Rex()
            statement = 'My favorite color is blue.  My favorite number is 7.'
            if rex.m(statement, r'(favorite\s+(\w+)\s+is\s+(\w+))', 'g'):
                # Cycle through all group sets (note the use of the 'g' option)
                while rex.d(0) is not None:
                    # Print "$2: $3" (but with $2 capitalized)
                    print(f'{rex.d(2).capitalize()}: {rex.d(3)})
                    rex.next()
            ```

            Output:

            ```text
            Color: blue
            Number: 7
            ```

        '''
        try:
            if j is None: return self.matrix[self.i][i]
            return self.matrix[i][j]
        except:
            return None
    data = d
    dollar = d

    def next(self):
        r'''
            Increment `rex.i`.  Can be used to loop through group sets when the `g` option is in 
            force.     
        '''
        self.i += 1

    def sets(self):
        r'''
            Returns the number of group sets.     
        '''
        return len(self.matrix)

    def cnt(self, i=None):
        r'''
            Return the count (or size) of a group set data object.  `rex.cnt()` returns the size of 
            the `rex.matrix[self.i]`.  `rex.cnt(0)` returns the size of `rex.matrix[0]`.  
        '''
        try:
            if i is None: return len(self.matrix[self.i])
            return len(self.matrix[i])
        except:
            return 0

    def m(self, var, pattern, opt=''):
        r'''
            Regular expression match (`m` short form, `match` long form).
            
            ## Usage
            
            ```python
            rex = Rex()
            str = "The rain in Spain ain't stopping nobody."
            if rex.match(str, r'(?:^|\s*)(\w*?ai.*?)(?:\s+|$)', 'g'):
                print(r.group)
            >>> ['rain', 'Spain', "ain't"]
            ```
            
            ## Arguments
            - `var`: Source string variable.
            - `pattern`: Regular expression pattern.
            - `opt`: Optional flags
            `g` = global (find all)
            `i` = case insensitive
            `m` = multi-line 
            `s` = single line (. can match anything, including "\n")
            
            ## Returns
            True if a match was found, False otherwise.  Additional information stored in data object.
            - `rex.result`: True if match was found, False otherwise.
            - `rex.group`: Array of matching groups
            - `rex.groups`: Array of global matching groups
        '''

        # Initialize instance attributes.
        self.opt = ''                 # List of flag options e.g. 'gs' -> ['g', 's'].
        self.flags = 0                # Integer flag mask used by native re search function.
        self.old = var                # Copy of initial string.  
        self.new = None               # Modified string.  Not used in match() method.    
        self.result = False           # Set to True if match found, False otherwise.  
        self.i = 0                    # Iterator index value.
        self.matrix = []              # Match group matrix.
        
        # Parse options and set self.flags.
        self.opt = list(opt.lower())
        for c in self.opt:
            if c == 'i': self.flags |= re.IGNORECASE; continue
            if c == 'm': self.flags |= re.MULTILINE; continue
            if c == 's': self.flags |= re.DOTALL; continue
            if c == 'g': continue
            raise Exception(f'Invalid option "{c}".')
        
        # Enter this branch if the 'g' flag option (global match) is specified.  This can result in 
        # more than one group set.   
        if 'g' in self.opt:
            self.matrix = []
            self.result = False
            index = 0
            for match in re.finditer(pattern, var, flags=self.flags):
                dollar = []
                for i in range(0, match.re.groups+1):
                    dollar.append(match.group(i))
                self.matrix.append(dollar)
                self.result = True
                index += 1

        # Enter this branch if 'g' flag option (global match) is not set.  This means there will be
        # at most one group set.
        else:
            self.matrix = []
            self.result = False
            match = re.search(pattern, var, flags=self.flags)
            if match:
                dollar = []
                for i in range(0, match.re.groups+1):
                    dollar.append(match.group(i))
                self.matrix.append(dollar)
                self.result = True

        # Return True if match was found, False otherwise.
        return(self.result)
    
    match = m

    def s(self, var, find, replace, opt=''):
        r'''
            Regular expression substitution (`s` short form, `sub` long form).
            
            ## Usage
            
            ```python
            rex = Rex()
            str = """
            This is a test.
            Test this!
            This is only a test.
            Test that!
            """
            str = rex.s(str, '^test', 'Foobar', 'gim='):
            print(str) 
            >>> 
            This is a test.
            Foobar this!
            This is only a test.
            Foobar that!
            ```

            ## Arguments
            - `var`: Source string variable.
            - `find`: Regular expression pattern.
            - `replace`: Replace with string.
            - `opt`: Optional flags:
            `i` case insensitive
            `m` multi-line 
            `s` single line (. can match anything, including "\n")
            `g` global (replace all)
            `=` return modified value, not Boolean

            ### Data Groups
            Using the `g` flag it is possible to get multiple match group sets.  For `match()` or 
            `m()` the match group sets are all recorded and accessible by specifying `dollar(i, j)`
            where `i` is the match group set and `j` is number of the match group corresponding to 
            $0, $1, $2, etc.  
            
            For `s()` and `sub()`, things are a little different because of the way the parent 
            `re.sub()` function works.  The `re.sub()` function returns the modified string, not a 
            match object that can be interrogated to get match groups.  And there is no iterative 
            `re.sub()` function.

            So how does match groups work?

            - If `replace` is a function, `rex.matrix` is updated for each call to the function.  If
            the `g` flag is enabled, the function is called for each non-overlapping match condition.
            If the `g` flag is not specified, only the first match condition is replaced.  The 
            `replace()` function is passed the `rex.matrix[0]` (i.e. an array with $0, $1, $2, etc.).
            The `rex.matrix` array is updated for each call.
            - If `replace` is a string, `rex.matrix` captures only the first match group set, this 
            even if `g` was specified.

            ## Returns
            Return value depends on if `opt` contains `=` or not.  If yes, the modified string is 
            returned.  If no, a Boolean denoting if a substitution was made.  Several instance
            attributes providing additional information are available:
            - `old`: Old (original) string.
            - `new`: New (modified) string.
            - `result`: True if replacement was made, False otherwise.

        '''
        # Initialize instance attributes.
        self.opt = list(opt.lower())  # List of flag options e.g. 'gs' -> ['g', 's'].
        self.flags = 0                # Integer flag mask used by native re search function.
        self.old = var                # Copy of initial string.  
        self.new = None               # Modified string.  Not used in match() method.    
        self.result = False           # Set to True if match found, False otherwise.  
        self.i = 0                    # Iterator index value.
        self.matrix = []              # Match group matrix.
        
        # Parse options and set self.flags.
        for c in self.opt:
            if c == 'i': self.flags |= re.IGNORECASE; continue
            if c == 'm': self.flags |= re.MULTILINE; continue
            if c == 's': self.flags |= re.DOTALL; continue
            if c == 'g': continue
            if c == '=': continue
            raise Exception(f'Invalid option "{c}".')
        
        # The replace value can be a function, in which case it will be "wrapped" with a decorator
        # function called replace_wrapper().  The function of replace_wrapper() is to get the 
        # dollar group variables to be passed to the specified callback.  
        if replace is not str and callable(replace):
            self.result = False
            def replace_wrapper(m):
                dollar = []
                for i in range(0, m.re.groups + 1):
                    dollar.append(m.group(i))
                    self.result = True
                self.matrix = []
                self.matrix.append(dollar)
                return(replace(dollar))
            # For subs with the 'g' flag option, we do an unbounded re.sub().
            if 'g' in opt:
                self.new = re.sub(find, replace_wrapper, var, flags=self.flags)
            # For bound subs (those without 'g' specified) we set count = 1.  
            else:
                self.new = re.sub(find, replace_wrapper, var, count=1, flags=self.flags)
        # This branch is entered if the replace argument is not a function callable.  
        else:
            # Do an initial search to set self.matrix[0].  
            self.matrix = []
            m = re.search(find, var, flags=self.flags)
            self.result = False
            if m is not None:
                dollar = []
                for i in range(0, m.re.groups+1): 
                    dollar.append(m.group(i))
                self.matrix.append(dollar)
                self.result = True
            # Do the regular expression substitution.
            if 'g' in opt:
                self.new = re.sub(find, replace, var, flags=self.flags)
            else:
                self.new = re.sub(find, replace, var, count=1, flags=self.flags)
        
        # The return value of s() is self.new if the '=' option was specified, or self.result 
        # otherwise.  
        if '=' in opt:
            return(self.new)
        else:
            return(self.result)

    sub = s        

    def split(self, var, pattern, opt='', cnt=0):
        r'''
            Regular expression split.
            
            ## Usage
            
            ```python
            rex = Rex()
            str = "The rain in Spain ain't stopping nobody."
            words = rex.split(str, r'\s+'):
            print(words)
            >>> ['The', 'rain', 'in', 'Spain', "ain't", 'stopping', 'nobody']
            ```

            ## Arguments
            - `var`: Source string variable.
            - `pattern`: Regular expression pattern.
            - `opt`: Optional flags
            `g` = global (find all)
            `i` = case insensitive
            `m` = multi-line 
            `s` = single line (. can match anything, including "\n")
            
            ## Returns
            List of values split on the pattern.
        '''        
        self.opt = set(list(opt.lower()))
        self.old = None
        self.new = None
        self.flags = 0
        self.group = []
        if 'i' in opt: self.flags |= re.IGNORECASE
        if 'm' in opt: self.flags |= re.MULTILINE
        if 's' in opt: self.flags |= re.DOTALL
        lst = re.split(pattern, var, flags=self.flags, maxsplit=cnt)
        return(lst)    

    def trim(self, var, opt='=s'):
        r'''
            Trim leading and trailing spaces.
            
            ## Usage
            
            ```python
            rex = Rex()
            val = rex.trim("  The rain in Spain ain't stopping nobody.  "):
            print(val)
            >>> The rain in Spain ain't stopping nobody.
            ```

            ## Arguments
            - `var`: Source string variable.
            - `opt`: Optional flags
            `g` = global (find all)
            `i` = case insensitive
            `m` = multi-line 
            `s` = single line (. can match anything, including "\n")
            
            ## Returns
            Trimmed string.
        '''        
        var = self.s(var, r'^\s*(.*?)\s*$', r'\1', opt)
        return(var)
    
    def unquote(self, var, opt='=s'):
        r'''
            Remove leading and trailing quotes from string.
            
            ## Usage
            
            ```python
            rex = Rex()
            val = rex.unquote('"Stop what you are doing!"'):
            print(val)
            >>> The rain in Spain ain't stopping nobody.
            ```

            ## Arguments
            - `var`: Source string variable.
            - `pattern`: Regular expression pattern.
            - `opt`: Optional flags
            `g` = global (find all)
            `i` = case insensitive
            `m` = multi-line 
            `s` = single line (. can match anything, including "\n")
            
            ## Returns
            Unquoted string.
        '''        
        var = self.s(var, r'^\s*(\'|\")(.*?)\1\s*', r'\2', opt)
        return(var)

    def escape(self, val):
        r'''
            Escape meta characters in a string.
            
            ## Usage
            
            ```python
            rex = Rex()
            val = rex.escape(r'^\1'):
            ```

            ## Arguments
            - `val`: String to be escaped.
            
            ## Returns
            Escaped string.
        '''            
        return re.escape(val)