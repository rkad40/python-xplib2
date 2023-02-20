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
from rex import Rex
import yaml

# class _DSSCListingTCLParser:

#     def __init__(self, path=None, tcl=None, ignore_files=None, ignore_dirs=None):
#         self.files = []
#         self.ignore_files = []
#         self.ignore_dirs = []
#         self.init(ignore_files, ignore_dirs)
#         if path is not None and tcl is not None: 
#             self.parse(path, tcl)

#     def init(self, ignore_files=None, ignore_dirs=None):
        
#         if ignore_files is not None:
#             t = type(ignore_files)
#             if t == str:
#                 self.ignore_files = [ignore_files]
#             elif t == list:
#                 self.ignore_files = ignore_files
#             elif t == set:
#                 self.ignore_files = list(ignore_files)
#             else:
#                 raise Exception(f"""Expected ignore_files to be a string, list or set (not {t}).""")
        
#         if ignore_dirs is not None:
#             t = type(ignore_dirs)
#             if t == str:
#                 self.ignore_dirs = [ignore_dirs]
#             elif t == list:
#                 self.ignore_dirs = ignore_dirs
#             elif t == set:
#                 self.ignore_dirs = list(ignore_dirs)
#             else:
#                 raise Exception(f"""Expected ignore_dirs to be a string, list or set (not {t}).""")

#     def parse(self, path, tcl, ignore_files=None, ignore_dirs=None):

#         self.init()
#         level = 0

#         def replace(m):
#             nonlocal level
#             if m[1] == '{': 
#                 level += 1
#                 rtn = f"""§{level}:§"""
#                 return rtn
#             if m[1] == '}':
#                 rtn = f"""§:{level}§"""
#                 level -= 1
#                 return rtn

#         self.files = []
#         rex = Rex()
#         tcl = rex.s(tcl, r'([\{\}])', replace, 'g=')
#         self._parse_folder(fs.dirname(path), tcl, 1)

#     def _parse_folder(self, path, tcl, i):
#         rex = Rex()

#         while rex.s(tcl, rf'\s*§{i}:§\s*name\s+§{i+1}:§(.*?)§:{i+1}§\s+type\s+(folder\s+objects|file\s+props)\s*§{i+1}:§(.*?)§:{i+1}§\s*§:{i}§\s*', '', 's') \
#            or rex.s(tcl, rf'\s*§{i}:§\s*name\s+'  +  r'(\S+)' +  rf'\s+type\s+(folder\s+objects|file\s+props)\s*§{i+1}:§(.*?)§:{i+1}§\s*§:{i}§\s*', '', 's'):
#             tcl = rex.new.strip()
#             name = rex.d(1)
#             content = rex.d(3).strip()
#             type = rex.split(rex.d(2), r'\s+')[0]
#             if type == 'folder':
#                 ignore = False
#                 for exp in self.ignore_dirs:
#                     if rex.m(name, exp, 'i'):
#                         ignore = True
#                 if not ignore:
#                     self._parse_folder(fs.join(path, name), content, i+2)
#             elif type == 'file':
#                 ignore = False
#                 for exp in self.ignore_files:
#                     if rex.m(name, exp, 'i'):
#                         ignore = True
#                 if not ignore:
#                     self._parse_file(fs.join(path, name), name, content, i+2)

#     def _parse_file(self, path, name, tcl, i):

#         rex = Rex()

#         orig = tcl
#         orig = rex.s(orig, r'§\d+:§', '{', 'g=')       
#         orig = rex.s(orig, r'§:\d+§', '}', 'g=')  

#         obj = dict(
#             name = None,
#             path = None,
#             type = None,
#             fetch = None,
#             modified = None,
#             version = None,
#             status = None
#         )

#         obj['name'] = name
#         obj['path'] = path
#         obj['type'] = 'file'

#         if rex.s(tcl, rf'mtime\s+§{i}:§(.*?)§:{i}§', '', 's') \
#         or rex.s(tcl, rf'mtime\s+(\S+)', '', 's'):
#             tcl = rex.new.strip()
#             obj['modified'] = rex.d(1)

#         if rex.s(tcl, rf'wsstatus\s+§{i}:§(.*?)§:{i}§', '', 's') \
#         or rex.s(tcl, rf'wsstatus\s+(\S+)', '', 's'):
#             tcl = rex.new.strip()
#             obj['status'] = rex.d(1)

#         if rex.s(tcl, rf'fetchedstate\s+§{i}:§(.*?)§:{i}§', '', 's') \
#         or rex.s(tcl, rf'fetchedstate\s+(\S+)', '', 's'):
#             tcl = rex.new.strip()
#             obj['fetch'] = rex.d(1)

#         if rex.s(tcl, rf'version\s+§{i}:§(.*?)§:{i}§', '', 's') \
#         or rex.s(tcl, rf'version\s+(\S+)', '', 's'):
#             tcl = rex.new.strip()
#             obj['version'] = rex.d(1)

#         if obj['status'] is None and obj['version'] is not None:
#             obj['status'] = obj['version']

#         if obj['version'] == 'Unmanaged':
#             obj['version'] = None

#         if len(tcl) > 0:
#             raise Exception(f"""Invalid syntax for "{path}" element "{orig}" near "{tcl}".""")

#         self.files.append(obj)

class DSSC():
    
    def __init__(self):
        self.exe = None
    
    def init(self):
        if self.exe is not None and fs.exists(self.exe): return
        settings_dir = fs.join(fs.appdata(), '.ApplicationSettings')
        if not fs.exists(settings_dir): fs.mkdir(settings_dir)
        settings_file = fs.join(settings_dir, 'DesignSync.yml')
        data = {}
        write_file = False
        while True:
            if not fs.exists(settings_file):
                data['DSSCExecutable'] = None
                write_file = True
                print(f"""ERROR: DSSCExecutable path not defined.  Please specify path in file "{settings_file}".""")
                break
            txt = fs.read(settings_file, to_string=True)
            data = yaml.safe_load(txt)
            if 'DSSCExecutable' not in data:
                data['DSSCExecutable'] = None
                write_file = True
                print(f"""ERROR: DSSCExecutable path not defined.  Please specify path in file "{settings_file}".""")
                break
            if not fs.exists(data['DSSCExecutable']):
                print(f"""ERROR: DSSCExecutable path "data['DSSCExecutable']" does not exist.  Please specify valid path in file "{settings_file}".""")
                break
            self.exe = data['DSSCExecutable']
            return
        if write_file == True:
            txt = yaml.safe_dump(data)
            fs.writeif(settings_file, txt)
        exit()

    def getvault(self, path):
        self.init()
        cwd = fs.cwd()
        fs.cd(path)
        meta = self.getmeta(path)
        vault = None
        if meta is not None and len(meta) > 0 and 'Vault' in meta[0]:
            vault = '/'.join(meta[0]['Vault'].split('/')[0:-1])
        fs.cd(cwd)
        return vault

    def getmeta(self, path):
        self.init()
        cwd = fs.cwd()
        fs.cd(path)
        contents_file = fs.join(path, '.SYNC', 'Contents')
        if not fs.exists(contents_file): 
            fs.cd(cwd)
            return None
        rex = Rex()
        headers = None
        data = []
        for line in fs.read(contents_file):
            if not rex.m(line, r'^\<(.*?)\>\s*$', ''): continue
            items = rex.split(rex.d(1), r'\>\s*\<')
            if headers is None: 
                headers = items
                continue
            row = {}
            for i in range(0, min(len(headers), len(items))):
                row[headers[i]] = items[i]
            data.append(row)
        fs.cd(cwd)
        return data
        
    def setvault(self, path, vault):
        """
        Do DSSC setvault operation.
        # Arguments
        - path = local directory
        - vault = corresponding DSSC vault URL
        """
        self.init()
        cwd = fs.cwd()
        fs.cd(path)
        args = [self.exe, "setvault", vault, '.']
        self._print_cmd(args)
        subprocess.run(args)
        fs.cd(cwd)

    def diff(self, path):
        """
        Do DSSC populate operation.
        # Arguments
        - path = file to diff
        """
        self.init()
        # cwd = fs.cwd()
        args = [self.exe, "diff"]
        args.append('-gui')
        args.append(path)
        self._print_cmd(args)
        subprocess.run(args)
        # fs.cd(cwd)
    
    def populate(self, path, rec=True, force=False):
        """
        Do DSSC populate operation.
        # Arguments
        - path = local directory
        - rec = populate recursively into sub-directories
        - force = force over-write of locally modified files
        """
        self.init()
        cwd = fs.cwd()
        fs.cd(path)
        args = [self.exe, "pop"]
        if rec: args.append('-rec')
        if force: args.append('-force')
        self._print_cmd(args)
        subprocess.run(args)
        fs.cd(cwd)

    def ls(self, path, modified=True, recursive=False, ignore_files=[], ignore_dirs=[]):
        rex = Rex()
        self.init()
        if ignore_files is None: ignore_files = []
        if ignore_dirs is None: ignore_dirs = []
        cwd = fs.cwd()
        if not fs.isdir(path):
            raise Exception(f'Argument path value "{path}" is not a directory.')
        fs.cd(path)
        args = [self.exe, 'ls']
        if modified: args.append('-modified')
        if recursive: args.append('-recursive')
        self._print_cmd(args)
        proc = subprocess.Popen(args, stdout=subprocess.PIPE)
        ls_out = proc.communicate()[0].decode()
        ls_out = rex.s(ls_out, r'\r', '\n', 'g=')
        ls_out = rex.s(ls_out, r'\r\n', '\n', 'g=')
        ls_lines = rex.split(ls_out, r'\n')
        abs_dir_path = None
        rel_dir_path = None
        base_dir_name = None
        dir_list = None
        loc = {}
        all = {}
        for line in ls_lines:
            if rex.s(line, r'^Directory\s+of:\s+file:///(\w)\|(.*)\s*', '', ''):
                abs_dir_path = fs.fix(rex.d(1) + ":" + rex.d(2))
                rel_dir_path = fs.unix(fs.rel(abs_dir_path, cwd))
                base_dir_name = fs.filename(abs_dir_path)
                dir_list = rel_dir_path.split('/')
                continue
            if abs_dir_path is None:
                continue
            if rex.m(line, r'^Time\s+Stamp'):
                loc['modified'] = [0, 17]
                loc['status'] = [18, line.find('WS Status') + len('WS Status') + 1]
                loc['version'] = [line.find('Version'), line.find('Type') - 1]
                loc['type'] = [line.find('Type'), line.find('Name') - 1]
                loc['name'] = [line.find('Name'), 1000]
            if len(line) == 0: 
                continue
            data = {}
            for key in loc:
                data[key] = line[loc[key][0]:loc[key][1]].strip()
            if data['modified'] != 'Time Stamp' and not data['modified'].startswith('---'):
                name = data['name']
                if name == 'mtr_fuse_converter.cpython-39.pyc':
                    stop = True
                keep = True
                for r in ignore_files: 
                    if rex.m(name, r, 'i'):
                        keep = False
                        break
                for dir in dir_list:
                    for r in ignore_dirs:
                        if rex.m(dir, r, 'i'):
                            keep = False
                            break
                if keep == True:
                    data['path'] = rel_dir_path
                    if data['version'] == 'Unmanaged':
                        data['version'] = None
                        data['status'] = 'Unmanaged'
                    key = rel_dir_path + '/' + name
                    all[key] = data
        fs.cd(cwd)
        return all

    # def ls(self, path, modified=True, recursive=False, ignore_files=None, ignore_dirs=None):
    #     self.init()
    #     cwd = fs.cwd()
    #     fs.cd(path)
    #     args = [self.exe, "ls", '-format', 'list']
    #     if modified: args.append('-modified')
    #     if recursive: args.append('-recursive')
    #     self._print_cmd(args)
    #     proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    #     ls_out = proc.communicate()[0].decode()
    #     files = _DSSCListingTCLParser(path, ls_out, ignore_files, ignore_dirs).files
    #     fs.cd(cwd)
    #     return files

    def ci(self, file, comment, path=None, managed=False):
        self.init()
        cwd = None
        if path is not None:
            cwd = fs.cwd()
            fs.cd(path)
        args = [self.exe, "ci", '-comment', comment]
        if not managed:
            args.append('-new')
        args.append(file)
        self._print_cmd(args)
        proc = subprocess.Popen(args, stdout=subprocess.PIPE)
        ci_out = proc.communicate()[0].decode()
        if path is not None:
            fs.cd(cwd)
        return(ci_out)

    def co(self, file, path=None):
        self.init()
        cwd = None
        if path is not None:
            cwd = fs.cwd()
            fs.cd(path)
        args = [self.exe, "co", file]
        self._print_cmd(args)
        proc = subprocess.Popen(args, stdout=subprocess.PIPE)
        out = proc.communicate()[0].decode()
        if path is not None:
            fs.cd(cwd)
        return out

    def _print_cmd(self, args):
        render = []
        for arg in args:
            if ' ' in args:
                arg = f'''"{arg}"'''
            render.append(arg)
        print('% ' + ' '.join(render))

api = DSSC()
