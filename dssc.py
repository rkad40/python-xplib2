r"""
# `dssc`

Basic DesignSync API.

## Usage
```python
import dssc
...
prog = r'R:\users\me\prog'
dssc.api.setvault(prog, 'sync://sync-15128:15128/Projects/nte_ls1046a/program')
dssc.api.populate(prog, rec=True, force=False)
```
"""

import fs, subprocess

POSSIBLE_PATHS = \
[
    r'C:\Program Files\ENOVIA\Synchronicity',
    r'C:\Program Files (x86)\ENOVIA\Synchronicity',
]

class DSSC():
    def __init__(self):
        executables = {}
        self.exe = None
        for exe in fs.get_files(POSSIBLE_PATHS, r'dssc\.exe$', True, False):
            mod = fs.last_modified(exe)
            executables[mod] = exe
        for mod in sorted(executables, reverse=True):
            self.exe = executables[mod]
            break
        if self.exe is None: raise Exception('Could not find dssc.exe in specified paths: {}'.format(', '.join(POSSIBLE_PATHS)))
    def setvault(self, path, vault):
        """
        Do DSSC setvault operation.
        # Arguments
        - path = local directory
        - vault = corresponding DSSC vault URL
        """
        args = [self.exe, "setvault", vault, path]
        subprocess.run(args)
    def populate(self, path, rec=True, force=False):
        """
        Do DSSC populate operation.
        # Arguments
        - path = local directory
        - rec = populate recursively into sub-directories
        - force = force over-write of locally modified files
        """
        args = [self.exe, "pop"]
        if rec: args.append('-rec')
        if force: args.append('-force')
        subprocess.run(args)

api = DSSC()
