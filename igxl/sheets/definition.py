import re
import csv
from pprint import pprint as pprint
import fs
import sys

def get_col_index(cname):
    clist = list(cname)
    cnum = ord(clist.pop(-1)) - 65
    if len(clist) > 0: cnum += (ord(clist.pop(-1)) - 64) * 26
    return(cnum)

def get_col_name(cnum):
    cstr = str()
    div = cnum + 1 
    while div:
        (div, mod) = divmod(div - 1, 26)
        cstr = chr(mod + 65) + cstr
    return(cstr)

def qdata(val, null="''", type='dict-value', force=False):
    val = str(val)
    if len(val) == 0: return(null)
    quotes_needed = True
    while not force:
        if re.search(r'^\W', val): break
        if re.search(r'\s+$', val): break
        if re.search(r':', val): break
        if re.search(r'"', val): break
        if re.search(r'\'', val): break
        if type == 'list-value' and re.search(r'\W', val): break
        quotes_needed = False
        break
    if quotes_needed:
        if not type == 'list-value' and not(re.search(r'^-\d+$', val) or re.search(r'^-\d+\.\d+$', val)):
            val = re.sub(r'\'', '\'\'', val)
            val = "'" + val + "'"
    return(val)

class SheetDefinition:
    r'''
    Description
    -----------
    Base class sheet definition.

    Usage
    -----
    The following example illustrates how class SheetDefinition is used.  Say
    you have a DT worksheet definition "igxl\sheets\pinmap\2.1.py".

        from igxl.sheets.definition import StandardTable as SheetDefinition

    The StandardTable class inherits from SheetDefinition:

        class StandardTable(SheetDefinition):
          ...

    '''
    def reset(self):
        self.file_path = None
        self.data = {}
        self.num_header_rows = 0
        self.banner = None
        self.header = None
        self.header_template_data = []
        self.columns = []
        self.sheet_info_params = ['platform', 'toprow', 'leftcol', 'rightcol', 'tabcolor']
        self.header_params = {}
        self.header_macros = {}

    def initialize(self):
        def trim(value):
            value = re.sub(r'^\s*\n', '', value, count=1)
            value = re.sub(r'\s*$', '', value, count=1, flags=re.S)
            match_spaces = re.search(r'^ *', value)
            spaces = match_spaces.group(0) if match_spaces else None
            if spaces: value = re.sub(r'^' + spaces, '', value, count=0, flags=re.M)
            return(value)
        self.banner = trim(self.banner)
        self.header = trim(self.header)
        if 'Prefix' not in self.columns:
            self.columns.insert(0, 'Prefix')
            for i in range(10):
                self.columns.append('UserDefined' + str(i))
        rows = re.split(r'\n', self.header)
        self.num_header_rows = 0
        for row in csv.reader(rows, dialect='excel-tab'):
            self.header_template_data.append(row)
            self.num_header_rows += 1
            c = 0
            for cell in row:
                m = re.search(r'^\s*\$\{\s*(\w+)\s*\}\s*$', cell)
                if m: self.header_params[m.group(1)] = [self.num_header_rows - 1, c]
                m = re.search(r'^\s*\$(\w+)\s*$', cell)
                if m: self.header_params[m.group(1)] = [self.num_header_rows - 1, c]
                m = re.search(r'^\s*\@\{\s*(\w+)\s*\}\s*$', cell)
                if m: self.header_macros[m.group(1)] = [self.num_header_rows - 1, c]
                m = re.search(r'^\s*\@(\w+)\s*$', cell)
                if m: self.header_macros[m.group(1)] = [self.num_header_rows - 1, c]
                c += 1

    def initialize_data(self):
        self.data = {}
        self.data['Info'] = {}
        self.data['Info']['File'] = fs.get_file_name(self.file_path)
        self.data['Info']['Variables'] = {}
        self.data['Info']['SheetParams'] = {}
        self.data['Info']['Comment'] = ''
        self.data['Data'] = []

    def parse_first_row(self, row):
        params = row[0]
        m = re.search(r'^(\w+)', params)
        if not m: raise Exception("Worksheet type not defined.")
        self.data['Info']['Type'] = m.group(1)
        m = re.search(r'version=(\d+\.\d+)', params)
        if not m: raise Exception("Worksheet version not defined.")
        self.data['Info']['Version'] = float(m.group(1))
        params = re.sub(r'^.*?:(.*)\s*$', r'\g<1>', params)
        for token in re.split(r':', params):
            m = re.search(r'^(.*?)=(.*)$', token)
            if m: self.data['Info']['SheetParams'][m.group(1)] = m.group(2)
        self.data['Info']['Name'] = row[1]

    def parse_header_rows(self, header):
        # Extra variable values from the header.
        for name, coord in self.header_params.items():
            if coord[1] < len(header[coord[0]]): self.data['Info']['Variables'][name] = header[coord[0]][coord[1]]
            else: self.data['Info']['Variables'][name] = ''
        # If the 'Sites' macros is defined, do site processing.
        if 'Sites' in self.header_macros:
            site_columns = []
            sites = []
            # Get the first site column row and column index in the header.
            r, c = int(self.header_macros['Sites'][0]), int(self.header_macros['Sites'][1])
            # Cycle through site column names in the header ...
            m = re.search(r'^(Site\s*(\d+))$', header[r][c])
            while m:
                col_name = m.group(1)
                site = m.group(2)
                sites.append(site)
                field_name = col_name
                field_name = re.sub(r'\s+', '', field_name)
                site_columns.append(field_name)
                m = None
                c += 1
                if c < len(header[r]): m = re.search(r'^(Site\s*(\d+))$', header[r][c])
            i = None
            if '@{Sites}' in self.columns: i = self.columns.index('@{Sites}')
            elif '@Sites' in self.columns: i = self.columns.index('@Sites')
            elif 'Site0' not in self.columns or 'Site1' not in self.columns: raise Exception("Expected \"@{Sites}\" or \"@Sites\" macro entry in \"columns\" list of file " + "\"{}\"".format(self.file_path))
            if i:
                new_columns = self.columns[0:i] + site_columns + self.columns[i + 1:]
                self.columns = new_columns
            self.data['Info']['Sites'] = sites
        # If the 'Categories' macros is defined, do specsheet processing.
        if 'Categories' in self.header_macros:
            categories = []
            selectors = []
            columns = []
            category = None
            selector_columns = []
            selector_name = {}
            # Get the first site column row and column index in the header.
            r, c = int(self.header_macros['Categories'][0]), int(self.header_macros['Categories'][1])
            while c < len(header[r + 1]) and len(header[r + 1][c]) > 0 and not(header[r + 1][c] == 'Comment'):
                if c < len(header[r]) and len(header[r][c]) > 0:
                    category = header[r][c]
                    categories.append(category)
                selector = header[r + 1][c]
                selector_columns.append(selector)
                if selector not in selectors: selectors.append(selector)
                column = "." + category + "." + selector
                columns.append(column)
                c += 1
            i = None
            if '@{Columns}' in self.columns: i = self.columns.index('@{Columns}')
            elif '@Columns' in self.columns: i = self.columns.index('@Columns')
            else: raise Exception("Expected \"@{Columns}\" or \"@Columns\" macro entry in \"columns\" list of file " + "\"{}\"".format(self.file_path))
            new_columns = self.columns[0:i] + columns + self.columns[i + 1:]
            self.columns = new_columns
            self.data['Info']['Categories'] = categories
            self.data['Info']['Selectors'] = selectors

    def update_ref(self, m, r):
        ref = m.group(0)
        cref = m.group(1)
        rnum = m.group(2)
        # If ref starts with "!" then the cell references a cell in another sheet
        # and cannot be processed.  Simply return the ref.
        if not self.allow_refs or ref.startswith("!"): return(ref)
        cnum = get_col_index(cref)
        if cnum < len(self.columns):
            cname = self.columns[cnum]
            if rnum == str(r): return("$" + cname)
            else: return("$" + cname + "." + rnum)
        else:
            return(ref)

    def replace_ref(self, m, id, id_to_row):
        ref = m.group(1)
        if not m.group(3) == None: id = m.group(3)
        r = id_to_row[id]
        if ref not in self.columns: raise Exception("Reference variable \"${}\" does not match any known column.  Must be one of: {}".format(cname,str(self.columns)))
        i = self.columns.index(ref)
        cname = get_col_name(i) + str(r)
        return(cname)

    def write_yml_top(self, fh):
        fh.write(self.banner + "\n")
        fh.write("---\n")
        fh.write('Info:\n')
        fh.write('  File: ' + qdata(self.data['Info']['File']) + '\n')
        fh.write('  Name: ' + qdata(self.data['Info']['Name']) + '\n')
        fh.write('  Type: ' + qdata(self.data['Info']['Type']) + '\n')
        fh.write('  Version: ' + qdata(self.data['Info']['Version']) + '\n')
        # Print SheetParams.
        fh.write('  SheetParams:' + str(' []' if len(self.data['Info']['SheetParams']) == 0 else '') + '\n')
        for key in self.sheet_info_params:
            if key in self.data['Info']['SheetParams']:
                val = self.data['Info']['SheetParams'][key]
                fh.write('    ' + key + ': ' + qdata(val) + "\n")
        # Print header Variables.
        fh.write('  Variables:' + str(' []' if len(self.data['Info']['Variables']) == 0 else '') + '\n')
        for key, val in self.data['Info']['Variables'].items():
            fh.write('    ' + key + ': ' + qdata(val) + "\n")
        # Print site data (if applicable)
        if 'Sites' in self.data['Info']:
            fh.write('  Sites: [' + ",".join(self.data['Info']['Sites']) + ']\n')
        # Print Categories (if applicable).
        if 'Categories' in self.data['Info']:
            fh.write('  Categories:' + str(' []' if len(self.data['Info']['Categories']) == 0 else '') + '\n')
            for val in self.data['Info']['Categories']:
                fh.write('    - ' + qdata(val) + '\n')
        # Print Selectors (if applicable).
        if 'Symbols' in self.data['Info']:
            fh.write('  Symbols:' + str(' []' if len(self.data['Info']['Symbols']) == 0 else '') + '\n')
            for val in self.data['Info']['Symbols']:
                fh.write('    - ' + qdata(val) + '\n')
        # Print Selectors (if applicable).
        if 'Selectors' in self.data['Info']:
            fh.write('  Selectors:' + str(' []' if len(self.data['Info']['Selectors']) == 0 else '') + '\n')
            for val in self.data['Info']['Selectors']:
                fh.write('    - ' + qdata(val) + '\n')
        # Print SelectorNames (if applicable).
        if 'SelectorNames' in self.data['Info']:
            fh.write('  SelectorNames:' + str(' {}' if not(bool(self.data['Info']['SelectorNames'])) else '') + '\n')
            for key in self.data['Info']['Selectors']:
                fh.write('    {}: {}\n'.format(key, qdata(self.data['Info']['SelectorNames'][key])))
        # Print comment (if defined)
        if 'Comment' in self.data['Info']:
            fh.write('  Comment: ' + qdata(self.data['Info']['Comment']) + '\n')

    def write_txt_top(self, fh):
        header = self.header
        sheet_info = self.data['Info']['Type'] + ",version=" + str(self.data['Info']['Version'])
        for key in self.sheet_info_params:
            if key in self.data['Info']['SheetParams'] and len(str(self.data['Info']['SheetParams'][key])) > 0:
                sheet_info += ":" + key + "=" + str(self.data['Info']['SheetParams'][key])
        header = re.sub(r'\@\{\s*SheetInfo\s*\}',sheet_info,header)
        header = re.sub(r'\@SheetInfo\b',sheet_info,header)
        header = re.sub(r'\@\{\s*SheetName\s*\}',self.data['Info']['Name'],header)
        header = re.sub(r'\@SheetName\b',self.data['Info']['Name'],header)
        if 'Variables' in self.data['Info']:
            for var in self.data['Info']['Variables']:
                header = re.sub(r'\$\{\s*' + var + r'\s*\}',self.data['Info']['Variables'][var],header)
                header = re.sub(r'\$' + var + r'\b',self.data['Info']['Variables'][var],header)
        header = re.sub(r'\$\{\s*\w+\s*\}','',header)
        header = re.sub(r'\$\w+\b','',header)
        if re.search(r'\@Sites',header) or re.search(r'\@\{\s*Sites\s*\}',header):
            cols = 'Site ' + '\tSite '.join(self.data['Info']['Sites'])
            header = re.sub(r'\@\{\s*Sites\s*\}',cols,header)
            header = re.sub(r'\@Sites\b',cols,header)
            i = None
            if '@{Sites}' in self.columns: i = self.columns.index('@{Sites}')
            elif '@Sites' in self.columns: i = self.columns.index('@Sites')
            elif 'Site0' not in self.columns or 'Site1' not in self.columns: raise Exception("Expected \"@{Sites}\" or \"@Sites\" macro or \"Site0\" token in \"columns\" list of file " + "\"{}\": {}".format(self.file_path,str(self.columns)))
            if i:
                site_columns = []
                for site in self.data['Info']['Sites']:
                    site_columns.append("Site {}".format(site))
                new_columns = self.columns[0:i] + site_columns + self.columns[i + 1:]
        fh.write(header)
        if 'Prefix' not in self.columns:
            self.columns.insert(0, 'Prefix')
            for i in range(10):
                self.columns.append('UserDefined' + str(i))
        fh.write("\n")

class StandardTable(SheetDefinition):
    def read_txt_file(self, file):
        # Initialize variables.
        self.file_path = fs.get_abs_path(file)
        r = 0
        # Define internal function update_ref(). Uses nonlocal variable r which
        # identifies the row number.
        def update_ref(m): nonlocal r; return(self.update_ref(m, r))
        # Initialize self.data dictionary values.
        self.initialize_data()
        # Parse self.file_path file ...
        with open(self.file_path, newline='') as csv_file_object:
            csv_file_stream = csv.reader(csv_file_object, dialect='excel-tab')
            r = 0  # Initialize row counter to 0
            header = []  # Header data (e.g. header[r][c])
            # Cycle through rows in the file stream ...
            for row in csv_file_stream:
                # Start row index is 1 (not 0).
                r += 1
                # Process header rows ...
                if r <= self.num_header_rows:
                    if r == 1: self.parse_first_row(row)
                    header.append(row)
                    if r == self.num_header_rows: self.parse_header_rows(header)
                    continue
                # If cell is a formula (i.e. beings with "="), replace cell references
                # with explicit nomenclature.  For example, "G175" -> "$DriveData.175"
                # (assuming column "G" is "DriveData").  If the cell references
                # another cell on the same line, the form can be further truncated to
                # "$DriveData".
                for i, cell in enumerate(row):
                    row[i] = str(cell)
                    if cell.startswith('='):
                        row[i] = re.sub(r'\b(\!{0,1}[a-zA-Z]{1,2})(\d+)\b', update_ref, cell)
                # Create a dictionary object out of the row and append this to the
                # self.data list.
                d = dict(zip(self.columns, row))
                d['ID'] = r
                self.data['Data'].append(d)
        if 'modify_data' in dir(self): self.modify_data()

    def to_yaml(self, file=""):
        fh = sys.stdout
        if file: fh = open(file, "w")
        self.write_yml_top(fh)
        self._to_yaml_data(fh)
        if file: fh.close()

    to_yml = to_yaml

    def _to_yaml_data(self, fh):
        fh.write('Data:' + str(' []' if len(self.data['Data']) == 0 else '') + '\n')
        for hash in self.data['Data']:
            fh.write("- ID: {}\n".format(hash['ID']))
            for col in self.columns:
                if col in hash:
                    fh.write("  {}: {}\n".format(col, qdata(hash[col],force=True)))
        fh.write("\n")

    def to_txt(self, file=""):
        fh = sys.stdout
        if file: fh = open(file, "w")
        self.write_txt_top(fh)
        self._to_txt_data(fh)
        if file: fh.close()
        
    def _to_txt_data(self, fh):
        id = '0'
        id_to_row = {}
        r = self.num_header_rows
        def replace_ref(m): nonlocal id; nonlocal id_to_row; return(self.replace_ref(m, id, id_to_row))
        # need to cycle through data and make ID to row dict to be used 
        # in fixing refs.
        if self.allow_refs:
            r = self.num_header_rows
            for hash in self.data['Data']:
                r += 1
                if 'ID' not in hash: raise Exception("ID not defined for file \"{}\".".format(self.file_path))
                id = str(hash['ID'])
                id_to_row[id] = r
        for hash in self.data['Data']:
            id = str(self.num_header_rows)
            if 'ID' in hash: id = str(hash['ID'])
            cells = []
            for col in self.columns:
                val = ''
                if col in hash: val = hash[col]
                if self.allow_refs and val.startswith("="):
                    val = re.sub(r'\$(\w+)(\.(\w+)){0,1}\b', replace_ref, val)
                cells.append(val)
            line = "\t".join(cells)
            line = re.sub(r'\s*$','',line)
            # line += "\t"  ### ADD THIS IN LATER !!!
            fh.write(line + "\n")


class Spec2Table(StandardTable):

    def modify_data(self):
        self.data['Info']['Symbols'] = []
        self.data['Info']['SelectorNames'] = {}
        i = 0
        data = {}
        meta = {}
        for hash in self.data['Data']:
            self.data['Info']['SelectorNames'][hash['SelectorVal']] = hash['SelectorName']
            symbol = hash['Symbol']
            if symbol not in self.data['Info']['Symbols']:
                self.data['Info']['Symbols'].append(symbol)
            if symbol not in meta:
                meta[symbol] = {}
                if 'Prefix' in hash: meta[symbol]['Prefix'] = hash['Prefix']
                if 'Comment' in hash: meta[symbol]['Comment'] = hash['Comment']
            for key, val in hash.items():
                m = re.search(r'^\.(.*?)\.(.*?)$', key)
                if m:
                    category = m.group(1)
                    selector = m.group(2)
                    if category not in data: data[category] = {}
                    if symbol not in data[category]: data[category][symbol] = {}
                    data[category][symbol][selector] = val
        self.data['Data'] = \
        {
           'Category': data,
           'Meta': meta
        }
        # print(self.data['Data']['Meta'])

    def _to_yaml_data(self, fh):
        r = self.num_header_rows
        fh.write('Data:' + str(' {}' if len(self.data['Data']) == 0 else '') + '\n')
        fh.write('  Category:' + str(' {}' if len(self.data['Data']['Category']) == 0 else '') + '\n')
        for category in sorted(self.data['Data']['Category'], key=lambda t: t.lower()):
            fh.write("    {}:\n".format(qdata(category)))
            for symbol in self.data['Info']['Symbols']:
                fh.write("      {}:\n".format(qdata(symbol)))
                for selector in self.data['Info']['Selectors']:
                    if selector in self.data['Data']['Category'][category][symbol]:
                        fh.write("        {}: {}\n".format(qdata(selector), qdata(self.data['Data']['Category'][category][symbol][selector])))
        meta_array = []
        for symbol in self.data['Info']['Symbols']:
            symbol_array = []
            if 'Prefix' in self.data['Data']['Meta'][symbol] and len(self.data['Data']['Meta'][symbol]['Prefix']) > 0:
                symbol_array.append('Prefix: ' + qdata(self.data['Data']['Meta'][symbol]['Prefix']))
            if 'Comment' in self.data['Data']['Meta'][symbol] and len(self.data['Data']['Meta'][symbol]['Comment']) > 0:
                symbol_array.append('Comment: ' + qdata(self.data['Data']['Meta'][symbol]['Comment']))
            if len(symbol_array) > 0: meta_array.append(qdata(symbol) + ": {" + ", ".join(symbol_array) + "}")
        fh.write('  Meta:' + str(' {}' if len(meta_array) == 0 else '') + '\n')
        for symbol_string in sorted(meta_array, key=lambda t: t.lower()):
            fh.write('    ' + symbol_string + '\n')
        fh.write("\n")

