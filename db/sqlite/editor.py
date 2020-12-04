r"""
## Description
Create and parse SQLite database files.

"""

import sqlite3
import ru
from regx import Regx
import fs

class ColumnInfoFK():
    def __init__(self):
        me = self
        me.table = None
        me.col = None

class ColumnInfo():
    def __init__(self):
        me = self
        me.name = None
        me.type = None
        me.pk = False
        me.fk = None
        me.default = None
        me.notnull = False
        me.unique = False
    def __repr__(self):
        me = self
        hash = {}
        hash['name'] = me.name
        hash['type'] = me.type
        if me.unique: hash['unique'] = me.unique
        if me.pk: hash['pk'] = me.pk
        if me.fk is not None:
            hash['fk'] = {}
            hash['fk']['table'] = me.fk.table
            hash['fk']['col'] = me.fk.col
        if me.default is not None: hash['default'] = me.default
        if me.notnull: hash['notnull'] = me.notnull
        return(repr(hash))

class TableInfo():
    def __init__(self, name=None):
        me = self
        me.name = name
        me.cols = {}
        me.order = []
        me.pk = 'rowid'
    def __repr__(self):
        me = self
        hash = {}
        hash['name'] = me.name
        hash['pk'] = me.pk
        hash['order'] = me.order
        hash['cols'] = me.cols
        return(repr(hash))

class SQLite():
    
    def __init__(self, dbfile, verbose=0, create=False):
        r"""
        ## Description
        Open a database.

        ## Usage
        Create a database:
        ```
        db = SQLite('file.db3', create=True)
        ```
        Read existing database:
        ```
        db = SQLite('file.db3')
        ```
        
        ## Arguments
        - `dbfile` : name of the db3 file to be opened
        - `verbose` : verbosity setting; verbose printing if > 0
        - `create` : create database if it does not already exist

        ## Returns
        SQLite object.
        """

        # Nested function to convert str into list.
        def str_to_list(val):
            regx = Regx()
            val = str(val)
            val = regx.split(val, r'\s*,\s*')
            return(val)
        
        # Nested function to convert list into str.
        def list_to_str(lst):
            return(", ".join(lst))

        # Nested function to return object as is.    
        def return_as_is(val): 
            return(val)

        # When creating tables, allow these aliases.  
        self.alias_type = \
        {
            'varchar':  'text',
            'boolean':  'integer',
            'string':   'text',
            'numeric':  'real',
            'float':    'real',
            'integer':  'integer',
            'text':     'text',
            'real':     'real',
            'serial':   'integer',
        }

        self.caster = \
        {
            'text': str,
            'integer': int,
            'real': float
        }

        # Valid args with conversion functions and defaults.
        self.arg = \
        {
            'table':
            {
                'type': {'str': str},
            },
            'where':
            {
                'type': {'str': str},
                'default': '',
            },
            'join':
            {
                'type': {'str': str},
                'default': '',
            },
            'cols':
            {
                'type': {'str': str, 'list': list_to_str},
                'default': '*',
            },
            'bindings':
            {
                'type': 
                {
                    'list': return_as_is, 
                    'str': str_to_list,
                    'float': str_to_list,
                    'int': str_to_list,
                },
                'default': [],
            },
            'data':
            {
                'type': {'dict': dict},
                'default': {},
            },
        }

        # Initialize variables.
        self.table_info = {}
        self.tables = []
        self.id_name = '$ID'
        self.db = None
        self.dbfile = dbfile
        self.verbose = verbose
        self.create = create
        # If a dbfile was passed in, read it.  
        if self.dbfile is not None: self.open(self.dbfile, self.verbose, self.create) 

    def open(self, dbfile=None, verbose=0, create=False):
        r"""
        ## Description
        Open a database.

        ## Usage
        Create a database:
        ```
        db.open('file.db3', create=True)
        ```

        Read existing database:
        ```
        db.open('file.db3')
        ```
        
        ## Arguments
        - `dbfile` : name of the dbfile to be opened
        - `vebose` : verbosity setting; verbose printing if > 0
        - `create` : create database if it does not already exist

        ## Returns
        Nothing.
        """
        self.dbfile = dbfile if dbfile is not None else self.dbfile
        if self.verbose < 0 and verbose >= 0: self.verbose = verbose
        if self.dbfile is None: raise Exception('No database file specified')
        if not create and not fs.file_exists(self.dbfile): raise Exception('Required database file "{}" does note exist (specify create=True to create it)'.format(self.dbfile))
        if self.verbose > 0: print('Opening connection to database file "{}"'.format(self.dbfile))
        self.db = sqlite3.connect(self.dbfile, check_same_thread=False)
    
    def close(self):
        self.db.close()

    def get_table_info(self, table):
        r"""
        ## Description
        Returns a `TableInfo` object for table `table`.

        ## Usage
        ```
        tables = db.get_tables()
        for table in tables:
            info = db.get_table_info(table)
        ```

        ## Arguments
        - `table` : table name

        ## Returns
        `TableInfo` object:
        - `info.name` : name of the table
        - `info.pk` : primary key column name if it exits, rowid otherwise
        - `info.cols` : column dict: {'`column-name`': `<ColumnInfo object>`, ...}
        - `info.order` : list of columns in correct order

        """
        curs = self.execute('pragma table_info("{}")'.format(table))
        rows = curs.fetchall()
        info = TableInfo(table)
        for row in rows:
            row = self.__row_to_dict(curs, row)
            name = row['name']
            col = ColumnInfo()
            col.name = name
            col.type = row['type']
            if 'pk' in row: 
                col.pk = bool(row['pk'])
                if col.pk: info.pk = name
            if 'dflt_value' in row and row['dflt_value'] is not None: 
                col.default = self.caster[col.type](row['dflt_value'])
            if 'unique' in row: col.unique = bool(row['unique'])
            if 'notnull' in row: col.unique = bool(row['notnull'])
            info.cols[name] = col
            info.order.append(col.name)
        curs = self.execute('pragma foreign_key_list("{}")'.format(table))
        rows = curs.fetchall()
        for row in rows:
            row = self.__row_to_dict(curs, row)
            name = row['from']
            col = info.cols[name]
            col.fk = ColumnInfoFK()
            col.fk.table = row['table']
            col.fk.col = row['to']
        self.table_info[table] = info
        return(info)

    def get_tables(self):
        r"""
        ## Description
        Returns a list of table names.
        
        ## Usage
        ```
        tables = db.get_tables()
        ```

        ## Arguments
        None.

        ## Returns
        List of tables e.g. `['people', 'places', 'things']`. 
        """
        sql = 'select name from sqlite_master as m where m.type="table" and not(m.tbl_name = "sqlite_sequence")'
        curs = self.execute(sql)
        self.tables = []
        rows = curs.fetchall()
        for row in rows:
            row = self.__row_to_dict(curs, row)
            self.tables.append(row['name'])
        return(self.tables)

    def get_id(self, **arg):
        '''
            Get the ID for the specified record.  Return 0 if no match is found.
            # Args
            - Required
                - table -> required table name
                - where -> required where clause
            - Optional
                - bindings -> optional where clause bindings
        '''
        # Validate args.
        param = self.__validate_args(arg, ['table', 'where'], ['bindings'])
        # Validated args to variables.
        table = param['table']
        where = param['where']
        bindings = param['bindings']
        # If self.table_info[table] is not defined, call self.get_table_info(table) to define it.
        if table not in self.table_info: self.get_table_info(table)
        # The the primary key (pk).
        pk = self.table_info[table].pk if self.table_info[table].pk else 'rowid'
        # Create the SQL statement and execute it returning the database cursor.
        sql = 'select {} from {} where {}'.format(pk, table, where)
        curs = self.execute(sql, bindings)
        # Fetch a single row from the database.
        row = curs.fetchone()
        # Return row[pk] if defined.
        if row is not None: 
            row = self.__row_to_dict(curs, row)
            return(row[pk])
        # If no row was found, return 0.
        return(0)

    def get_ids(self, **arg):
        '''
            Get the ID for the specified record.  Return 0 if no match is found.
            # Args
            - Required
                - table -> required table name
                - where -> required where clause
            - Optional
                - bindings -> optional where clause bindings
        '''
        param = self.__validate_args(arg, ['table', 'where'], ['bindings'])
        sql = 'select rowid as {} from {}'.format(self.id_name, param['table'])
        if len(param['where']) > 0: sql += ' where {}'.format(param['where'])
        curs = self.execute(sql, param['bindings'])
        ids = []
        rows = curs.fetchall()
        for row in rows:
            row = self.__row_to_dict(curs, row)
            ids.append(row[self.id_name])
        return(ids)

    def update_record(self, **arg):
        param = self.__validate_args(arg, ['table', 'data', 'where'], ['bindings'])
        table = param['table']
        if table not in self.table_info: self.get_table_info(table)
        id = self.get_id(table=param['table'], where=param['where'], bindings=param['bindings'])
        # If no record matching the rowid is found, insert a new record.
        if id == 0: return(0)
        # If a matching record was found, update the existing record.
        data = self.__get_update_data(param['data'])
        sql = 'update {} set {} where rowid = {}'.format(param['table'], data['update'], id)
        self.execute(sql, [data['bindings']])
        self.db.commit()
        return(id)

    def insert_record(self, **arg):
        param = self.__validate_args(arg, ['table', 'data'], ['bindings'])
        # If param['data'] contains the rowid key ...
        if self.id_name in param['data']:
            # Get the record rowid.
            id = param['data'][self.id_name]
            del(param['data'][self.id_name])
            # Query the database for the record by the rowid.
            record = self.read_record(table=param['table'], cols="*", where='rowid = ?', bindings=[id])
            # If no record matching the rowid is found, insert a new record.
            if record is None:
                return(0)
            # If a matching record was found, update the existing record.
            else:
                data = self.__get_update_data(param['data'])
                sql = 'update {} set {} where rowid = {}'.format(param['table'], data['update'], id)
                curs = self.execute(sql, data['bindings'])
                self.db.commit()
                return(id)
        # if param['data'] did not contain a rowid key (and param['where'] is not defined), we 
        # just insert the new data.
        else:
            data = self.__get_insert_data(param['data'])
            sql = 'insert into {} ({}) values ({})'.format(param['table'], data['cols'], data['vals'])
            curs = self.execute(sql, data['bindings'])
            self.db.commit()
            return(curs.lastrowid)

    def write_record(self, **arg):
        '''
            Write data to the database.  If *where* is specified or if *data* contains self.id_name key,
            update the indicated record.  Otherwise add a new record.  Return the id of the 
            updated or added record, 0 if no write was done.
            # Args
            - Required
                - table -> required table name
                - data -> data to write
            - Optional
                - where -> optional where clause
                - bindings -> optional where clause bindings
        '''
        param = self.__validate_args(arg, ['table', 'data'], ['where', 'bindings'])
        # If there is no param['where'] clause ...
        if len(param['where']) == 0:
            # If param['data'] contains the rowid key ...
            if self.id_name in param['data']:
                # Get the record rowid.
                id = param['data'][self.id_name]
                del(param['data'][self.id_name])
                # Query the database for the record by the rowid.
                record = self.read_record(table=param['table'], cols="*", where='rowid = ?', bindings=[id])
                # If no record matching the rowid is found, insert a new record.
                if record is None:
                    return(0)
                # If a matching record was found, update the existing record.
                else:
                    data = self.__get_update_data(param['data'])
                    sql = 'update {} set {} where rowid = {}'.format(param['table'], data['update'], id)
                    curs = self.execute(sql, data['bindings'])
                    self.db.commit()
                    return(id)
            # if param['data'] did not contain a rowid key (and param['where'] is not defined), we 
            # just insert the new data.
            else:
                data = self.__get_insert_data(param['data'])
                sql = 'insert into {} ({}) values ({})'.format(param['table'], data['cols'], data['vals'])
                curs = self.execute(sql, data['bindings'])
                self.db.commit()
                return(curs.lastrowid)
        # If param['where'] clause was specified.
        else:
            id = self.get_id(table=param['table'], where=param['where'], bindings=param['bindings'])
            # If no record matching the rowid is found, insert a new record.
            if id == 0:
                return(0)
            # If a matching record was found, update the existing record.
            else:
                data = self.__get_update_data(param['data'])
                sql = 'update {} set {} where rowid = {}'.format(param['table'], data['update'], id)
                curs = self.execute(sql, [data['bindings']])
                self.db.commit()
                return(id)

    def read_record(self, **arg):
        '''
            Read a single record.  Return the matching row as dict, or None if no record is found.
            # Args
            - Required
                - table -> required table name
                - where -> required where clause
            - Optional
                - cols -> columns to query (default = "*")
                - bindings -> optional where clause bindings
            # Usage
            Find and return record matching *where* clause.  Example: 
                record = db.read_record(table="BLOCKS", where="BITS > 1024");
            This command will:
            1. Check to see if record matching *where* clause exists.
            2. If exists, return the record.
            3. If it does not exist, return None.
        '''
        # Validate params.
        param = self.__validate_args(arg, ['table', 'where'], ['cols', 'bindings'])
        # Create SQL statement.
        if ',' not in param['table']: param['cols'] += ', rowid as "{}"'.format(self.id_name)
        sql = 'select {} from {}'.format(param['cols'], param['table'])
        if len(param['where']) > 0: sql += ' where {}'.format(param['where'])
        # Execute SQL query.
        curs = self.execute(sql, param['bindings'])
        # Return record if found, None otherwise.
        row = curs.fetchone()
        if row is not None: return(self.__row_to_dict(curs, row))
        return(None)

    def read_records(self, **arg):
        '''
            Read matching records.  Return generator object of dict rows, or None if no record is found.
            # Args
            - Required
                - table -> required table name
                - where -> required where clause
            - Optional
                - join -> inner join clause
                - cols -> columns to query (default = "*")
                - bindings -> optional where clause bindings
            # Usage
            Find and return generator object for records matching *where* clause.  Example: 
                for record in db.read_record(table="BLOCKS", where="BITS > 1024"): print(record)
            If multiple tables are being searched, 
        '''
        # Validate params.
        param = self.__validate_args(arg, ['table'], ['cols', 'join', 'where', 'bindings'])
        # Create SQL statement.
        if ',' in param['table']:
            regx = Regx()
            tables = regx.split(param['table'], r'\s*,\s*')
            for table in tables:
                param['cols'] += ', {}.rowid as "{}"'.format(table, table + "." + self.id_name)
        elif len(param['join']) > 0:
            regx = Regx()
            table = param['table']
            param['cols'] += ', {}.rowid as "{}"'.format(table, table + "." + self.id_name)
            if regx.m(param['join'], r'^\s*(\S+)'):
                table = regx.group[0]
                param['cols'] += ', {}.rowid as "{}"'.format(table, table + "." + self.id_name)
        else:
            param['cols'] += ', rowid as "{}"'.format(self.id_name)
        sql = 'select {} from {}'.format(param['cols'], param['table'])
        if len(param['join']) > 0: sql += ' inner join {}'.format(param['join'])
        if len(param['where']) > 0: sql += ' where {}'.format(param['where'])
        # if len(param['join']) > 0 and len(param['where']) > 0: 
        #     raise Exception('Cannot execute both INNER JOIN and WHERE in SQL statement: {}'.format(sql))
        # Execute SQL query.
        curs = self.execute(sql, param['bindings'])
        # Yield generator results if found, return None otherwise.
        rows = curs.fetchall()
        # if rows == None: return(None)
        for row in rows:
            yield(self.__row_to_dict(curs, row))

    def execute(self, sql, bindings=''):
        curs = self.db.cursor()
        # if not type(bindings) == list: bindings = [str(bindings)]
        if self.verbose > 0: print(sql); print(bindings)
        curs.execute(sql, bindings)
        return(curs)

    def __validate_args(self, arg, required, optional):
        param = {}
        for key in required:
            if key not in arg: 
                raise Exception('Required parameter "{}" not defined'.format(key))
        for key in optional:
            if key not in arg:
                stype = ru.string_type(self.arg[key]['default'])
                if stype == 'dict' or stype == 'list': arg[key] = self.arg[key]['default'].copy()
                else: arg[key] = self.arg[key]['default']
        for key in arg:
            if key not in required and key not in optional: raise Exception('Invalid parameter "{}" specified'.format(key))
            stype = ru.string_type(arg[key])
            param[key] = self.arg[key]['type'][stype](arg[key]) if stype in self.arg[key]['type'] else arg[key]
        return(param)    

    def __get_insert_data(self, data):
        cols = []; vals = []; bindings = []
        for key in sorted(data):
            cols.append(key)
            vals.append("?")
            bindings.append(data[key])
        info = \
        {
            'cols': ','.join(cols),
            'vals': ','.join(vals),
            'bindings': bindings,
        }
        return(info)

    def __get_update_data(self, data):
        update = []
        bindings = []
        for key in data:
            if key != self.id_name:
                update.append('{} = ?'.format(key))
                bindings.append(data[key])
        info = \
        {
            'update': ', '.join(update),
            'bindings': bindings,
        }
        return(info)
            
    def __row_to_dict(self, curs, row):
        d = {}
        for idx, col in enumerate(curs.description):
            d[col[0]] = row[idx]
        return (d)






    