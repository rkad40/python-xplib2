'''
# `fs`
A plethora of file system functions.

## Usage
```
import fs
```
'''

import os, sys, re, filecmp, shutil, time

def open_file(path, mode='r', encoding="utf8"):
  '''
    ## Description
    Open a file.
    
    ## Usage
    ```
    fstream = fs.open_file(file_path)
    ```
    
    ## Arguments
    - `path`: file as str
    - `mode='r'`: 'r' for read, 'w' for write
    - `encoding='utf8'`: encoding
    
    ## Returns
    file stream (use `close()` to close when done)
  '''
  f = open(path, mode, encoding)
  return f

def read_file(path, to_string = False, encoding="utf8"):
  '''
    ## Description
    Read file and return a list of lines.
    
    ## Usage
    ```
    my_lines = fs.read_file(path)
    ```
    
    ## Arguments
    - `path`: file as str
    - `to_string`: optional bool; if True return content as a string
    - `encoding='utf8'`: encoding
    
    ## Returns
    list of lines each of typ str (or a single string if to_string is True)
  '''
  f = open(path, 'r', encoding="utf8")
  if to_string:
    return("".join(f.readlines()))
  else:
    return(f.readlines())

def write_file(path, content):
  '''
    ## Description
    Write content to file.
    
    ## Usage
    ```
    fs.write_file(path, content)
    ```

    ## Arguments
    - `path`: file as str
    - `content`: str or list data to write to file
    
    ## Returns
    nothing
  '''  
  f = open(path, 'w')
  if type(content) == str:
    f.write(content)
  elif type(content) == list:
    f.writelines(content)
  else:
    raise Exception('Invalid content of type "{}"; must be "str" or "list".'.format(type(content).__name__))

def delete_file(path):
  '''
    ## Description
    Delete a file.
    
    ## Usage
    ```
    fs.delete_file(path)
    ```

    ## Arguments
    - `path`: file as str
    
    ## Returns
    nothing
  '''  
  os.remove(path)

def delete_dir(path):
  '''
    ## Description
    Delete a directory.
    
    ## Usage
    ```
    fs.delete_dir(path)
    ```

    ## Arguments
    - `path`: directory as str
    
    ## Returns
    nothing
  '''  
  shutil.rmtree(path)

def write_file_if_changed(path, content, create_dir=True, mode=None):
  '''
    ## Description
    Write a file only if it results in a change.
    
    ## Usage
    ```
    fs.write_file_if_changed(path, content)
    ```

    ## Arguments
    - `path`: file as str
    - `content`: content to write to file
    - `create_dir`: create base dir if it does not already exist (default = True)
    - `mode`: assert file mode (default = None)  
    
    ## Returns
    A string indicating the action that was performed.
  '''  
  dir_name = get_dir_name(path)
  if create_dir == True and not dir_exists(dir_name): 
    dir_mode = mode if mode is not None else 0x755
    os.makedirs(dir_name, dir_mode)
  if not dir_exists(dir_name): 
    raise Exception('Cannot write file "{}"; base directory "{}" does not exist.'.format(path, dir_name))
  if not file_exists(path):
    write_file(path, content)
    if mode is not None: os.chmod(path, mode)
    return('Created new file "{}".'.format(path))
  else:
    temp_file = join_names(get_dir_name(path), '.' + get_root_name(path) + '-' + str(time.time()) + '.' + get_ext(path))
    write_file(temp_file, content)
    if files_are_identical(temp_file, path):
      delete_file(temp_file)
      return('No change to file "{}".'.format(path))
    else:
      shutil.move(temp_file, path)
      return('Upated file "{}".'.format(path))

def rename_file(orig_file, new_file):
  '''
    ## Description
    Rename or move a file.
    
    ## Usage
    ```
    fs.rename_file(orig_file, new_file)
    ```

    ## Arguments
    - `orig_file`: original file
    - `new_file`: new file
    
    ## Returns
    New file name.
  '''
  shutil.move(orig_file, new_file)
  return(new_file)

def get_file_name(path):
  '''
    ## Description
    Get the base file name.
    
    ## Usage
    ```
    file_name = fs.get_file_name(path)
    ```

    ## Arguments
    - `path`: file as str
    
    ## Returns
    Base file name as str.
  '''
  rval = os.path.basename(path)
  return(rval)
  
def get_root_name(path):
  '''
    ## Description
    Get the root file name.
    
    ## Usage
    ```
    root_name = fs.get_root_name(path)
    ```

    ## Arguments
    - `path`: file as str
    
    ## Returns
    Root file name as str (i.e. `fs.get_file_name()` minus extension).
  '''
  rval = get_file_name(path)
  rval = os.path.splitext(rval)[0]
  return(rval)

def append_root_name(path, val):
  '''
    ## Description
    Append val to the file root name (before the extension).
    
    ## Usage
    ```
    orig_file = '/home/files/test.txt'
    temp_file = fs.append_root_name(orig_file, '-temp')
    # now temp_file = 'home/files/test-temp.txt'
    ```

    ## Arguments
    - `path`: file as str
    - `val`: token to append to root name
    
    ## Returns
    File name as string.
  '''
  dir = get_dir_name(path)
  name = get_file_name(path)
  root = get_root_name(name)
  ext = get_ext(name)
  rval = join_names(dir, root + val + '.' + ext)
  return(rval)
  
def remove_ext(path):
  '''
    ## Description
    Remove the extension from file name.
    
    ## Usage
    ```
    file_name = fs.get_ext(path)
    ```

    ## Arguments
    - `path`: file as str
    
    ## Returns
    Path minus file extension as str.
  '''
  rval = path
  rval = re.sub(r'\.\w+$','',rval)
  return(rval)

def get_ext(path):
  '''
    ## Description
    Get the file extension.
    
    ## Usage
    ```
    ext = fs.get_ext(path)
    ```

    ## Arguments
    - `path`: file as str
    
    ## Returns
    File extension as str in lower case.
  '''
  rval = path
  m = re.search(r'\.(\w+)$',rval)
  ext = m.group(1) if m else ""
  ext = ext.lower()
  return(ext)

def get_dir_name(path,count=1):
  '''
    ## Description
    Get dir name.
    
    ## Usage
    ```
    dir = fs.get_dir_name(path)
    ```

    ## Arguments
    - `path`: file as str
    - `count`: depth (default = 1)
    
    ## Returns
    Dir name as string.
  '''
  path = get_abs_path(path)
  while count > 0:
    path = os.path.dirname(path)
    count -= 1
  return(path)
  
def fix_path_name(*path):
  '''
    ## Description
    Fix path name (render as Windows path).
    
    ## Usage
    ```
    dir = fs.fix_path_name(path)
    ```

    ## Arguments
    - `path`: path as str tuple (e.g. 'C:', 'users/me')
    
    ## Returns
    Windows style path as str.
  '''
  path = '/'.join(path)
  if sys.platform == 'win32': path = re.sub(r'/', r'\\', path)
  else : path = re.sub(r'\\', r'/', path)
  path = os.path.normpath(path)
  return(path)

def get_unix_path(path):
  '''
    ## Description
    Get the UNIX / Linux style path.
    
    ## Usage
    ```
    my_path = fs.get_unix_path(some_path)
    ```

    ## Arguments
    - `path`: file or folder path as str
    
    ## Returns
    Absolute path as str.
  '''
  path = re.sub(r'\\', r'/', path)
  return(path)

def file_exists(path):
  '''
    ## Description
    Test if file exists.
    
    ## Usage
    ```
    if fs.file_exists('C:/Data/Last.txt'): # Do something
    ```

    ## Arguments
    - `path`: file path
    
    ## Returns
    True if file exists, False otherwise.
  '''
  return(os.path.exists(path))

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
    
    ## Returns
    True if dir exists, False otherwise.
  '''
  return(os.path.exists(path))

def get_rel_path(abs_path, base_path):
  '''
    ## Description
    Get the relative path.
    
    ## Usage
    ```
    my_path = fs.get_rel_path(long_path, base_path)
    ```

    ## Arguments
    - `abs_path`: absolute path to be converted into relative path
    - `base_path`: base path from which the relative path begins
    
    ## Returns
    Relative path as a str.
  '''
  if is_file(base_path): base_path = get_dir_name(base_path)
  return(os.path.relpath(abs_path, base_path))

def get_app_data_path(abs_path, base_path):
  '''
    ## Description
    Get app data path %APPDATA%.
    
    ## Usage
    ```
    app_data_path = fs.get_app_data_path()
    ```
    ## Returns
    absolute path to %APPDATA%
  '''
  return(get_abs_path(os.getenv('APPDATA')))

def get_cwd():
  '''
    ## Description
    Get current working directory.
    
    ## Usage
    ```
    my_path = fs.get_cwd()
    ```
    
    ## Returns
    Absolute path as a str.
  '''
  return(os.getcwd())

def change_dir(dir_path):
  '''
    ## Description
    Change directory.
    
    ## Usage
    ```
    fs.change_dir(dir_path)
    ```

    ## Returns
    nothing
  '''
  return(os.chdir(dir_path))

def get_script_file():
  '''
    ## Description
    Get current script file being executed.
    
    ## Usage
    ```
    this_script = fs.get_script_file()
    ```

    ## Returns
    Absolute path to current script file.
  '''
  script_file = sys.argv[0]
  if not is_abs_path(script_file): script_file = get_abs_path(script_file)
  return(script_file)

def get_script_dir():
  '''
    ## Description
    Get directory of the current script file being executed.
    
    ## Usage
    ```
    script_dir = fs.get_script_dir()
    ```

    ## Returns
    Absolute path to current script file directory.
  '''
  return(get_dir_name(get_script_file()))

def join_names(*args):
  '''
    ## Description
    Join items to form a path.
    
    ## Usage
    ```
    my_path = fs.join_names('C:/', 'Users', 'Me')
    ```

    ## Arguments
    - `args`: list of tokens to join
    
    ## Returns
    Joined path as str.
  '''
  return(os.path.join(*args))

def is_abs_path(path):
  '''
    ## Description
    Is the specified path absolute?
    
    ## Usage
    ```
    if fs.is_abs_path(path): print("Path is absolute.")
    ```

    ## Arguments
    - `path`: file or folder path as a string
    
    ## Returns
    True if absolute path, else False.
  '''
  return(os.path.isabs(path))

def is_file(path):
  '''
    ## Description
    Is specified path a file?
    
    ## Usage
    ```
    if fs.is_file(path): print('{} is a file'.format(path))
    ```

    ## Arguments
    - `path`: file or folder path as a string
    
    ## Returns
    True if a file, False otherwise.
  '''
  return(os.path.isfile(path))

def is_dir(path):
  '''
    ## Description
    Is specified path a directory?
    
    ## Usage
    ```
    if fs.is_dir(path): print('{} is a file'.format(path))
    ```

    ## Arguments
    - `path`: file or folder path as a string
    
    ## Returns
    True if a directory, False otherwise.
  '''
  return(os.path.isdir(path))

def get_abs_path(path, relpath=None):
  '''
    ## Description
    Get the absolute path.
    
    ## Usage
    ```
    my_path = fs.get_abs_path(path)
    ```

    ## Arguments
    - `path`: file or folder path as a string
    
    ## Returns
    Absolute path as a str.
  '''
  if os.path.isabs(path): 
    return(os.path.normpath(path))
  if relpath is None:
    path = os.path.abspath(path)
    path = os.path.normpath(path)
    return(path)
  else:
    if not os.path.isabs(relpath): relpath = os.path.abspath(relpath)
    # if not os.path.isdir(path): relpath = os.path.dirname(relpath)
    path = os.path.join(relpath, path)
    path = os.path.normpath(path)
    return(path)

def get_files(paths,regx=r'.*',rec=True,must_exist=True):
  '''
    ## Description
    Yield matching files in specified path(s) as generator object.
    
    ## Usage
    ```
    # Iterator form
    for file in get_files(paths,regx,rec): print(file)
      
    # List form
    files = list(get_files(paths,regx,rec))
    ```

    ## Arguments
    - `path`: a single path of type str -OR- a list of paths each of type str
    - `regx`: regular expression matching file name (default = '.*')
    - `rec`: recursive files search if True (default = True).
    
    ## Returns
    A generator object yielding full file names of type str.
  '''
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

def get_dirs(paths,regx=r'.*'):
  '''
    ## Description
    Yield matching directories in specified path(s) as generator object.
    
    ## Usage
    ```
    ## Iterator form
    for dir_name in get_dirs(paths,regx): print(dir_name)
      
    ## List form
    dirs = list(get_dirs(paths,regx))
    ```

    ## Arguments
    - `path`: a single path of type str -OR- a list of paths each of type str
    - `regx`: regular expression matching dir name (default = '.*')
    
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

def create_dir(path, mode=0x775):
  '''
    ## Description
    Create directory (or directories) recursively.
    
    ## Usage
    ```
    fs.create_dir(path, mode=0x755)
    ```

    ## Arguments
    - `path`: dir to create as str
    - `mode`: optional mode selection (default = 0x755)
    
    ## Returns
    A printable string indicating status.
  '''
  if not dir_exists(path): 
    os.makedirs(path,mode)
    return("Created directory \"{}\".".format(path))
  else:
    return("Directory \"{}\" already exists.".format(path))

def files_are_identical(file1, file2):
  '''
    ## Description
    Compare two files returning True if identical, false otherwise.
    
    ## Usage
    ```
    if fs.files_are_identical(file1, file2)
    ```

    ## Arguments
    - `file1`: first file
    - `file2`: second file
    
    ## Returns
    True if identical, Falser otherwise.
  '''  
  return (filecmp.cmp(file1, file2, shallow=False))

def copy_file(src, tar, create_dirs=False, meta=False):
  '''
    ## Description
    Copy a file.
    
    ## Usage
    ```
    fs.copy_file(src, tar)
    ```

    ## Arguments
    - `src`: source file
    - `tar`: target file
    - `meta`: copy meta data and permissions
    
    ## Returns
    A printable string indicating status.
  '''  
  dir = get_dir_name(tar)
  if create_dirs and not dir_exists(dir): create_dir(dir)
  if meta:
    shutil.copy(src, tar)
  else:
    shutil.copy2(src, tar)
  return("Copied file \"{}\" to \"{}\".".format(src, tar))

def copy_dir_if_changed(src, tar, omit=None, verbose=1, meta=False):
  '''
    ## Description
    Copy a dir.  Files are only copied if new or changed.
    
    ## Usage
    ```
    fs.copy_dir_if_changed(src, tar)
    ```
    ## Arguments
    - `src`: source directory
    - `tar`: target directory
    - `omit`: will not copy file or dir mathing regular expression
    - `verbose`: verbose setting for printing (0=minimal to 3=maximum)
    - `meta`: copy meta data and permissions
    
    ## Returns
    A printable string indicating status.

  '''
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
  msg = "Results: " + str(info)
  if verbose > 0: 
    if verbose > 1: print('---')
    print(msg)
  return '\n'.join(results)
    

def copy_file_if_changed(src, tar, create_dirs=False, meta=False, rstat=True):
  '''
    ## Description
    Copy a file only if it has been changed.
    
    ## Usage
    ```
    fs.copy_file_if_changed(src, tar)
    ```

    ## Arguments
    - `src`: source file
    - `tar`: target file
    - `create_dir`: if True, create the target directory if it does not already exist
    - `meta`: copy meta data and permissions as well
    - `rstat`: if True, return status string; if False, return bool (True if copied, False otherwise)
    
    ## Returns
    A printable string indicating status.
  '''
  dir = get_dir_name(tar)
  if create_dirs and not dir_exists(dir): create_dir(dir)
  if not file_exists(tar):
    if meta: shutil.copy(src, tar)
    else: shutil.copy2(src, tar)
    if rstat: return("Copied file \"{}\" to \"{}\".".format(src, tar))
    else: return(True)
  elif files_are_identical(src, tar):
    if rstat: return("Files \"{}\" and are \"{}\" identical.".format(src, tar))
    else: return(False)
  else:
    if meta: shutil.copy(src, tar)
    else: shutil.copy2(src, tar)
    if rstat: return("Updated file \"{}\" to \"{}\".".format(src, tar))
    else: return(True)

def get_size(path):
  '''
    ## Description
    Get size of path or file.
    
    ## Usage
    ```
    size = fs.get_size(path)
    ```

    ## Arguments
    - `path`: file or directory path
    
    ## Returns
    Size as int.
  '''  
  return(os.path.getsize(path))

def last_modified(path):
  '''
    ## Description
    Get last modified time stamp.
    
    ## Usage
    ```
    ts = fs.last_modified(path)
    ```

    ## Arguments
    - `path`: file or directory path
    
    ## Returns
    Time stamp as int.
  '''  
  return(os.path.getmtime(path))
