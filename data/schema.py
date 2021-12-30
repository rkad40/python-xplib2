r"""
The `data.schema` module features one exportable class, `DataManager` which can be used to:

- validate data objects
- serialize data objects

Currently the only serialization format supported is YAML.  One restriction is that only base types 
can be validated and rendered.  This means you could not validate or render data objects with nested 
classes.  
"""

import fs
import ru
import re
import json
from rex import Rex
import importlib.util as importer
import textwrap

VERSION = '1.2.0'

r"""
## History

1.2:
- Various bug fixes.

1.1:
- Added dict class `key-sort-func` schema attribute.  Allows user to specify custom key sort function for dict nodes where `keys` is not defined or `regx` is True for a speceifed entry in `keys`.

"""

TEST = []

class DataManagerRenderYAMLOptions():
    def __init__(self):
        self.number_indent_spaces = 2
        self.enable_list_inset = False
        self.enable_list_compaction = True
        self.enable_double_quote = False
        self.collapsed_line_length = 0
        self.add_document_separator = True

class DataManagerRenderOptions():
    def __init__(self):
        self.yaml = DataManagerRenderYAMLOptions()

class DataManager():
    r"""
    ## Description
    Validate and render data object (as YAML).

    ## Usage
    
    ```python
    from data.schema import DataManager
    import yaml, fs
    # Load the schema.
    schema = yaml.load(fs.read_file('example-schema.yml', True), Loader=yaml.FullLoader)
    # Load the data
    example = yaml.load(fs.read_file('example-data.yml', True), Loader=yaml.FullLoader)
    # Create a DataManager object.,
    dm = DataManager(schema, 'example-schema.py')
    # Validate the data.
    dm.validate(example)
    # Render data as YAML.
    yaml_text = dm.to_yml(example)
    ```

    ## Arguments
    - `schema`: `DataManager` schema.  This defines the rules for validating and rendering data.
    - `module_file`: Additional interposer functions defined in the schema.  The functions are used 
    to modify and validate data.  Optional, defaults to `None`.
    - `root_rule_name`: Defines the root rule in the schema.  Alternatively the rule can define a 
    `root` attribute set to `True`.  Optional, defaults to "root".
    - `verbosity`=1: Currently does not do anything.

    ## Examples
    Here are a few examples that illustrate how to use `DataManager`:

    ### Example 1: Generic Data

    This example includes many different data object examples:  

    - The source data file [`example-data.yml`](../test/data-schema/example-data.yml) features a 
    wide range of YAML styled data objects.
    - The schema file [`example-schema.yml`](../test/data-schema/example-schema.yml) is a YAML file 
    that tells `DataManager` how to parse the source YAML: 
    - The schema module [`example-schema.py`](../test/data-schema/example-schema.py) contains 
    interposer routines references in `example-schema.yml` that are used to validate and update 
    source data.
    - The script file [`example-test.py`](../test/data-schema/example-test.py) reads the data file 
    and uses the schema to validate it and render an output file 
    [`example-test.py`](../test/data-schema/example-test.py)

    ### Example 2: Sitcoms

    This example illustrates the reach of `DataManager`:  

    - The source data file [`example-data.yml`](../test/data-schema/example-data.yml) features a 
    wide range of YAML styled data objects.
    - The schema file [`example-schema.yml`](../test/data-schema/example-schema.yml) is a YAML file 
    that tells `DataManager` how to parse the source YAML: 
    - The schema module [`example-schema.py`](../test/data-schema/example-schema.py) contains 
    interposer routines references in `example-schema.yml` that are used to validate and update 
    source data.
    - The script file [`example-test.py`](../test/data-schema/example-test.py) reads the data file 
    and uses the schema to validate it and render an output file 
    [`example-test.py`](../test/data-schema/example-test.py)

    """

    debug_mode = False
    print_warnings = True
    coverage_testing = False  # Turned on for coverage tests.  Suppresses some prints.
    
    ##########

    def __init__(self, schema, module_file=None, root_rule_name='root', verbosity=1):
        self.schema = None
        self.root_rule_name = None
        self.render = DataManagerRenderOptions()
        self.initialize(schema, module_file, root_rule_name, verbosity)
    
    ##########

    def __repr__(self):
        return('<DataManager>')
    
    ##########

    def __load_module(self, module_file=None):
        orig_module_file = module_file
        if not fs.is_abs_path(module_file): 
            module_file = fs.join_names(fs.get_script_dir(), module_file)
        if not fs.file_exists(module_file): 
            raise Exception('File "{}" does not exist.'.format(orig_module_file))
        spec = importer.spec_from_file_location(name="", location=module_file)
        self.module_spec = importer.module_from_spec(spec)
        spec.loader.exec_module(self.module_spec)
    
    ##########

    def initialize(self, schema, module=None, root_rule_name=None, verbosity=1):
        
        # Initialize instance variables.
        # schema = json.loads(json.dumps(schema)) # Bug fix.  If schema is used a second time, an error can occur:
        #                                         # Exception: Schema rule name "__undefined__" not defined in schema object.
        self.data_object = None
        self.schema = schema         # schema object
        self.validated_rules = {}    # hash of validated rule names
        self.debug_index = 0
        # self.render = DataManagerRenderOptions()

        if schema is None: raise Exception('Parameter schema cannot be None.')
        if type(schema) is not dict: raise Exception('Parameter schema is not a dict object.')
        if len(schema) == 0: raise Exception('Parameter schema cannot be an empty dict.')

        # Identify the root schema rule (will have 'root' attribute set to True).
        for rule_name in self.schema: 
            schema_rule = self.schema[rule_name]
            if 'root' in schema_rule and bool(schema_rule['root']): 
                self.root_rule_name = rule_name
        if self.root_rule_name is None and root_rule_name is not None:
            self.root_rule_name = root_rule_name
        if self.root_rule_name is None: raise Exception('A root schema rule was not specified.')
        if not self.root_rule_name in self.schema: raise Exception('Schema rule name "{}" not defined in schema object.'.format(self.root_rule_name))
        
        # Validate schema recursively starting at self.root_rule_name.
        self.__validate_schema_recursively(self.root_rule_name)

        # See if there are any rules that were not validated.
        if self.print_warnings:
            rules_not_validated = []
            for rule_name in self.schema:
                if not rule_name in self.validated_rules:
                    rules_not_validated.append(rule_name)
            number_rules = len(rules_not_validated)
            if number_rules == 1: 
                if not self.coverage_testing: # pragma: no cover
                    print('WARNING: Schema rule "{}" defined but not used. (You can disable this warning by setting class variable print_warnings to False.)'.format(rules_not_validated[0]))
            elif number_rules > 1:
                if not self.coverage_testing: # pragma: no cover
                    print('WARNING: Schema rules "{}" defined but not used. (You can disable this warning by setting class variable print_warnings to False.)'.format('", "'.join(rules_not_validated)))

        # Load module if one is defined.
        if module is not None:
            self.__load_module(module)
    
    ##########

    def __validate_schema_recursively(self, rule_name):
        '''
            Recursively validate the schema schema.
            # Usage 
                self.__validate_schema_recursively(self.root_rule_name)
            # Args
            - rule_name: rule_name to be evaluted
            # Returns
            Nothing, raises Exception on failure
        '''
        # Get schema rule object.
        if rule_name is None: return()

        if not rule_name in self.schema:
            # If a rule is not specified, checks (and recursive checks) are suspended for the data 
            # node.  If a schema is used twice, the rule of type None is given the name 
            # '__undefined__'.  Check for that here and return if found.  
            if rule_name == '__undefined__': 
                return
            raise Exception('Schema rule name "{}" not defined in schema object.'.format(rule_name))
        schema_rule = self.schema[rule_name]
        
        # Identify and validate rule 'class' attribute.
        if not 'class' in schema_rule: # pragma: no coverage
            raise Exception('Required attribute "class" not defined for schema rule "{}".'.format(rule_name))
        rule_class = str(schema_rule['class']).lower()
        
        # Rule class must must be one of 'str', 'int', 'float', 'list', 
        # 'list', or 'dict'.  Validate the valid and required attributes.  Then 
        # recursively validate all children nodes. 
        if rule_class == 'str':
            self.__validate_rule_params(schema_rule, rule_name, ['class'], ['root', 'default', 'allow-null', 'validation-func', 
                'comment', 'matches', 'in', 'equals'])
            self.validated_rules[rule_name] = True
            return()
        if rule_class == 'bool':
            self.__validate_rule_params(schema_rule, rule_name, ['class'], ['root', 'default', 'allow-null', 'validation-func', 
                'comment'])
            self.validated_rules[rule_name] = True
            return()
        if rule_class == 'int' or rule_class == 'float':
            self.__validate_rule_params(schema_rule, rule_name, ['class'], ['root', 'min-value', 'max-value', 'default', 
                'allow-null', 'validation-func', 'comment'])
            self.validated_rules[rule_name] = True
            return()
        elif rule_class == 'list':
            self.__validate_rule_params(schema_rule, rule_name, ['class'], ['rule', 'root', 'min-count', 'max-count', 'comment', 
                'default', 'render', 'pre-validation-func', 'post-validation-func'])
            if 'rule' in schema_rule: self.__validate_schema_recursively(schema_rule['rule'])
            self.validated_rules[rule_name] = True
            return()
        elif rule_class == 'dict':
            self.__validate_rule_params(schema_rule, rule_name, ['class'], ['keys', 'min-count', 'max-count', 'key-sort-func', 'comment', 'default', 
                'render', 'root', 'pre-validation-func', 'post-validation-func'])
            i = 0
            if 'keys' in schema_rule:
                for hash in schema_rule['keys']:
                    self.__validate_rule_params(hash, '{}.keys[{}]'.format(rule_name,i), ['name', 'rule'], ['root', 'comment', 
                        'required', 'regx', 'default'])
                    if 'rule' in hash: self.__validate_schema_recursively(hash['rule'])
                    i += 1
            self.validated_rules[rule_name] = True
            return()
        else: # pragma: no coverage
            raise Exception('Invalid schema rule class "{}" for schema rule "{}"'.format(rule_class, rule_name))
    
    ##########

    def __validate_rule_params(self, schema_rule, rule_name, required_attr, valid_attr):
        '''
            Analyze rule (named rule_name).  Make sure required_attr exist and used valid_attr to make sure there are no invalid attributes.
            # Usage: 
                self.__validate_rule_params(schema_rule, rule_name, ['class'], ['function', 'comment', 'line-comment'])
            # Arguments
            - schema_rule: schema rule object being evaluated
            - rule_name: rule_name name of schema rule being evaluated (used for printing errors, if found)
            - required_attr: list of required attributes
            - valid_attr: along with required_attr, list of attributes that may exist
            # Returns
            Nothing, raises Exception on failure
        '''
        # Create all_valid_attr_hash whose keys are all required and valid attributes.
        all_valid_attr_hash = {}
        all_valid_attr_list = required_attr + valid_attr
        for item in all_valid_attr_list:
            all_valid_attr_hash[item] = True
        
        # Make sure all attributes in schema rule are valid.
        for item in schema_rule:
            if not item in all_valid_attr_hash: raise Exception('Invalid attribute "{}" defined in schema rule "{}".'.format(item, rule_name))
        
        # Make sure all requires attributes for the schema rule are defined.
        for item in required_attr:
            if not item in schema_rule: raise Exception('Required attribute "{}" not defined in schema rule "{}".'.format(item, rule_name))
    
    ##########

    def validate(self, data):
        '''
            ### Description
            Validate data using the pre-defined schema.
            
            ### Usage
            
            ```python 
            self.validate(data)
            ```

            ### Arguments
            - `data`: data object to be validated
            
            ### Returns
            Nothing, raises Exception on failure.
        '''
        # Begin validating data from the root rule, recursively thereafter.
        rule_name = self.root_rule_name
        self.data_object = data
        self.__validate_data_recursively(data, rule_name, rule_name, [], 0, None, '')
        return data
    
    ##########

    def __validate_data_recursively(self, data, rule_name, node, nodes, depth, parent, parent_class, default_value=None):
        '''
            Private, recursive workhorse of the validate() method.
            # Arguments
            - data: data object to be validated
            - rule_name: rule name used for data validation
            - node: printable node depth indicator
            - nodes: list of nodes to current depth
            - depth: depth of nodes
            - parent: parent object
            - parent_class: class of parent object
            # Returns
            Value or None - if a value, then the data is a base type and is replaced with the returned value; if a non-base type None is returned indicating no action is necessary
        '''
        # Get the rule.
        if rule_name is None: return(data)
        if rule_name == '__undefined__': return(data)
        if not rule_name in self.schema: raise Exception('Rule name "{}" not defined in schema.'.format(rule_name))
        schema_rule = self.schema[rule_name]

        # if node == 'Root.["Data"]["File Types"]["Excel"]':
        #     stop = True

        # Get the rule class.
        if not 'class' in schema_rule: raise Exception('Required attribute "class" not defined for schema rule "{}".'.format(rule_name))
        rule_class = str(schema_rule['class']).lower()
        
        # Get data type.
        data_type = type(data)
        object_type = data_type.__name__.capitalize()
        # object_type = ru.stype(data)

        ###

        # Data is base type (str, float, int, or bool)
        if rule_class == 'str' or rule_class == 'float' or rule_class == 'int' or rule_class == 'bool':

            cast_type = str
            if rule_class == 'float':
                cast_type = float
            elif rule_class == 'int':
                cast_type = int
            elif rule_class == 'bool':
                cast_type = bool
            elif rule_class == 'str':
                cast_type = str

            # Handle type casting, null assignment, default values, interposer functions etc.
            if data is None:
                allow_null = True if 'allow-null' in schema_rule and bool(schema_rule['allow-null']) else False
                # If data is None and there is a default specified, use the default value ...
                if 'default' in schema_rule:
                    data = cast_type(schema_rule['default'])
                # elif not default_value is None:
                #     data = default_value
                # If allow_null is True, simply return and allow the null value.
                elif allow_null:
                    return(None)
                # Otherwise, raise an exception.
                else:
                    raise Exception('Required {} value {} is not defined. (To fix this in the schema rule, specify allow-null = True or supply a default value.)'.format(cast_type.__name__, node))
            
            # The data_type may have changed, so update it.
            data_type = type(data)

            # If data_type doesn't match the desired type, re-cast it.
            if not data_type == cast_type:
                data = cast_type(data)

            # If an interposer function is specified, call it.  
            if 'validation-func' in schema_rule:
                func_name = schema_rule['validation-func']
                try:
                    arg = \
                    {
                        'object': self,
                        'data': self.data_object,
                        'rule': rule_name,
                        'node': node,
                        'nodes': nodes.copy(),
                        'depth': rule_name,
                        'parent': parent,
                        'parent_class': parent_class,
                    }
                    data = self.module_spec.__dict__[func_name](data, arg)
                except Exception as e:
                    error = re.sub(r'\s*(\.\?\!)', '', str(e)) 
                    raise Exception(error + " at {}.".format(node))

            # If 'min-value' attribute is defined, ensure that the value is greater than or equal
            # to the value indicated.
            if 'min-value' in schema_rule:
                min_value = float(schema_rule['min-value'])
                if data < min_value: 
                    raise Exception('{} object "{}" = {} must be greater than or equal to {}.'.format(object_type, node, data, min_value))

            # If 'max-value' attribute is defined, ensure that the value is less than or equal
            # to the value indicated.
            if 'max-value' in schema_rule:
                max_value = float(schema_rule['max-value'])
                if data > max_value: 
                    raise Exception('{} object "{}" = {} must be less than or equal to {}.'.format(object_type, node, data, max_value))

            # If 'matches' attribute is defined, ensure that the value matches the expression.
            if 'matches' in schema_rule:
                matches = str(schema_rule['matches'])
                rex = Rex()
                if rex.m(matches, r'^\s*\/(.*?)\/(.*?)\s*$'):
                    expression = rex.d(1)
                    flags = rex.d(2)
                    if not rex.m(data, expression, flags):
                        raise Exception('{} object {} = "{}" does not match {}.'.format(object_type, node, data, matches))
                elif not rex.m(data, matches, ''):
                    raise Exception('{} object {} = "{}" does not match {}.'.format(object_type, node, data, matches))

            # If 'in' attribute is defined, ensure that the value is in the designated list.
            if 'in' in schema_rule:
                if data not in schema_rule['in']:
                    raise Exception('{} object {} = "{}" not in [{}].'.format(object_type, node, data, '"' + '", "'.join(schema_rule['in']) + '"'))

            # If 'equals' attribute is defined, ensure that the value equals the value specified.
            if 'equals' in schema_rule:
                if not data == schema_rule['equals']:
                    raise Exception('{} object {} = "{}" does not equal "{}".'.format(object_type, node, data, schema_rule['equals']))

            return(data)

        ###
        
        # Process list and dict nodes.
        if data_type == list  or data_type == dict:
            # Get number of data elements.
            num_elements = len(data)

            # If an interposer function is specified, call it.  
            if 'pre-validation-func' in schema_rule:
                func_name = schema_rule['pre-validation-func']
                try:
                    arg = \
                    {
                        'object': self,
                        'data': self.data_object,
                        'rule': rule_name,
                        'node': node,
                        'nodes': nodes.copy(),
                        'depth': rule_name,
                        'parent': parent,
                        'parent_class': parent_class,
                    }
                    data = self.module_spec.__dict__[func_name](data, arg)
                except Exception as e:
                    error = re.sub(r'\s*(\.\?\!)', '', str(e)) 
                    raise Exception(error + " at {}.".format(node))
            
            # If 'min-count' attribute is defined, ensure that number of elements is greater than or
            # equal to the value indicated.
            if 'min-count' in schema_rule:
                min_count = schema_rule['min-count']
                text = '' if num_elements == 1 else 's'
                if num_elements < min_count: 
                    raise Exception('{} object "{}" has {} element{}. Minimum of {} required.'.format(object_type, node, num_elements, text, min_count))
            
            # If 'max-count' attribute is defined, ensure that number of elements is less than or
            # equal to the value indicated.
            if 'max-count' in schema_rule:
                max_count = schema_rule['max-count']
                text = '' if num_elements == 1 else 's'
                if num_elements > max_count: 
                    raise Exception('{} object "{}" has {} element{}. Maximum of {} allowed.'.format(object_type, node, num_elements, text, max_count))

            # Data is a list.
            if data_type == list and rule_class == 'list':
                
                # Recursively validate all list data elements.  
                i = 0
                for i, element in enumerate(data):
                    # for element in data:
                    child_node = '{}[{}]'.format(node, i)
                    child_nodes = nodes.copy()
                    child_nodes.append(i)
                    if self.debug_mode: print('Processing {} ...'.format(child_node))
                    if not 'rule' in schema_rule: schema_rule['rule'] = '__undefined__' 
                    rval = self.__validate_data_recursively(element, schema_rule['rule'], child_node, child_nodes, depth + 1, data, rule_class)
                    if not rval is None: data[i] = rval
                    i += 1

                # If an interposer function is specified, call it.  
                if 'post-validation-func' in schema_rule:
                    func_name = schema_rule['post-validation-func']
                    try:
                        arg = \
                        {
                            'object': self,
                            'data': self.data_object,
                            'rule': rule_name,
                            'node': node,
                            'nodes': nodes.copy(),
                            'depth': rule_name,
                            'parent': parent,
                            'parent_class': parent_class,
                        }
                        data = self.module_spec.__dict__[func_name](data, arg)
                    except Exception as e:
                        error = re.sub(r'\s*(\.\?\!)', '', str(e)) 
                        raise Exception(error + " at {}.".format(node))

                return(None)

            if data_type == list:
                i = 0

            # Data is a dict.
            if (data_type == dict and rule_class == 'dict'):                
                # Identify all required keys.  Stuff into required_key_not_yet_processed hash.  Once
                # the required key is processed, delete it from the list.  In the end, any required
                # keys still in the required_key_not_yet_processed hash will trigger exceptions.
                required_key_not_yet_processed = {}
                if 'keys' in schema_rule:
                    
                    for dict_valid_key_hash in schema_rule['keys']:
                        name = dict_valid_key_hash['name']
                        required = True if 'required' in dict_valid_key_hash and bool(dict_valid_key_hash['required']) else False
                        is_regx = True if 'regx' in dict_valid_key_hash and bool(dict_valid_key_hash['regx']) else False
                        # If regx is specified, the name cannot be required.  
                        if required and is_regx: required = False
                        if required: required_key_not_yet_processed[name] = True
                        # If required and the name is not in data, but a default value is specified
                        # in the rule, use it.
                        if required and not name in data:
                            if 'default' in dict_valid_key_hash:
                                data[name] = dict_valid_key_hash['default']
                            elif 'rule' in dict_valid_key_hash and dict_valid_key_hash['rule'] in self.schema:
                                child_rule = self.schema[dict_valid_key_hash['rule']]
                                if 'default' in child_rule:
                                    default_value = child_rule['default']
                                    default_value_type = ru.stype(default_value)
                                    # If not a base type, get a copy of the default value.
                                    if default_value_type == 'list' or default_value_type == 'dict':
                                        default_value = default_value.copy()
                                    data[name] = default_value

                    # Recursively validate all list data key-value pairs.  
                    for data_key in sorted(data.keys()):
                        match_found = False
                        # Cycle through all valid_keys_hashes and try to find a match for data_key.
                        for dict_valid_key_hash in schema_rule['keys']:
                            rule_key = dict_valid_key_hash['name']
                            is_regx = True if 'regx' in dict_valid_key_hash and bool(dict_valid_key_hash['regx']) else False
                            if (not is_regx and data_key == rule_key) or (is_regx and re.search(rule_key, data_key)):
                                if not is_regx and data_key in required_key_not_yet_processed: del required_key_not_yet_processed[data_key]
                                child_node = '{}'.format(node)
                                child_node += '["{}"]'.format(data_key)
                                if self.debug_mode: print('Processing {} ...'.format(child_node))
                                child_nodes = nodes.copy()
                                child_nodes.append(data_key)
                                if 'rule' in dict_valid_key_hash:
                                    rule_default_value = dict_valid_key_hash['default'] if 'default' in dict_valid_key_hash else None
                                    rval = self.__validate_data_recursively(data[data_key], dict_valid_key_hash['rule'], child_node, child_nodes, depth + 1, data, rule_class, default_value=rule_default_value)
                                    if not rval is None: data[data_key] = rval
                                match_found = True
                                break
                        if not match_found: raise Exception('Invalid entry "{}" found at node {}.'.format(data_key, node))

                # Are there any required_key_not_yet_processed entries?  If so, flag them as exceptions.
                required_keys = list(required_key_not_yet_processed.keys())

                if len(required_keys) == 1:
                    raise Exception('Required key "{}" at node {} not defined.'.format(required_keys[0], node))
                elif len(required_keys) > 1:
                    raise Exception('Required keys "{}" at node {} not defined.'.format('", "'.join(required_keys), node))            

                # If an interposer function is specified, call it.  
                if 'post-validation-func' in schema_rule:
                    func_name = schema_rule['post-validation-func']
                    try:
                        arg = \
                        {
                            'object': self,
                            'data': self.data_object,
                            'rule': rule_name,
                            'node': node,
                            'nodes': nodes.copy(),
                            'depth': rule_name,
                            'parent': parent,
                            'parent_class': parent_class,
                        }
                        data = self.module_spec.__dict__[func_name](data, arg)
                    except Exception as e:
                        error = re.sub(r'\s*(\.\?\!)', '', str(e)) 
                        raise Exception(error + " at {}.".format(node))

                return(None)

            if data_type == dict:
                i = 0

        # If we get here it means that there is an invalid data_type / rule_class combination. 
        raise Exception('Data node {} is of type {}. This cannot be reconciled with {}.'.format(node, data_type, rule_class))

    ##########

    def to_yaml(self, data, file=None):
        '''
            Render data in YML format.
            # Arguments
            - data: data object to be validated
            - file: file name to write; if none specified, return YML as string
            # Returns
            If file is not specified, returns the data encoded as YML. Otherwise, returns nothing.    
        '''
        # Initialize variables.
        rule_name = self.root_rule_name
        self.data_object = data
        self.lines = []

        # Add document separator ("---") if requested.
        if self.render.yaml.add_document_separator: self.lines.append('---' + "\n")
        
        # Output recurse.
        self.__to_yml_recurse(data, None, rule_name, rule_name, [], 0)

        # Do list compaction if requested.
        rex = Rex()
        if self.render.yaml.enable_list_compaction:
            remove_line_index = []
            for i, line in enumerate(self.lines):
                if rex.m(line, r'^(\s*)(-\s*)\n$', ''):
                    first_part = rex.d(1) + rex.d(2)
                    child_indent = '^' + " " * len(first_part)
                    if len(self.lines) > i+1 and rex.s(self.lines[i+1], child_indent, first_part):
                        self.lines[i+1] = rex.new
                        remove_line_index.append(i)
                elif rex.m(line, r'^(\s*)(-\s*)(\#.*?)\n$', ''):
                    first_part = rex.d(1) + rex.d(3)
                    child_indent = '^' + " " * len(first_part)
                    comment = rex.d(3) + "\n"
                    if len(self.lines) > i and rex.s(self.lines[i+1], child_indent, first_part):
                        self.lines[i+0] = comment
                        self.lines[i+1] = rex.new
            if len(remove_line_index) > 0:
                remove_line_index.reverse()
                for i in remove_line_index: self.lines.pop(i)

        # Return the data.
        return("".join(self.lines))
    
    ##########

    to_yml = to_yaml

    ##########

    def __to_yml_recurse(self, data, parent_data_key, rule_name, node, nodes, depth, collapse=False):
        '''
            Render data in YML format.
            # Arguments
            - data: data object to be validated
            - file: file name to write; if none specified, return YML as string
            # Returns
            If file is not specified, returns the data encoded as YML. Otherwise, returns nothing.    
        '''
        tab = ' ' * self.render.yaml.number_indent_spaces
        # list_tab = '-' + ' ' * (len(tab)-1)
        list_tab = '-' + ' '
        schema = self.schema
        rex = Rex()

        data_type = ru.stype(data)
        if rule_name == '__undefined__':
            schema_rule = {'class': data_type}
        elif not rule_name in schema: 
            raise Exception('Rule {} not defined in schema.'.format(rule_name))
        else:
            schema_rule = self.schema[rule_name]

        # Get the rule class.
        if not 'class' in schema_rule: raise Exception('Required attribute "class" not defined for schema rule "{}".'.format(rule_name))
        rule_class = str(schema_rule['class']).lower()

        # Discern render yaml rules.
        render = {}
        parent_collapse = False
        child_collapse = False
        if 'render' in schema_rule and 'yaml' in schema_rule['render']: render = schema_rule['render']['yaml']
        if 'collapse' in render and bool(render['collapse']): 
            if not collapse: parent_collapse = True
            collapse = True 
        if collapse and not parent_collapse: child_collapse = True        

        # Comments, padding and literals are disabled for collapsed child elements.
        if not child_collapse:
            # ... otherwise:
            # if 'comment' in schema_rule:
            #     pass
            if 'insert' in render:
                insert = rex.s(render['insert'], r'\n\s*$', '', '=')
                insert_lines = rex.split(insert, r'\n')
                for insert_line in insert_lines:
                    self.lines.append((tab * (depth-1)) + '{}'.format(insert_line) + "\n")
            if 'padding-before' in render and bool(render['padding-before']):
                item = self.lines.pop(-1)
                self.lines.append("\n")
                self.lines.append(item)
            if 'comment' in schema_rule:
                comment_arg = schema_rule['comment']
                if callable(comment_arg):
                    comment = comment_arg(parent_data_key, data)
                else:
                    comment = comment_arg
                    if comment.endswith('()'):
                        comment_temp = comment.replace('()', '')
                        if comment_temp.isidentifier():
                            comment = self.module_spec.__dict__[comment_temp](parent_data_key, data)
                comment = rex.s(comment, r'\n\s*$', '', '=')
                comment_lines = rex.split(comment, r'\n')
                for comment_line in comment_lines:
                    item = self.lines.pop(-1)
                    if not comment_line.startswith('#'): comment_line = '# ' + comment_line
                    self.lines.append((tab * (depth-1)) + comment_line + "\n")
                    self.lines.append(item)
                if 'padding-after-comment' in render and bool(render['padding-after-comment']):
                    item = self.lines.pop(-1)
                    self.lines.append("\n")
                    self.lines.append(item)
        
        while True:
            if data_type == 'list' and rule_class == 'list':
                i = 0
                number_of_entries = 0
                list_depth = depth - 1 if depth > 1 and not self.render.yaml.enable_list_inset else depth
                if collapse: 
                    if parent_collapse: 
                        self.lines[-1] = rex.s(self.lines[-1], r'\n$', '', 's=')
                        # self.lines.append((tab * list_depth) + tab)
                    self.lines.append('[')
                for element in data:
                    element_type = ru.stype(element)
                    # Render list items
                    if element_type == 'bool':
                        if collapse: self.lines[-1] += str(bool(element)) + ", "
                        else: self.lines.append((tab * list_depth) + list_tab + str(bool(element)) + "\n")
                    elif element_type == 'int' or element_type == 'float':
                        if collapse: self.lines[-1] += str(element) + ", "
                        else: self.lines.append((tab * list_depth) + list_tab + str(element) + "\n")
                    elif element_type == 'str':
                        if collapse: self.lines[-1] += self.__yml_quote_item(element, -1) + ", "
                        else: self.lines.append((tab * list_depth) + list_tab + self.__yml_quote_item(element, list_depth) + "\n")
                    else:
                        child_node = '{}[{}]'.format(node, i)
                        child_nodes = nodes.copy()
                        child_nodes.append(i)
                        if collapse:
                            if parent_collapse:
                                self.lines.append((tab * list_depth) + list_tab)
                            else:
                                self.lines[-1] += '['
                            self.__to_yml_recurse(element, None, schema_rule['rule'], child_node, child_nodes, list_depth + 1, collapse)
                        else:
                            self.lines.append((tab * list_depth) + list_tab + "\n")
                            self.__to_yml_recurse(element, None, schema_rule['rule'], child_node, child_nodes, list_depth + 1, collapse)
                    number_of_entries += 1
                    i += 1
                if collapse: 
                    self.lines[-1] = rex.s(self.lines[-1], r',\s*$', '', '=')
                    self.lines[-1]  += '], '
                    if parent_collapse: 
                        self.lines[-1] = rex.s(self.lines[-1], r',\s*$', '', '=')
                        if self.render.yaml.collapsed_line_length > 0:
                            wrapper = textwrap.TextWrapper()
                            wrapper.initial_indent = ''
                            wrapper.subsequent_indent = tab * (list_depth + 1) + '  '
                            wrapper.width = self.render.yaml.collapsed_line_length
                            new_lines = wrapper.wrap(self.lines[-1])
                            self.lines[-1] = "\n".join(new_lines)
                        self.lines[-1] += "\n"
                # If list has no elements, append [] to the parent element.
                elif number_of_entries == 0:
                    self.lines[-1] = self.lines[-1].rstrip() + ' []\n'
                break

            if data_type == 'dict' and rule_class == 'dict':
                number_of_entries = 0
                if collapse: 
                    if parent_collapse: 
                        self.lines[-1] = rex.s(self.lines[-1], r'\n$', '', 's=')
                        # self.lines.append(tab * depth)
                    self.lines.append('{')
                key_sort = None
                if 'key-sort-func' in schema_rule:
                    key_sort = schema_rule['key-sort-func']
                    if type(key_sort) == str:
                        if key_sort.startswith('str.'):
                            key_sort = eval(key_sort)
                        else:
                            key_sort = self.module_spec.__dict__[key_sort]
                if 'keys' in schema_rule:
                    valid_key_hashes = schema_rule['keys']
                    did_it = {}
                    valid_key_index = 0
                    for valid_key_hash in valid_key_hashes:
                        schema_key = valid_key_hash['name']
                        is_regx = True if 'regx' in valid_key_hash and bool(valid_key_hash['regx']) else False
                        for data_key in sorted(data.keys(), key=key_sort):
                            if data_key in did_it: continue
                            match0 = True if not is_regx and (data_key == schema_key) else False
                            match1 = True if is_regx and (rex.m(data_key, schema_key)) else False
                            if match0 or match1:
                                did_it[data_key] = True
                                child_rule_name = valid_key_hash['rule']
                                if not child_rule_name in schema: 
                                    raise Exception('Rule {} not defined in schema.'.format(child_rule_name))
                                child_rule = schema[child_rule_name]
                                child_node = '{}'.format(node)
                                child_node += '["{}"]'.format(data_key)
                                if self.debug_mode: print('Processing {} ...'.format(child_node))
                                child_nodes = nodes.copy()
                                child_nodes.append(data_key)
                                value = data[data_key]
                                value_type = ru.stype(value)
                                if value_type == 'bool':
                                    if collapse: self.lines[-1] += self.__yml_quote_key(data_key) + ": " + str(bool(value)) + ", "
                                    else: self.lines.append((tab * depth) + self.__yml_quote_key(data_key) + ": " + str(bool(value)) + "\n")
                                elif value_type == 'int' or value_type == 'float':
                                    if collapse: self.lines[-1] += self.__yml_quote_key(data_key) + ": " + str(value) + ", "
                                    else: self.lines.append((tab * depth) + self.__yml_quote_key(data_key) + ": " + str(value) + "\n")
                                elif value_type == 'str':
                                    if collapse: self.lines[-1] += self.__yml_quote_key(data_key) + ": " + self.__yml_quote_data_collapsed(value, depth) + ", "
                                    else: self.lines.append((tab * depth) + self.__yml_quote_key(data_key) + ": " + self.__yml_quote_data(value, depth) + "\n")
                                else:
                                    if collapse: self.lines[-1] += self.__yml_quote_key(data_key) + ": "
                                    else: self.lines.append((tab * depth) + self.__yml_quote_key(data_key) + ": " + "\n")
                                    self.__to_yml_recurse(value, data_key, child_rule_name, child_node, child_nodes, depth + 1, collapse)
                                number_of_entries += 1
                else:
                    for data_key in sorted(data.keys(), key=key_sort):
                        child_rule = '__undefined__'
                        child_rule_name = '__undefined__'
                        child_node = '{}'.format(node)
                        child_node += '["{}"]'.format(data_key)
                        if self.debug_mode: print('Processing {} ...'.format(child_node))
                        child_nodes = nodes.copy()
                        child_nodes.append(data_key)
                        value = data[data_key]
                        value_type = ru.stype(value)
                        if value_type == 'bool':
                            if collapse: self.lines[-1] += self.__yml_quote_key(data_key) + ": " + str(bool(value)) + ", "
                            else: self.lines.append((tab * depth) + self.__yml_quote_key(data_key) + ": " + str(bool(value)) + "\n")
                        elif value_type == 'int' or value_type == 'float':
                            if collapse: self.lines[-1] += self.__yml_quote_key(data_key) + ": " + str(value) + ", "
                            else: self.lines.append((tab * depth) + self.__yml_quote_key(data_key) + ": " + str(value) + "\n")
                        elif value_type == 'str':
                            if collapse: self.lines[-1] += self.__yml_quote_key(data_key) + ": " + self.__yml_quote_data_collapsed(value, depth) + ", "
                            else: self.lines.append((tab * depth) + self.__yml_quote_key(data_key) + ": " + self.__yml_quote_data(value, depth) + "\n")
                        else:
                            if collapse: self.lines[-1] += self.__yml_quote_key(data_key) + ": "
                            else: self.lines.append((tab * depth) + self.__yml_quote_key(data_key) + ": " + "\n")
                            self.__to_yml_recurse(value, data_key, child_rule_name, child_node, child_nodes, depth + 1, collapse)
                        number_of_entries += 1
                if collapse: 
                    self.lines[-1] = rex.s(self.lines[-1], r',\s*$', '', 's=')
                    self.lines[-1] += '}, '
                    if parent_collapse: 
                        self.lines[-1] = rex.s(self.lines[-1], r',\s*$', '', '=')
                        if self.render.yaml.collapsed_line_length > 0:
                            wrapper = textwrap.TextWrapper()
                            wrapper.initial_indent = ''
                            wrapper.subsequent_indent = tab * (depth + 1) + '  '
                            wrapper.width = self.render.yaml.collapsed_line_length
                            new_lines = wrapper.wrap(self.lines[-1])
                            self.lines[-1] = "\n".join(new_lines)
                        self.lines[-1] += "\n"
                # If dict has no keys, append {} to the parent element.
                elif number_of_entries == 0:
                    self.lines[-1] = self.lines[-1].rstrip() + ' {}\n'
                break

            # If data is None and 'allow-null' is True.
            if data is None:
                if 'allow-null' in schema_rule and bool(schema_rule['allow-null']):
                    self.lines[-1] = self.lines[-1].rstrip() + ' ~\n'
                    break

            # Special case.
            if data is None and rule_class == 'nonetype':
                break

            # If we get here, there's a problem!
            raise Exception('Data of type "{}" cannot be reconciled with schema "{}".'.format(data_type, rule_class))    
    
    def __yml_quote_key(self, value):
        rex = Rex()
        if rex.m(value, r'^\s+') or rex.m(value, r'\s+$') or rex.m(value, r'[:#\\]') or rex.m(value, r'^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$'):
            return(self.__yml_quote(value))
        return(value)
    
    def __yml_quote_data(self, value, level):
        if value is None: return('~')
        if level >= 0:
            rex = Rex()
            tab = ' ' * self.render.yaml.number_indent_spaces
            if rex.m(value, r'\n'):
                lines = rex.split(value, r'\n')
                for i,line in enumerate(lines):
                    lines[i] = (tab * (level+1)) + line
                value = '|\n' + '\n'.join(lines)
                value = rex.s(value, r'\s*\n\s*$', '', 's=')
                return(value)
            if len(value) == 0 or rex.m(value, r'^\s+') or rex.m(value, r'\s+$') or rex.m(value, r'^[\!\*]') or rex.m(value, r'[#\\:\']') or rex.m(value, r'^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$'):
                return(self.__yml_quote(value))
            return(value)
        else:
            return(self.__yml_quote(value))
    
    def __yml_quote_data_collapsed(self, value, level):
        if value is None: return('~')
        if level >= 0:
            rex = Rex()
            if rex.m(value, r'\n'):
                value = rex.s(value, r'\n\s*$', '', '=')
                return(self.__yml_quote(value, True))
            if len(value) == 0 or rex.m(value, r'^[\!\*]') or rex.m(value, r'[\s#\\:\']') or rex.m(value, r'^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$'):
                return(self.__yml_quote(value))
            return(value)
        else:
            return(self.__yml_quote(value))
    
    def __yml_quote_item(self, value, level):
        if value is None: return('~')
        rex = Rex()
        if level >= 0:
            tab = ' ' * self.render.yaml.number_indent_spaces
            if rex.m(value, r'\n'):
                lines = rex.split(value, r'\n')
                for i,line in enumerate(lines):
                    lines[i] = (tab * (level+2)) + line
                value = '|\n' + '\n'.join(lines)
                return(value)
            if rex.m(value, r'^\s+') or rex.m(value, r'\t') or rex.m(value, r'\s+$') or rex.m(value, r'^\W') or rex.m(value, r':') or rex.m(value, r"'") or rex.m(value, r'^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$'):
                return(self.__yml_quote(value))
            return(value)
        else:
            if rex.m(value, r'^\s+') or rex.m(value, r'\s+$') or rex.m(value, r'^\W') or rex.m(value, r':') or rex.m(value, r"'") or rex.m(value, r'^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$'):
                return(self.__yml_quote(value))
            return(value)

    def __yml_quote_item_collapsed(self, value, level):
        if value is None: return('~')
        rex = Rex()
        if level >= 0:
            tab = ' ' * self.render.yaml.number_indent_spaces
            if rex.m(value, r'\n'):
                lines = rex.split(value, r'\n')
                for i,line in enumerate(lines):
                    lines[i] = (tab * (level+2)) + line
                value = '|\n' + '\n'.join(lines)
                return(value)
            if rex.m(value, r'^\s+') or rex.m(value, r'\s+$') or rex.m(value, r'^\W') or rex.m(value, r':\s+') or rex.m(value, r"'") or rex.m(value, r'^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$'):
                return(self.__yml_quote(value))
            return(value)
        else:
            if rex.m(value, r'^\s+') or rex.m(value, r'\s+$') or rex.m(value, r'^\W') or rex.m(value, r':\s+') or rex.m(value, r"'") or rex.m(value, r'^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$'):
                return(self.__yml_quote(value))
            return(value)

    def __yml_quote(self, value, double_quote=False):
        rex = Rex()
        if self.render.yaml.enable_double_quote or double_quote:
            if rex.s(value, r"\"", r"\\\"", 'g'): value = rex.new
            if rex.s(value, r"\n", r"\\n", 'g'): value = rex.new
            value = "\"" + value + "\""
        else:
            if rex.s(value, r"'", r"''", 'g'): value = rex.new
            value = "'" + value + "'"
        return(value)



