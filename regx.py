'''
## Description
An intuitive regular expression class wrapper for Python's often confusing `re`
regular expression module.

## Usage
```
from regx import Regx
regx = Regx()
...
# Reformat lines of phone numbers.  
val = regx.s(val, r'^\s*(\d{3})(\d{3})(\d{4})\s*$', r'\1-\2-\3', '=gm')
```
'''

import re

class Regx():
    def __init__(self): 
        self.clear()
    
    def clear(self):
        r'''
            ## Description
            Reset `regx` object.
            
            ## Usage
            ```
            regx.clear()
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
        self.cnt = 0
        self.result = False
        self.opt = set()
        self.matched = None
    
    def m(self, var, pattern, opt=''):
        r'''
            ## Description
            Regular expression match (`m` short form, `match` long form).
            
            ## Usage
            ```
            regx = Regx()
            str = "The rain in Spain ain't stopping nobody."
            if regx.match(str, r'(?:^|\s*)(\w*?ai.*?)(?:\s+|$)', 'g'):
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
            - `regx.result`: True if match was found, False otherwise.
            - `regx.group`: Array of matching groups
            - `regx.groups`: Array of global matching groups
            - `regx.cnt`: Number of matched groups
        '''
        # Initialize instance attributes.
        self.opt = list(opt.lower())
        self.old = var
        self.new = None
        self.flags = 0
        self.cnt = 0
        self.group = []
        self.groups = []
        self.result = False
        
        # Parse options and set self.flags.
        for c in self.opt:
            if c == 'i':
                self.flags |= re.IGNORECASE
                continue
            if c == 'm':
                self.flags |= re.MULTILINE
                continue
            if c == 's':
                self.flags |= re.DOTALL
                continue
            if c == 'g':
                continue
            raise Exception(f'Invalid option "{c}".')
        
        # If a global search is indicated do re.findall().  This function returns all non-overlapping 
        # matches of pattern in the source string as a list of strings.  If the match expressions 
        # in parentheses are not nested, you simply get a list of matches. If nested expressions, 
        # e.g "((John|Jane)\s+(Doe|Buck))", then you get a list of tuples.  This function sets 
        # self.group equal to the first match group regardless.  For for "John Doe, Jane Buck" 
        # self.group would be ['John Doe', 'John', 'Doe'].  But with the global flag enabled, there
        # are more match groups.  So self.groups get them.  In this case, self.groups would be
        # [['John Doe', 'John', 'Doe'], ['Jane Buck', 'Jane', 'Buck']].  Note: (1) self.group is the 
        # same as self.groups[0] and (2) the tuples are recast as lists.
        if 'g' in self.opt:

            self.group = []
            self.groups = []
            self.result = False
            match_object_index = 0
            for match_object in re.finditer(pattern, var, flags=self.flags):
                groups_list = []
                if match_object_index == 0:
                    for i in range(1, match_object.re.groups+1):
                        self.group.append(match_object.group(i))
                for i in range(1, match_object.re.groups+1):
                    groups_list.append(match_object.group(i))
                self.groups.append(groups_list)
                self.result = True
                match_object_index += 1

            # matches = re.findall(pattern, var, flags=self.flags)
            # if len(matches) > 0:
            #     t = type(matches[0])
            #     if t == tuple:
            #         self.group = list(matches[0])
            #         for match in matches:
            #             self.groups.append(list(match))
            #     else:
            #         self.group = matches
            #     self.result = True
            # else:
            #     self.group = []
            #     self.result = False




            # self.group = m
            # self.result = True if len(m) > 0 else False

            # if len(m) > 0:
            #     t = type(m[0])
            #     if t == tuple:
            #         self.group = list(m[0])
            #     elif t == str:
            #         self.group.append(m[0])
            #     self.result = True 
            # else:
            #     self.group = []
            #     self.result = False

        else:
            # if re.search(pattern, var, flags=self.flags):
            #     m = re.findall(pattern, var, flags=self.flags)
            #     self.group = []
            #     # Value m should always be > 0 because we did an initial re.search() was true if we
            #     # get to this point.  
            #     if len(m) > 0:
            #         t = type(m[0])
            #         if t == tuple:
            #             self.group = list(m[0])
            #         elif t == str:
            #             self.group.append(m[0])
            #     self.result = True 
            # else:
            #     self.group = []
            #     self.result = False
        # The "else" branch is hit if global matching is disabled.  In this case we use re.search().
        # Python regular expression syntax and implementation is maddening at times.  The function 
        # re.search() returns a match object, not a list of matching groups or group tuples like 
        # re.findall().  Getting the list of matching groups takes a bit of work.  You must 
        # iterate through indexed match_object.group entries.  Here's the rub, match_object.group(i)
        # returns the string but you have to correctly iterate over the indices to get these out.
        # In short, you do "for i in range(1, match_object.re.groups+1)".  We skip over the first 
        # item match_object.groups(0) because it is the full matched string.  If you want this, you
        # can always nest the matched expression like so: "((John|Jane)\s+(Doe|Buck))".   

            self.group = []
            self.result = False
            match_object = re.search(pattern, var, flags=self.flags)
            if match_object:
                for i in range(1, match_object.re.groups+1):
                    self.group.append(match_object.group(i))
                self.result = True

            # for match in re.finditer(pattern, var, flags=self.flags):
            #     t = type(matches)
            #     if t == tuple:
            #         self.group = list(match)
            #     else:
            #         self.group = match
            #     self.result = True

            # matches = re.findall(pattern, var, flags=self.flags)
            # if len(matches) > 0:
            #     t = type(matches[0])
            #     if t == tuple:
            #         self.group = list(matches[0])
            #     else:
            #         self.group = matches
            #     self.result = True
            # else:
            #     self.group = []
            #     self.result = False


            # if len(matches) > 0:
            #     self.groups = matches
            #     self.result = True
            # else:
            #     self.result = False
            # pass

            # m = re.findall(pattern, var, flags=self.flags)
            # if len(m) > 0:
            #     t = type(m[0])
            #     if t == tuple:
            #         self.group = list(m[0])
            #     elif t == str:
            #         self.group.append(m[0])
            #     self.result = True 
            # else:
            #     self.group = []
            #     self.result = False
        
        self.cnt = len(self.group)
        return(self.result)
    
    match = m

    def s(self, var, find, replace, opt=''):
        r'''
            ## Description
            Regular expression substitution (`s` short form, `sub` long form).
            
            ## Usage
            ```
            regx = Regx()
            str = """
            This is a test.
            Test this!
            This is only a test.
            Test that!
            """
            str = regx.s(str, '^test', 'Foobar', 'gim='):
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
            
            NOTE: For inline substitution in the `replace` argument value, the first match group is
            \1, the second \2, etc., etc.
            
            ## Returns
            Return value depends on if `opt` contains `=` or not.  If yes, the modified string is 
            returned.  If no, a Boolean denoting if a substitution was made.  Several instance
            attributes providing additional information are available:
            - `old`: Old (original) string.
            - `new`: New (modified) string.
            - `result`: True if replacement was made, False otherwise.
            - `group`: Array of matching groups.  NOTE: The array is zero indexed, meaning `group[0]`
            contains the first match.  For inline substitutions using the `replace` argument, the 
            first matched group is \1.  
            - `cnt`: Number of matched groups.
        '''
        self.opt = set(list(opt.lower()))
        self.old = var
        self.new = None
        self.flags = 0
        self.group = []
        self.cnt = 0
        if 'i' in opt: self.flags |= re.IGNORECASE
        if 'm' in opt: self.flags |= re.MULTILINE
        if 's' in opt: self.flags |= re.DOTALL
        m = re.search(find, var, flags=self.flags)
        self.result = False
        if m is not None:
            self.result = True
            for i in range(1, m.re.groups+1): 
                self.group.append(m.group(i))
        if replace is not str and callable(replace):
            def replace_wrapper(m):
                self.group = []
                if m is not None:
                    for i in range(1, m.re.groups + 1):
                        self.group.append(m.group(i))
                return(replace(self.group))
            if 'g' in opt:
                self.new = re.sub(find, replace_wrapper, var, flags=self.flags)
            else:
                self.new = re.sub(find, replace_wrapper, var, count=1, flags=self.flags)
        else:
            if 'g' in opt:
                self.new = re.sub(find, replace, var, flags=self.flags)
            else:
                self.new = re.sub(find, replace, var, count=1, flags=self.flags)
        if '=' in opt:
            return(self.new)
        else:
            return(self.result)

    sub = s        

    def split(self, var, pattern, opt=''):
        r'''
            ## Description
            Regular expression split.
            
            ## Usage
            ```
            regx = Regx()
            str = "The rain in Spain ain't stopping nobody."
            words = regx.split(str, r'\s+'):
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
        self.cnt = 0
        if 'i' in opt: self.flags |= re.IGNORECASE
        if 'm' in opt: self.flags |= re.MULTILINE
        if 's' in opt: self.flags |= re.DOTALL
        lst = re.split(pattern, var, flags=self.flags)
        return(lst)    

    def trim(self, var, opt='=s'):
        r'''
            ## Description
            Trim leading and trailing spaces.
            
            ## Usage
            ```
            regx = Regx()
            val = regx.trim("  The rain in Spain ain't stopping nobody.  "):
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
            ## Description
            Remove leading and trailing quotes from string.
            
            ## Usage
            ```
            regx = Regx()
            val = regx.unquote('"Stop what you are doing!"'):
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