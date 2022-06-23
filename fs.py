'''
A plethora of file system functions.

## Usage

```python
import fs
```

'''

import os, sys, re, filecmp, shutil, time, io

def open_file(path, mode='r', encoding='utf-8', errors='ignore'):
  '''
    ## Description
    Open a file.
    
    ## Usage
    
    ```python
    fstream = fs.open_file(file_path)
    ```
    
    ## Arguments
    - `path`: file as str
    - `mode='r'`: 'r' for read, 'w' for write
    - `encoding`: encoding
    
    ## Aliases
    `open_file`, `fopen`

    ## Returns
    file stream (use `close()` to close when done)
  '''
  try:
    f = open(path, mode=mode, encoding=encoding, errors=errors)
    return f
  except Exception as err:
    if path is None: raise Exception(f'''Required path variable not defined: {err}''')
    raise Exception(f'''Could not open file "{path}": {err}''')

fopen = open_file

def read_file(path, to_string=False, to_iter=False, encoding='utf-8', errors='ignore'):
  '''
    ## Description
    Read file and return a list of lines.
    
    ## Usage
    
    ```python
    my_lines = fs.read_file(path)
    ```
    
    ## Arguments
    - `path`: file as str
    - `to_string`: optional bool; if True return content as a string
    - `to_iter`: optional bool; if True return content is an iterator
    - `encoding`: encoding
    
    ## Aliases
    `read_file`, `fread`, `read`

    ## Returns
    list of lines each of typ str (or a single string if to_string is True)
  '''
  try:
    f = open(path, 'r', encoding=encoding, errors=errors)
    if to_iter:
      return(f)
    if to_string:
      text = "".join(f.readlines())
      f.close()
      return(text)
    else:
      lines = f.readlines()
      f.close()
      return(lines)
  except Exception as err:
    # Close file connection if open.
    try: f.close()
    except: pass
    # # Default encoding is "utf-8".  If this fails, try to read with encoding None.  I have oddly 
    # # found that "utf-8" is the safest thing to do but that this sometimes fails and encoding None
    # # will often work.  It takes a combination of both unfortunately.  
    # if encoding is not None:
    #   return read_file(path, to_string=to_string, to_iter=to_iter, encoding=None)
    # Raise verbose exception.
    if path is None: raise Exception(f'''Required path variable not defined: {err}''')
    raise Exception(f'''Could not read file "{path}": {err}''')

fread = read_file
read = read_file
fread = read_file
read = read_file

def reads(path, encoding='utf-8', errors='ignore'):
  '''
    ## Description
    Read file and return as string.
    
    ## Usage
    
    ```python
    content = fs.reads(path)
    ```
    
    ## Arguments
    - `path`: file as str
    - `encoding`: encoding
    
    ## Returns
    file content as string

  '''
  return read(path, to_string=True, encoding=encoding, errors=errors)

def write_file(path, content, encoding='utf-8', errors='ignore'):
  '''
    ## Description
    Write content to file.
    
    ## Usage
    
    ```python
    fs.write_file(path, content)
    ```

    ## Arguments
    - `path`: file as str
    - `content`: str or list data to write to file
    
    ## Aliases
    `write_file`, `fwrite`, `write`

    ## Returns
    nothing
  '''  
  try:
    with io.open(path, 'w', encoding=encoding, errors=errors) as f:
      if type(content) == str:
        f.write(content)
        f.close()
      elif type(content) == list:
        f.writelines(content)
        f.close()
      else:
        raise Exception('Invalid content of type "{}"; must be "str" or "list".'.format(type(content).__name__))
  except Exception as err:
    # Close file connection if open.
    try: f.close()
    except: pass
    # # Default encoding is "utf-8".  If this fails, try to read with encoding None.  I have oddly 
    # # found that "utf-8" is the safest thing to do but that this sometimes fails and encoding None
    # # will often work.  It takes a combination of both unfortunately.  
    # if encoding is not None:
    #   return write_file(path, content, encoding=None)
    # Raise verbose exception.
    if path is None: raise Exception(f'''Required path variable not defined: {err}''')
    raise Exception(f'''Could not write file "{path}": {err}''')

fwrite = write_file
write = write_file

def delete_file(path):
  '''
    ## Description
    Delete a file.
    
    ## Usage
    
    ```python
    fs.delete_file(path)
    ```

    ## Arguments
    - `path`: file as str
    
    ## Aliases
    `delete_file`, `unlink`, `fdelete`, `fdel`

    ## Returns
    nothing
  '''
  try:
    os.remove(path)
  except Exception as err:
    if path is None: raise Exception(f'''Required path variable not defined: {err}''')
    raise Exception(f'''Could not delete file "{path}": {err}''')

unlink = delete_file
fdelete = delete_file
fdel = delete_file

def delete_dir(path):
  '''
    ## Description
    Delete a directory.
    
    ## Usage
    
    ```python
    fs.delete_dir(path)
    ```

    ## Arguments
    - `path`: directory as str
    
    ## Aliases
    `delete_dir`, `rmdir`

    ## Returns
    nothing
  '''  
  try:
    shutil.rmtree(path)
  except Exception as err:
    raise Exception(f'''Could not delete directory "{path}": {err}''')

rmdir = delete_dir
# ddelete = delete_dir
# ddel = delete_dir

def write_file_if_changed(path, content, create_dir=True, simple=False, mode=None, encoding='utf-8'):
  '''
    ## Description
    Write a file only if it results in a change.
    
    ## Usage
    
    ```python
    fs.write_file_if_changed(path, content)
    ```

    ## Arguments
    - `path`: file as str
    - `content`: content to write to file
    - `create_dir`: create base dir if it does not already exist (default = True)
    - `simple`: if True, return simple status string (e.g. "created", "identical", or "updated"); if False, return bool (True if copied, False otherwise)
    - `mode`: assert file mode (default = None)  
    
    ## Aliases
    `write_file_if_changed`, `fwriteif`, `writeif`

    ## Returns
    A string indicating the action that was performed.
  '''  
  try:
    dir_name = get_dir_name(path)
    if create_dir == True and not dir_exists(dir_name): 
      dir_mode = mode if mode is not None else 0x755
      os.makedirs(dir_name, dir_mode)
    if not dir_exists(dir_name): 
      raise Exception('Cannot write file "{}"; base directory "{}" does not exist.'.format(path, dir_name))
    if not file_exists(path):
      write_file(path, content, encoding=encoding)
      if mode is not None: os.chmod(path, mode)
      if simple: return('created')
      else: return('Created new file "{}".'.format(path))
    else:
      temp_file = join_names(get_dir_name(path), '.' + get_root_name(path) + '-' + str(time.time()) + '.' + get_ext(path))
      write_file(temp_file, content, encoding=encoding)
      if files_are_identical(temp_file, path):
        delete_file(temp_file)
        if simple: return('identical')
        else: return('No change to file "{}".'.format(path))
      else:
        shutil.move(temp_file, path)
        if simple: return('updated')
        else: return('Updated file "{}".'.format(path))
  except Exception as err:
    if path is None: raise Exception(f'''Required path variables not defined: {err}''')
    raise Exception(f'''Could not write file "{path}": {err}''')

fwriteif = write_file_if_changed
writeif = write_file_if_changed

def rename_file(orig_file, new_file):
  '''
    ## Description
    Rename or move a file.
    
    ## Usage
    
    ```python
    fs.rename_file(orig_file, new_file)
    ```

    ## Arguments
    - `orig_file`: original file
    - `new_file`: new file

    ## Aliases
    `rename_file`, `frename`, `rename`
    
    ## Returns
    New file name.
  '''
  try:
    shutil.move(orig_file, new_file)
    return(new_file)
  except Exception as err:
    raise Exception(f'''Could not rename file "{orig_file}" to "{new_file}": {err}''')

frename = rename_file
rename = rename_file

def get_file_name(path):
  '''
    ## Description
    Get the base file name.
    
    ## Usage
    
    ```python
    file_name = fs.get_file_name(path)
    ```

    ## Arguments
    - `path`: file as str

    # Aliases
    `get_file_name`, `filename`, `fname`
    
    ## Returns
    Base file name as str.
  '''
  try:
    rval = os.path.basename(path)
    return(rval)
  except Exception as err:
    if path is None: raise Exception(f'''Required path variables not defined: {err}''')
    raise Exception(f'''Could get file name for file "{path}": {err}''')

fname = get_file_name
filename = get_file_name
  
def get_root_name(path):
  '''
    ## Description
    Get the root file name.
    
    ## Usage
    
    ```python
    root_name = fs.get_root_name(path)
    ```

    ## Arguments
    - `path`: file as str

    ## Aliases
    `get_root_name`, `froot`, `rootname`
    
    ## Returns
    Root file name as str (i.e. `fs.get_file_name()` minus extension).
  '''
  try:
    rval = get_file_name(path)
    rval = os.path.splitext(rval)[0]
    return(rval)
  except Exception as err:
    if path is None: raise Exception(f'''Required path variables not defined: {err}''')
    raise Exception(f'''Could not get root name for file "{path}": {err}''')

froot = get_root_name
rootname = get_root_name

def prepend_root_name(path, val):
  '''
    ## Description
    Prepend val to the file root name (before the root name).
    
    ## Usage
    
    ```python
    orig_file = '/home/files/test.txt'
    temp_file = fs.append_root_name(orig_file, '.')
    # now temp_file = 'home/files/.test.txt'
    ```

    ## Arguments
    - `path`: file as str
    - `val`: token to prepend to root name

    ## Aliases
    `prepend_root_name`, `prepend`
    
    ## Returns
    File name as string.
  '''
  try:
    dir = get_dir_name(path)
    name = get_file_name(path)
    root = get_root_name(name)
    ext = get_ext(name)
    rval = join_names(dir, val + root + '.' + ext)
    return(rval)
  except Exception as err:
    if path is None: raise Exception(f'''Required path variables not defined: {err}''')
    raise Exception(f'''Could not prepend "{val}" to root name of file "{path}": {err}''')

prepend = prepend_root_name
  
def append_root_name(path, val):
  '''
    ## Description
    Append val to the file root name (before the extension).
    
    ## Usage
    
    ```python
    orig_file = '/home/files/test.txt'
    temp_file = fs.append_root_name(orig_file, '-temp')
    # now temp_file = 'home/files/test-temp.txt'
    ```

    ## Arguments
    - `path`: file as str
    - `val`: token to append to root name
    
    ## Aliases
    `append_root_name`, `append`

    ## Returns
    File name as string.
  '''
  try:
    dir = get_dir_name(path)
    name = get_file_name(path)
    root = get_root_name(name)
    ext = get_ext(name)
    rval = join_names(dir, root + val + '.' + ext)
    return(rval)
  except Exception as err:
    if path is None: raise Exception(f'''Required path variables not defined: {err}''')
    if val is None: raise Exception(f'''Required val variables not defined: {err}''')
    raise Exception(f'''Could not append "{val}" to root name of file "{path}": {err}''')

append = append_root_name
  
def remove_ext(path):
  '''
    ## Description
    Remove the extension from file name.
    
    ## Usage
    
    ```python
    file_name = fs.get_ext(path)
    ```

    ## Arguments
    - `path`: file as str

    ## Aliases
    `remove_ext`, `rmext`
    
    ## Returns
    Path minus file extension as str.
  '''
  try:
    rval = path
    rval = re.sub(r'\.\w+$','',rval)
    return(rval)
  except Exception as err:
    if path is None: raise Exception(f'''Required path variables not defined: {err}''')
    raise Exception(f'''Could not remove extension from "{path}": {err}''')


rmext = remove_ext

def get_ext(path):
  '''
    ## Description
    Get the file extension.
    
    ## Usage
    
    ```python
    ext = fs.get_ext(path)
    ```

    ## Arguments
    - `path`: file as str

    ## Aliases
    `get_ext`, `ext`
    
    ## Returns
    File extension as str in lower case.
  '''
  try:
    rval = path
    m = re.search(r'\.(\w+)$',rval)
    ext = m.group(1) if m else ""
    ext = ext.lower()
    return(ext)
  except Exception as err:
    if path is None: raise Exception(f'''Required path variables not defined: {err}''')
    raise Exception(f'''Could not get extension for file "{path}": {err}''')

ext = get_ext

def fsplit(path):
  '''
    ## Description
    Split file name return tuple of root name and ext (lower case).
    
    ## Usage
    
    ```python
    root,ext = fs.fsplit(path)
    ```

    ## Arguments
    - `path`: file as str
    
    ## Returns
    Tuple consisting of root name and ext (lower case).
  '''
  try:
    rval = path
    m = re.search(r'^(.*?)\.(\w+)$',rval)
    if m:
      root = m.group(1)
      ext = m.group(2).lower()
    else:
      root = path
      ext = ''
    return(root,ext)
  except Exception as err:
    if path is None: raise Exception(f'''Required path variables not defined: {err}''')
    raise Exception(f'''Could not split file "{path}" into name and extension tuple: {err}''')

def get_dir_name(path,count=1):
  '''
    ## Description
    Get dir name.
    
    ## Usage
    
    ```python
    dir = fs.get_dir_name(path)
    ```

    ## Arguments
    - `path`: file as str
    - `count`: depth (default = 1)

    ## Aliases
    `get_dir_name`, `dirname`
    
    ## Returns
    Dir name as string.
  '''
  try:
    path = get_abs_path(path)
    # if is_file(path): path = os.path.dirname(path)
    while count > 0:
      path = os.path.dirname(path)
      count -= 1
    return(path)
  except Exception as err:
    if path is None: raise Exception(f'''Required path variables not defined: {err}''')
    raise Exception(f'''Could not get director name of "{path}": {err}''')
  
dirname = get_dir_name

def fix_path_name(*path):
  '''
    ## Description
    Fix path name (render as Windows path). 
    
    ## Usage
    
    ```python
    dir = fs.fix_path_name(path)
    ```

    ## Arguments
    - `path`: path as str tuple (e.g. 'C:', 'users/me')
    
    ## Aliases
    `fix_path_name`, `fix`

    ## Returns
    Windows style path as str.
  '''
  try:
    path = '/'.join(path)
    if sys.platform == 'win32': 
      path = re.sub(r'/', r'\\', path)
    else : 
      path = re.sub(r'\\', r'/', path)
    path = os.path.normpath(path)
    return(path)
  except Exception as err:
    raise Exception(f'''Could not fix path name "{path}": {err}''')

fix = fix_path_name

def get_unix_path(path):
  '''
    ## Description
    Get the UNIX / Linux style path.
    
    ## Usage
    
    ```python
    my_path = fs.get_unix_path(some_path)
    ```

    ## Arguments
    - `path`: file or folder path as str

    ## Aliases
    `get_unix_path`, `unix`
    
    ## Returns
    Absolute path as str.
  '''
  try:
    path = re.sub(r'\\', r'/', path)
    return(path)
  except Exception as err:
    raise Exception(f'''Could get UNIX style path name "{path}": {err}''')

unix = get_unix_path

def file_exists(path):
  '''
    ## Description
    Test if file exists.
    
    ## Usage
    
    ```python
    if fs.file_exists('C:/Data/Last.txt'): # Do something
    ```

    ## Arguments
    - `path`: file path

    ## Aliases
    `file_exists`, `exists`
    
    ## Returns
    True if file exists, False otherwise.
  '''
  return(os.path.exists(path))

exists = file_exists

def dir_exists(path):
  '''
    ## Description
    Test if dir path exists.
    
    ## Usage
    
    ```
    if fs.dir_exists('C:/Data'): # Do something
    ```

    ## Arguments
    - `path`: dir path

    ## Aliases
    `dir_exists`, `exists`
    
    ## Returns
    True if dir exists, False otherwise.
  '''
  return(os.path.exists(path))

def get_rel_path(abs_path, base_path=None):
  '''
    ## Description
    Get the relative path.
    
    ## Usage
    
    ```python
    my_path = fs.get_rel_path(long_path, base_path)
    ```

    ## Arguments
    - `abs_path`: absolute path to be converted into relative path
    - `base_path`: base path from which the relative path begins

    ## Aliases
    `get_rel_path`, `rel`
    
    ## Returns
    Relative path as a str.
  '''
  try:
    if base_path is None: base_path = get_cwd()
    if is_file(base_path): base_path = get_dir_name(base_path)
    return(os.path.relpath(abs_path, base_path))
  except Exception as err:
    raise Exception(f'''Could not get relative path for "{abs_path}" given base path "{base_path}": {err}''')


rel = get_rel_path

def get_app_data_path():
  '''
    ## Description
    Get app data path %APPDATA%.
    
    ## Usage
    
    ```python
    app_data_path = fs.get_app_data_path()
    ```
    
    ## Aliases
    `get_app_data_path`, `appdata`

    ## Returns
    absolute path to %APPDATA%
  '''
  try:
    return(get_abs_path(os.getenv('APPDATA')))
  except Exception as err:
    raise Exception(f'''Could not get APPDATA path: {err}''')

appdata = get_app_data_path

def get_temp_dir():
  '''
    ## Description
    Get temporary directory path %TEMP%.
    
    ## Usage
    
    ```python
    temp_path = fs.get_temp_dir()
    ```
    
    ## Aliases
    `get_temp_dir`, `tempdir`

    ## Returns
    Absolute path to %TEMP%
  '''
  try:
    return(get_abs_path(os.getenv('TEMP')))
  except Exception as err:
    raise Exception(f'''Could not get TEMP directory path: {err}''')

tempdir = get_temp_dir

def get_cwd():
  '''
    ## Description
    Get current working directory.
    
    ## Usage
    
    ```python
    my_path = fs.get_cwd()
    ```

    ## Aliases
    `get_cwd`, `cwd`
    
    ## Returns
    Absolute path as a str.
  '''
  try:
    return(os.getcwd())
  except Exception as err:
    raise Exception(f'''Could not get CWD: {err}''')

cwd = get_cwd

def change_dir(dir_path):
  '''
    ## Description
    Change directory.
    
    ## Usage
    
    ```python
    fs.change_dir(dir_path)
    ```

    ## Aliases
    `change_dir`, `cd`

    ## Returns
    nothing
  '''
  try:
    return(os.chdir(dir_path))
  except Exception as err:
    raise Exception(f'''Could not change directory to "{dir_path}": {err}''')

cd = change_dir

def get_script_file():
  '''
    ## Description
    Get current script file being executed.
    
    ## Usage
    
    ```python
    this_script = fs.get_script_file()
    ```

    ## Aliases
    `get_script_dir`, `script`

    ## Returns
    Absolute path to current script file.
  '''
  try:
    script_file = sys.argv[0]
    if not is_abs_path(script_file): script_file = get_abs_path(script_file)
    return(script_file)
  except Exception as err:
    raise Exception(f'''Could not get script file name: {err}''')

script = get_script_file

def get_script_dir():
  '''
    ## Description
    Get directory of the current script file being executed.
    
    ## Usage
    
    ```python
    script_dir = fs.get_script_dir()
    ```

    ## Aliases
    `get_script_dir`, `scriptdir`

    ## Returns
    Absolute path to current script file directory.
  '''
  try:
    return(get_dir_name(get_script_file()))
  except Exception as err:
    raise Exception(f'''Could not get script directory path: {err}''')

scriptdir = get_script_dir

def join_names(*args):
  '''
    ## Description
    Join items to form a path.
    
    ## Usage
    
    ```python
    my_path = fs.join_names('C:/', 'Users', 'Me')
    ```

    ## Arguments
    - `args`: list of tokens to join
    
    ## Aliases
    `join_names`, `join`

    ## Returns
    Joined path as str.
  '''
  return(os.path.join(*args))

join = join_names

def is_abs_path(path):
  '''
    ## Description
    Is the specified path absolute?
    
    ## Usage
    
    ```python
    if fs.is_abs_path(path): print("Path is absolute.")
    ```

    ## Arguments
    - `path`: file or folder path as a string
    
    ## Aliases
    `is_abs_path`, `abs`

    ## Returns
    True if absolute path, else False.
  '''
  return(os.path.isabs(path))

isabs = is_abs_path

def is_file(path):
  '''
    ## Description
    Is specified path a file?
    
    ## Usage
    
    ```python
    if fs.is_file(path): print('{} is a file'.format(path))
    ```

    ## Arguments
    - `path`: file or folder path as a string
    
    ## Aliases
    `is_file`, `isfile`

    ## Returns
    True if a file, False otherwise.
  '''
  return(os.path.isfile(path))

isfile = is_file

def is_dir(path):
  '''
    ## Description
    Is specified path a directory?
    
    ## Usage
    
    ```python
    if fs.is_dir(path): print('{} is a file'.format(path))
    ```

    ## Arguments
    - `path`: file or folder path as a string
    
    ## Aliases
    `is_dir`, `isdir`

    ## Returns
    True if a directory, False otherwise.
  '''
  return(os.path.isdir(path))

isdir = is_dir

def get_abs_path(path, basepath=None):
  '''
    ## Description
    Get the absolute path.
    
    ## Usage
    
    ```python
    my_path = fs.get_abs_path(path)
    ```

    ## Arguments
    - `path`: file or folder path as a string
    - `basepath`: if specified, use this as the base path
    
    ## Aliases
    `get_abs_path`, `abs`

    ## Returns
    Absolute path as a str.
  '''
  try:
    if os.path.isabs(path): 
      return(os.path.normpath(path))
    if basepath is None:
      path = os.path.abspath(path)
      path = os.path.normpath(path)
      return(path)
    else:
      if not os.path.isabs(basepath): basepath = os.path.abspath(basepath)
      path = os.path.join(basepath, path)
      path = os.path.normpath(path)
      return(path)
  except Exception as err:
    raise Exception(f'''Could get absolute path for "{path}": {err}''')

abs = get_abs_path

def get_files(paths,regx=r'.*',rec=True,must_exist=True):
  '''
    ## Description
    Yield matching files in specified path(s) as generator object.
    
    ## Usage
    
    ```python
    # Iterator form
    for file in get_files(paths,regx,rec): print(file)
      
    # List form
    files = list(get_files(paths,regx,rec))
    ```

    ## Arguments
    - `path`: a single path of type str -OR- a list of paths each of type str
    - `regx`: regular expression matching file name (default = '.*')
    - `rec`: recursive files search if True (default = True).

    ## Aliases
    `get_files`, `files`
    
    ## Returns
    A generator object yielding full file names of type str.
  '''
  try:
    if not type(paths).__name__ == 'list': paths = [paths]
    for path in paths:
      if not dir_exists(path):
        if must_exist: raise Exception('Path \"{}\" does not exist'.format(path))
        else: continue
      for root, dirs, files in os.walk(path):
        dirs # Not used, included on line to remove lint error.
        for file in files:
          if not re.search(regx, file): continue
          yield(os.path.join(root,file))
        if not rec: break
  except Exception as err:
    raise Exception(f'''Could not get files for specified path(s): {paths}. {err}''')
  
files = get_files

def get_dirs(paths,regx=r'.*'):
  '''
    ## Description
    Yield matching directories in specified path(s) as generator object.
    
    ## Usage
    
    ```python
    ## Iterator form
    for dir_name in get_dirs(paths,regx): print(dir_name)
      
    ## List form
    dirs = list(get_dirs(paths,regx))
    ```

    ## Arguments
    - `path`: a single path of type str -OR- a list of paths each of type str
    - `regx`: regular expression matching dir name (default = '.*')

    ## Aliases
    `get_dirs`, `getdirs`, `dirs`
    
    ## Returns
    A generator object yielding full file names of type str.
  '''
  if not type(paths).__name__ == 'list': paths = [paths]
  for path in paths:
    for root, dirs, files in os.walk(path):
      files # Not used, included on line to remove lint error.
      for dir_name in dirs:
        if not re.search(regx, dir_name): continue
        yield(os.path.join(root,dir_name))
      break

getdirs = get_dirs
dirs = get_dirs

def create_dir(path, mode=0x775):
  '''
    ## Description
    Create directory (or directories) recursively.
    
    ## Usage
    
    ```python
    fs.create_dir(path, mode=0x755)
    ```

    ## Arguments
    - `path`: dir to create as str
    - `mode`: optional mode selection (default = 0x755)

    ## Aliases
    `create_dir`, `mkdir`
    
    ## Returns
    A printable string indicating status.
  '''
  try:
    if not dir_exists(path): 
      os.makedirs(path,mode)
      return("Created directory \"{}\".".format(path))
    else:
      return("Directory \"{}\" already exists.".format(path))
  except Exception as err:
    raise Exception(f'''Could create directory "{path}": {err}''')


mkdir = create_dir

def files_are_identical(file1, file2, rstrip=False):
  '''
    ## Description
    Compare two files returning True if identical, false otherwise.
    
    ## Usage
    
    ```python
    if fs.files_are_identical(file1, file2)
    ```

    ## Arguments
    - `file1`: first file
    - `file2`: second file
    - `rstrip`: strip spaces at the end of each line

    ## Aliases
    `files_are_identical`, `fsame`, `same`
    
    ## Returns
    True if identical, False otherwise.
  '''  
  try:
    if rstrip:
      if filecmp.cmp(file1, file2, shallow=False): return True
      lines1 = read_file(file1, to_string=True).rstrip().splitlines()
      lines2 = read_file(file2, to_string=True).rstrip().splitlines()
      if len(lines1) != len(lines2): return False
      for i in range(0, len(lines1)):
        if lines1[i].rstrip() != lines2[i].rstrip(): return False
      return True
    return (filecmp.cmp(file1, file2, shallow=False))
  except Exception as err:
    raise Exception(f'''Error comparing files "{file1}" and "{file2}": {err}''')

fsame = files_are_identical
same = files_are_identical

def copy_file(src, tar, create_dirs=False, meta=False):
  '''
    ## Description
    Copy a file.
    
    ## Usage
    
    ```python
    fs.copy_file(src, tar)
    ```

    ## Arguments
    - `src`: source file
    - `tar`: target file
    - `meta`: copy meta data and permissions

    ## Aliases
    `copy_file`, `fcopy`
    
    ## Returns
    A printable string indicating status.
  '''  
  try:
    dir = get_dir_name(tar)
    if create_dirs and not dir_exists(dir): create_dir(dir)
    if meta:
      shutil.copy(src, tar)
    else:
      shutil.copy2(src, tar)
    return("Copied file \"{}\" to \"{}\".".format(src, tar))
  except Exception as err:
    raise Exception(f'''Error trying to copy "{src}" to "{tar}": {err}''')

fcopy = copy_file

def copy_dir_if_changed(src, tar, omit=None, verbose=0, meta=False):
  '''
    ## Description
    Copy a dir.  Files are only copied if new or changed.
    
    ## Usage
    
    ```python
    fs.copy_dir_if_changed(src, tar)
    ```
    
    ## Arguments
    - `src`: source directory
    - `tar`: target directory
    - `omit`: will not copy file or dir mathing regular expression
    - `verbose`: verbose setting for printing (0=minimal to 3=maximum)
    - `meta`: copy meta data and permissions
    
    ## Aliases
    `copy_dir_if_changed`, `dcopy`

    ## Returns
    A printable string indicating status.

  '''
  try:
    if omit is None: omit = []
    if not type(omit) == list: omit = [omit]
    if not is_abs_path(src): src = os.path.join(get_script_dir(), src)
    if not is_abs_path(tar): tar = os.path.join(get_script_dir(), tar)
    info = {}
    info['files'] = {'omitted': 0, 'created': 0, 'updated': 0, 'identical': 0}
    info['dirs'] = {'omitted': 0, 'created': 0, 'exists': 0}
    target_base = get_dir_name(tar)
    results = []
    for root, dirs, files in os.walk(src):
      for isa, lst in zip(('dirs', 'files'), (dirs, files)):
        for name in lst:
          source = os.path.join(root,name)
          rel_source = get_rel_path(source, src)
          target = os.path.join(tar, rel_source)
          rel_target = get_rel_path(target, target_base)
          omitted = False
          for pattern in omit:
            if re.search(pattern, name): 
              omitted = True
              break
          if isa == 'dirs':
            # If the source directory matched item in omit list, don't create.
            if omitted: 
              msg = "Source directory \"{}\" not copied (matched omit pattern).".format(rel_source)
              if verbose > 1: print(msg)
              results.append(msg)
              info['dirs']['omitted'] += 1
              continue
            # If the target directory already exists, no need for additional action.
            if dir_exists(target):
              msg = "Target directory \"{}\" already exists.".format(rel_target)
              if verbose > 1: print(msg)
              results.append(msg)
              info['dirs']['exists'] += 1
              continue
            # All else, create the directory.
            else:
              create_dir(target)
              msg = "Created target directory \"{}\".".format(rel_target)
              if verbose > 1: print(msg)
              results.append(msg)
              info['dirs']['created'] += 1
              continue
          elif isa == 'files':
            # If the source file matched a pattern in the omit list, don't copy it. 
            if omitted: 
              msg = "Source file \"{}\" not copied (matched omit pattern).".format(rel_source)
              if verbose > 1: print(msg)
              results.append(msg)
              info['files']['omitted'] += 1
              continue
            # If the directory of the target file does not exit, the source directory matched a 
            # pattern in the omit list.  Don't copy the source file.
            if not dir_exists(get_dir_name(target)):
              msg = "Source file \"{}\" not copied (parent directory was omitted).".format(rel_source)
              if verbose > 1: print(msg)
              results.append(msg)
              info['files']['omitted'] += 1
              continue
            # If the file exists, check to see if update is necessary.
            if file_exists(target):
              # If the target file exists and is identical to the source file, don't copy.
              if files_are_identical(source, target):
                msg = "No change to target file \"{}\".".format(rel_target)
                if verbose > 1: print(msg)
                results.append(msg)
                info['files']['identical'] += 1
                continue
              # If the target file exists and is not identical to the source file, copy it.
              else:
                copy_file(source, target)
                msg = "Updated target file \"{}\".".format(rel_target)
                if verbose > 1: print(msg)
                results.append(msg)
                info['files']['updated'] += 1
                continue
            # If the target file does not exist, copy it.  
            else:
                copy_file(source, target)
                msg = "Created target file \"{}\".".format(rel_target)
                if verbose > 1: print(msg)
                results.append(msg)
                info['files']['created'] += 1
                continue
    msg = "Copy dir results: " + str(info)
    if verbose > 0: 
      if verbose > 1: print('---')
      print(msg)
    return '\n'.join(results)
  except Exception as err:
    raise Exception(f'''Error trying to copy "{src}" to "{tar}": {err}''')

dcopy = copy_dir_if_changed    

def copy_file_if_changed(src, tar, create_dirs=False, meta=False, rstat=True, simple=False):
  '''
    ## Description
    Copy a file only if it has been changed.
    
    ## Usage
    ```python
    fs.copy_file_if_changed(src, tar)
    ```

    ## Arguments
    - `src`: source file
    - `tar`: target file
    - `create_dir`: if True, create the target directory if it does not already exist
    - `meta`: copy meta data and permissions as well
    - `rstat`: if True, return status string; if False, return bool (True if copied, False otherwise)
    - `simple`: if True, return simple status string (e.g. "created", "identical", or "updated"); if False, return bool (True if copied, False otherwise)
    
    ## Aliases
    `copy_file_if_changed`, `fcopyif`

    ## Returns
    A printable string indicating status.
  '''
  try:
    dir = get_dir_name(tar)
    if create_dirs and not dir_exists(dir): create_dir(dir)
    if not file_exists(tar):
      if meta: shutil.copy(src, tar)
      else: shutil.copy2(src, tar)
      if rstat: 
        if simple: return("created")
        else: return("Copied file \"{}\" to \"{}\".".format(src, tar))
      else: return(True)
    elif files_are_identical(src, tar):
      if rstat:
        if simple: return("identical")
        else: return("Files \"{}\" and are \"{}\" identical.".format(src, tar))
      else: return(False)
    else:
      if meta: shutil.copy(src, tar)
      else: shutil.copy2(src, tar)
      if rstat:
        if simple: return("updated") 
        else: return("Updated file \"{}\" to \"{}\".".format(src, tar))
      else: return(True)
  except Exception as err:
    raise Exception(f'''Error trying to copy "{src}" to "{tar}": {err}''')

fcopyif = copy_file_if_changed

def get_size(path):
  '''
    ## Description
    Get size of path or file.
    
    ## Usage
    
    ```python
    size = fs.get_size(path)
    ```

    ## Arguments
    - `path`: file or directory path
    
    ## Aliases
    `get_size`, `size`

    ## Returns
    Size as int.
  '''  
  try:
    return(os.path.getsize(path))
  except Exception as err:
    raise Exception(f'''Could not get size of "{path}": {err}''')

size = get_size

def last_modified(path):
  '''
    ## Description
    Get last modified time stamp.
    
    ## Usage
    
    ```python
    ts = fs.last_modified(path)
    ```

    ## Arguments
    - `path`: file or directory path

    ## Aliases
    `last_modified`, `modified`
    
    ## Returns
    Time stamp as int.
  '''  
  try:
    return(os.path.getmtime(path))
  except Exception as err:
    raise Exception(f'''Could not read modification time of "{path}": {err}''')

modified = last_modified
