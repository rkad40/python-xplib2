r'''
Create a text based data table.  

```python
data = [
dict(name="Mercury", diameter="5000", distance="60", year="0.24", day="1400", comment="Closest to the sun."),
dict(name="Venus", diameter="12000", distance="110", year="0.60", day="5800", comment="Hottest planet."),
dict(name="Earth", diameter="12800", distance="150", year="1", day="24", comment="Our home world."),
dict(name="Mars", diameter="7000", distance="230", year="2", day="25", comment="Most Earth-like planet."),
dict(name="Jupiter", diameter="140000", distance="780", year="12", day="10", comment="Largest planet."),
dict(name="Saturn", diameter="120000", distance="1400", year="30", day="10", comment="Has a large ring system."),
dict(name="Uranus", diameter="52000", distance="2900", year="84", day="17", comment="Has a ring system but not as prominent as Saturn's."),
dict(name="Neptune", diameter="50000", distance="4500", year="160", day="16", comment="Officially the planet farthest from the sun."),
dict(name="Pluto", diameter="3000", distance="6000", year="250", day="150", comment="No longer considered a planet."),
]

t = Table(title='The Planets')
t.add_col('Name', key='name', width=0.2)
t.add_col('Diameter (km)', key='diameter', justify='center', width=0.1)
t.add_col('Distance from Sun (km)', justify='center', key='distance', width=0.1)
t.add_col('Orbit (year)', key='year', justify='center', width=0.1)
t.add_col('Day (hours)', key='day', justify='center', width=0.1)
t.add_col('Comment', key='comment', width=0.4)
for row in data:
    t.add_row(row)
print(t.render())
```

This prints:

```
╔═══════════════════╤══════════╤══════════╤══════════╤══════════╤════════════════════════════════════╗
║ Name              │ Diameter │ Distance │  Orbit   │   Day    │ Comment                            ║
║                   │   (km)   │ from Sun │  (year)  │ (hours)  │                                    ║
║                   │          │   (km)   │          │          │                                    ║
╟───────────────────┼──────────┼──────────┼──────────┼──────────┼────────────────────────────────────╢
║ Mercury           │   5000   │    60    │   0.24   │   1400   │ Closest to the sun.                ║
╟───────────────────┼──────────┼──────────┼──────────┼──────────┼────────────────────────────────────╢
║ Venus             │  12000   │   110    │   0.60   │   5800   │ Hottest planet.                    ║
╟───────────────────┼──────────┼──────────┼──────────┼──────────┼────────────────────────────────────╢
║ Earth             │  12800   │   150    │    1     │    24    │ Our home world.                    ║
╟───────────────────┼──────────┼──────────┼──────────┼──────────┼────────────────────────────────────╢
║ Mars              │   7000   │   230    │    2     │    25    │ Most Earth-like planet.            ║
╟───────────────────┼──────────┼──────────┼──────────┼──────────┼────────────────────────────────────╢
║ Jupiter           │  140000  │   780    │    12    │    10    │ Largest planet.                    ║
╟───────────────────┼──────────┼──────────┼──────────┼──────────┼────────────────────────────────────╢
║ Saturn            │  120000  │   1400   │    30    │    10    │ Has a large ring system.           ║
╟───────────────────┼──────────┼──────────┼──────────┼──────────┼────────────────────────────────────╢
║ Uranus            │  52000   │   2900   │    84    │    17    │ Has a ring system but not as       ║
║                   │          │          │          │          │ prominent as Saturn's.             ║
╟───────────────────┼──────────┼──────────┼──────────┼──────────┼────────────────────────────────────╢
║ Neptune           │  50000   │   4500   │   160    │    16    │ Officially the planet farthest     ║
║                   │          │          │          │          │ from the sun.                      ║
╟───────────────────┼──────────┼──────────┼──────────┼──────────┼────────────────────────────────────╢
║ Pluto             │   3000   │   6000   │   250    │   150    │ No longer considered a planet.     ║
╚═══════════════════╧══════════╧══════════╧══════════╧══════════╧════════════════════════════════════╝
```
'''

from textwrap import wrap
from rex import Rex
import ru
import colorama

class TableColor:
    class bg:
        header = colorama.Back.BLUE
        data = colorama.Back.WHITE
    class fg:
        header = colorama.Fore.WHITE
        data = colorama.Fore.BLACK

class TableStyle:

    class Unicode3:
        nw = '╔'
        n  = '═'
        ne = '╗'
        e  = '║'
        se = '╝'
        s  = '═'
        sw = '╚'
        w  = '║'
        v  = ' '
        h  = ' '
        nv = '═'
        sv = '═'
        wh = '║'
        eh = '║'
        vh = ' '

    class Unicode2:
        nw = '╔'
        n  = '═'
        ne = '╗'
        e  = '║'
        se = '╝'
        s  = '═'
        sw = '╚'
        w  = '║'
        v  = '║'
        h  = '═'
        nv = '╦'
        sv = '╩'
        wh = '╠'
        eh = '╣'
        vh = '╬'

    class Unicode1:
        nw = '╔'
        n  = '═'
        ne = '╗'
        e  = '║'
        se = '╝'
        s  = '═'
        sw = '╚'
        w  = '║'
        v  = '│'
        h  = '─'
        nv = '╤'
        sv = '╧'
        wh = '╟'
        eh = '╢'
        vh = '┼'

    class Basic:
        nw = '+'
        n  = '='
        ne = '+'
        e  = '|'
        se = '+'
        s  = '='
        sw = '+'
        w  = '|'
        v  = '|'
        h  = '-'
        nv = '+'
        sv = '+'
        wh = '+'
        eh = '+'
        vh = '+'

class _TableColumnDef:
    def __init__(self, table, title, key=None, width=None, justify='left'):
        r'''
        Define column attributes.

        ## Arguments
        - `title`: Header name.
        - `key`: Header data key.  If not defined, `title` is used (non-word characters will be removed).
        - `width`: Width (value between 0.0 and 1.0) as a factor of the total width.  If no widths are specified, the columns will be equal in size.  If the last column width is not specified, it will be calculated automatically.
        - `justify`: Either "left", "center", or "right". Can also be a list or tuple if justify differs for the header row and data rows (e.g. ['center', 'left']). 
        '''
        self.table = table
        self.table.num_cols += 1
        self.title = title
        self.key = key
        if key is None:
            rex = Rex()
            self.key = rex.s(self.title, r'\W', '', 'g=')
        self.width = width
        type_justify = type(justify)
        if type_justify == list:
            self.justify = justify
        elif type_justify == str:
            self.justify = [justify, justify]
        if len(self.justify) == 1:
            self.justify.append(self.justify)
        if len(self.justify) != 2:
            raise Exception(f'Attribute justify {self.justify} can only contain 2 items.')
        for item in self.justify:
            if item not in ['left', 'center', 'right']:
                raise Exception(f'Attribute justify {self.justify} has an invalid member "{item}".  Must be "left", "center" or "right".')
        self.size = 0

class Table:
    def __init__(self, title, width=98, hpad=1, vpad=0, style=TableStyle.Unicode1, color=False):
        r'''
        Define table.

        ## Arguments
        - `title`: Title for table.
        - `width`: Width of table in characters (default 98)
        - `style`: A `TableStyle.*` object (default = `TableStyle.Unicode1`).
        - `hpad`: Horizontal padding in characters (default = 1).
        - `vpad`: Vertical padding in empty lines (default = 0).
        - `color`: Color the table (default = False).

        ### Styles

        For argument `style`, you can choose from:

        - `TableStyle.Unicode1`
        - `TableStyle.Unicode2`
        - `TableStyle.Unicode3`
        - `Basic`

        `TableStyle.Unicode1`:

        ```
        ╔══════════════════════╤══════════════════════╤═════════════╗
        ║ City                 │ State                │  Population ║
        ╟──────────────────────┼──────────────────────┼─────────────╢
        ║ New York             │ New York             │   8,467,513 ║
        ╟──────────────────────┼──────────────────────┼─────────────╢
        ║ Los Angeles          │ California           │   3,849,297 ║
        ╟──────────────────────┼──────────────────────┼─────────────╢
        ║ Houston              │ Texas                │   2,288,250 ║
        ╚══════════════════════╧══════════════════════╧═════════════╝
        ```

        `TableStyle.Unicode2`:

        ```
        ╔══════════════════════╦══════════════════════╦═════════════╗
        ║ City                 ║ State                ║  Population ║
        ╠══════════════════════╬══════════════════════╬═════════════╣
        ║ New York             ║ New York             ║   8,467,513 ║
        ╠══════════════════════╬══════════════════════╬═════════════╣
        ║ Los Angeles          ║ California           ║   3,849,297 ║
        ╠══════════════════════╬══════════════════════╬═════════════╣
        ║ Houston              ║ Texas                ║   2,288,250 ║
        ╚══════════════════════╩══════════════════════╩═════════════╝
        ```

        `TableStyle.Unicode3`:

        ```
        ╔═══════════════════════════════════════════════════════════╗
        ║ City                   State                   Population ║
        ║                                                           ║
        ║ New York               New York                 8,467,513 ║
        ║                                                           ║
        ║ Los Angeles            California               3,849,297 ║
        ║                                                           ║
        ║ Houston                Texas                    2,288,250 ║
        ╚═══════════════════════════════════════════════════════════╝
        ```

        `TableStyle.Basic`:

        ```
        +======================+======================+=============+
        | City                 | State                |  Population |
        +----------------------+----------------------+-------------+
        | New York             | New York             |   8,467,513 |
        +----------------------+----------------------+-------------+
        | Los Angeles          | California           |   3,849,297 |
        +----------------------+----------------------+-------------+
        | Houston              | Texas                |   2,288,250 |
        +======================+======================+=============+
        ```

        '''
        self.title = title
        self.width = width
        self.style = style
        self.hpad = hpad 
        self.vpad = vpad 
        self.num_cols = 0
        self.col_width = []
        self.rows = []
        self.cols = []
        self.col = {}
        self.color = None
        if color:
            self.color = TableColor()

    def add_col(self, title, key=None, width=None, justify='left'):
        r'''
        Define and add a column to the table.  

        ## Arguments
        - `title`: Title of the column.
        - `name`: Data key name for the column.  If not defined, `title` is used.
        - `width`: Fractional width of the column.  All `width` values must total 1.0.  The following
           scenarios are allowed (1) You specify widths totalling 1.0 for all columns. (2) You specify
           all widths except 1 totalling < 1.0 -- the last will be calculated for you. (3) You don't
           specify any widths -- all widths will be equal.
        - `justify`: "left", "center" or "right" (default is "left")
          
        '''
        col = _TableColumnDef(self, title, key=key, width=width, justify=justify)
        self.cols.append(col)
        self.col[col.key] = col

    def add_data(self, data):
        r'''
        Add data table.  Value `data` must be a list of rows.  Each row object can be a dictionary,
        a column ordered tuple, or a column ordered list.

        ## Usage

        ```
        table.add_data(data)
        ```
        '''
        self.data = []
        for row in data:
            self.add_row(row)

    def add_row(self, row):
        r'''
        Add a data row.  Value `row` can be a dictionary, a column ordered tuple, or a column ordered
        list.

        ## Usage

        ```
        for row in data:
            table.add_row(row)
        ```
        '''
        type_row = type(row)
        if type_row == dict:
            set_table_keys = set(self.col.keys())
            set_row_keys = set(row.keys())
            diff = set_row_keys - set_table_keys
            if len(diff) > 0:
                raise Exception(f'Invalid data key(s) {diff} in data row {row}.')
            self.rows.append(row)
            return
        if type_row == tuple:
            row = list(row)
        if type_row == list:
            if len(row) > len(self.cols):
                raise Exception(f'Invalid data row {row} contains {len(row)} items but table only defines {len(self.cols)} columns.')
            d = dict()
            for i in range(0, len(row)):
                d[self.cols[i].key] = row[i]
            self.rows.append(d)
            return
        raise Exception(f'Invalid row data type {type_row} for row data {row}.  Must be dict, list or tuple.')
    
    def _prep_cols(self):
        # Set `no_width_col` to the first column with width of None.  Set `all_col_widths_undefined`
        # to True if no column has a defined width, False otherwise.  Set `sum_widths` to the sum
        # of all defined columns widths.
        no_width_col = None
        all_col_widths_undefined = True
        sum_widths = 0
        for col in self.cols:
            if col.width is not None:
                all_col_widths_undefined = False
                sum_widths += col.width
            else:
                if no_width_col is None:
                    no_width_col = col
        # # # If more than one column has width undefined but there is at least one column where the 
        # # # width is defined, it is an error.
        # # if no_width_col is not None and all_col_widths_undefined:
        # #     raise Exception('You may define widths for all columns, all but one, or none.')
        # If all columns widths are undefined, the columns will all have the same width, equally 
        # divisible by the number of available spaces.  
        if all_col_widths_undefined:
            width = 1 / self.num_cols
            for col in self.cols:
                col.width = width
        # If only a single column width is not defined, calculate the width from the others.
        elif no_width_col is not None:
            no_width_col.width = 1 - sum_widths
        # Recalculate the sum of all column widths.  
        sum_widths = 0
        for col in self.cols:
            sum_widths += col.width
        # Make sure the column widths are not too large or small. 
        if abs(1-sum_widths) > 0.05:
            raise Exception(f'Column widths total {sum_widths} but must be equal to 1.')
        # Calculate the column size.  The is the actual number of available characters for the 
        # column.
        available_char_spaces = self.width - 2*(1+self.hpad) - (self.num_cols-1)*(1+self.hpad) - 1
        char_count = 0
        for col in self.cols:
            col.size = round(col.width * available_char_spaces)
            char_count += col.size
        # If the total column sizes does not equal to the total available spaces (possible because 
        # we are rounding) try to correct.
        if char_count != available_char_spaces:
            diff = available_char_spaces - char_count
            self.cols[-1].size += diff
        # Calculate the total column sizes one more time.
        char_count = 0
        for col in self.cols:
            char_count += col.size
        # We shouldn't fail here.  If we do, it is because the algorithm isn't doing what it was
        # designed to do (a.k.a. it is an operator head-space issue).
        if char_count != available_char_spaces:
            raise Exception(f'Column total size {char_count} does not equal available character size {available_char_spaces}.  This is an algorithm issue that needs to be fixed.')

    def render(self):
        r'''
        Render and return the text table.

        ## Usage

        ```
        print(table.render())
        ```
        '''
        self._prep_cols()
        row = {}
        for col in self.cols:
            row[col.key] = col.title
        data = ru.clone(self.rows)
        data.insert(0, row)
        index = 0

        color = None
        start_color = ''
        clear_color = ''
        start_color1 = ''
        start_color2 = ''
        if self.color is not None:
            colorama.init(autoreset=True)
            color = self.color
            start_color = f'{color.bg.header}{color.fg.header}'
            clear_color = f'{colorama.Style.RESET_ALL}'
            start_color1 = f'{color.bg.header}{color.fg.header}'
            start_color2 = f'{color.bg.data}{color.fg.data}'

        style = self.style
        last = len(self.cols)
        top = []
        mid = []
        bot = []
        no1 = []
        no2 = []
        top.append(style.nw)
        mid.append(style.wh)
        bot.append(style.sw)
        no1.append(style.w)
        no2.append(style.w)
        for i in range(0, last):
            col = self.cols[i]
            width = col.size + 2*self.hpad
            top.append(style.n * width)
            mid.append(style.h * width)
            bot.append(style.s * width)
            no1.append(start_color1)
            no1.append(' ' * width)
            no1.append(clear_color)
            no2.append(start_color2)
            no2.append(' ' * width)
            no2.append(clear_color)
            if i == last - 1: continue
            top.append(style.nv)
            mid.append(style.vh)
            bot.append(style.sv)
            no1.append(style.v)
            no2.append(style.v)
        top.append(style.ne)
        mid.append(style.eh)
        bot.append(style.se)
        no1.append(style.e)
        no2.append(style.e)
        top = ''.join(top)
        mid = ''.join(mid)
        bot = ''.join(bot)
        no1 = ''.join(no1)
        no2 = ''.join(no2)

        pad = no1
        
        text = []
        text.append(top)

        for row in data:
            max_line_cnt = 0
            for key in row:
                col = self.col[key]
                width = col.size
                justify = col.justify[index]
                
                split_lines = str(row[key]).split('\n')
                cell = []
                for split_line in split_lines:
                    wrapped_lines = wrap(split_line, width=width)
                    if len(wrapped_lines) == 0:
                        cell.append('')
                    else:
                        for wrapped_line in wrapped_lines:
                            cell.append(wrapped_line)
                
                max_line_cnt = max(max_line_cnt, len(cell))

                for i in range(0, len(cell)):
                    line = cell[i]
                    if   justify == 'left':    line = line.ljust(width)
                    elif justify == 'center':  line = line.center(width)
                    elif justify == 'right':   line = line.rjust(width)
                    else: raise Exception(f'Attribute justify {col.justify} has an invalid member "{justify}".  Must be "left", "center" or "right".')
                    cell[i] = line
                row[key] = cell
            
            for key in row:
                col = self.col[key]
                width = col.size
                while len(row[key]) < max_line_cnt:
                    row[key].append(''.ljust(width))
            
            for i in range(0, self.vpad):
                text.append(pad)
            
            for i in range(0, max_line_cnt):
                line = []
                line.append(style.w)
                for col in self.cols:
                    key = col.key
                    line.append(start_color)
                    line.append(' '*self.hpad)
                    line.append(row[key][i])
                    line.append(' '*self.hpad)
                    line.append(clear_color)
                    if key == self.cols[-1].key: continue
                    line.append(style.v)
                line.append(style.e)
                line = ''.join(line)
                text.append(line)
            for i in range(0, self.vpad):
                text.append(pad)
            text.append(mid)
            if index == 0: 
                index = 1
                if self.color is not None:
                    start_color = f'{color.bg.data}{color.fg.data}'
                    pad = no2
        text.pop()
        text.append(bot)
        text = '\n'.join(text)
        return text
            
if __name__ == '__main__':
    t = Table('Test One', style=TableStyle.Unicode1, color=False, hpad=0, vpad=0)
    t.add_col('1st Column', key='c1', width=0.2, justify=['center', 'left'])
    t.add_col('2nd Column', key='c2', width=0.2, justify=['center', 'left'])
    t.add_col('3rd Column', key='c3', width=0.3, justify=['center', 'left'])
    t.add_col('4th Column', key='c4', justify=['center', 'left'])
    data = [
        {
            'c1': 'Lorem ipsum dolor sit amet',
            'c2': 'Consectetur adipiscing elit',
            'c3': 'D do eiusmod tempor incididunt ut labore et dolore magna aliqua',
            'c4': 'Ut enim ad minim veniam',
        },
        {
            'c1': 'Sed ut perspiciatis unde omnis',
            'c2': 'Iste natus error sit voluptatem',
            'c3': 'Accusantium doloremque',
            'c4': 'Totam rem aperiam',
        },
        {
            'c1': 'Eaque ipsa quae ab illo inventore',
            'c2': 'Veritatis et quasi architecto',
            'c3': 'Beatae vitae dicta sunt explicabo',
            'c4': 'Nemo enim ipsam voluptatem',
        },
        {
            'c1': 'Quia voluptas sit aspernatur',
            'c2': 'Aut odit aut fugit',
            'c3': 'Sed quia consequuntur magni dolores',
            'c4': 'Eos qui ratione voluptatem',
        },
    ]
    t.add_data(data)
    t.render()
