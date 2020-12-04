# Data-Schema

Validate and render data.

## Quick Start

Let's start with a YAML file that looks like this:

```yaml
# File: sitcoms-data.yml
- Name: 'Modern Family'
  Rating: 4.2
  StillRunning: true
  CastMembers: 
    - {Character: 'Jay Pritchett', PlayedBy: 'Ed ONeill', Role: 'patriarch, father'}
    - {Character: 'Claire Dunphy', PlayedBy: 'Julie Brown', Role: 'Jay''s daughter'}
    - {Character: 'Mitchell Pritchett', PlayedBy: 'Jesse Tyler Ferguson', Role: 'Jay''s son'}
    - {Character: 'Phil Dunphy', PlayedBy: 'Ty Burrell', Role: 'Claire''s husband'}
  Networks:
    NBC: [monday, friday]
    ABC: [wednesday]
    TBS: [monday, thursday, friday]
  Reviews:
  - 'I love it!'
  - 'Never miss an episode.'
  - 'Early seasons were much better.'
  Episodes:
    S10 E16: Red Alert
    S11 E04: Pool Party
    S08 E22: The Graduates
    Others:
      xxx: 111
      yyy: 222
      zzz: 333
    
- Name: 'The Office'
  Rating: ~
  StillRunning: false
  CastMembers: 
    - {Character: 'Michael Scott', PlayedBy: 'Steve Carell', Role: 'manager'}
    - {Character: 'Jim Halpert', PlayedBy: 'John Krasinski', Role: 'salesman'}
    - {Character: 'Pam Beesly', PlayedBy: 'Jenna Fisher', Role: 'secretary'}
  Networks:
    ABC: [thursday]
    TBS: [tuesday, wednesday]
    OWN: [saturday, sunday]
```

It's easy enough to read this file with Python using the `yaml` module.  You'd just do something like this:

```python
import yaml

sitcoms = yaml.load(fs.read_file('sitcoms-data.yml', True), Loader=yaml.FullLoader)
```

The problem now, though, is two-fold:

1. Writing Python code to validate the data is cumbersome, painful.
2. Using the `yaml` module, there is no way to re-create the order and flow of the original YAML doc.

The `data.schema` module attempts to solve both of these problems.  Using this module, you can define a **schema** that both defines what the data must contain, and how it is to be rendered as YAML output.

### Schema - The "Rules" for Interpreting the Raw YAML Data

Here is the schema for this YAML input:

```yaml
# File: sitcoms-schema.yml
Sitcoms: 
    class: list
    rule: Sitcom
    root: true
    comment: Must See TV
Sitcom: 
    class: dict
    keys: 
    - {name: 'Name', rule: 'GenericValue', required: true, comment: 'Sitcom name'}
    - {name: 'Rating', rule: 'Rating', required: true}
    - {name: 'StillRunning', rule: 'Boolean', required: false}
    - {name: 'CastMembers', rule: 'CastMembers', required: true}
    - {name: 'Networks', rule: 'Network'}
    - {name: 'Reviews', rule: 'GenericList'}
    - {name: 'Episodes', rule: 'GenericDict'}
    - {name: 'Comment', rule: 'GenericValue'}
    default: {}
    comment: Sitcom
CastMembers: 
    class: list
    rule: CastMember
    default: []
    render: {yaml: {padding: true}}    
CastMember: 
    class: dict
    keys: 
    - {name: 'Character', rule: 'Person', required: true}
    - {name: 'PlayedBy', rule: 'Person', required: true}
    - {name: 'Role', rule: 'GenericValue', required: true}
    default: {}
    render: {yaml: {collapse: true}}    
Network: 
    class: dict
    keys:
    - {name: 'NBC', rule: 'Days', required: false}
    - {name: 'ABC', rule: 'Days', required: false}
    - {name: 'CBS', rule: 'Days', required: false}
    - {name: '\w+', regx: true, rule: 'Days', required: false}
Boolean: 
    class: bool
    default: false
Rating:
    class: float
    min-value: 0
    max-value: 5
    default: 2
    allow-null: true
Days: 
    class: list
    rule: Day
    render: {yaml: {collapse: true}}
GenericValue: 
    class: str
GenericList:
    class: list
    render: {yaml: {collapse: true}}    
GenericDict:
    class: dict
    render: {yaml: {collapse: true}}
Person: 
    class: str 
Day: 
    class: str
    validation-func : validate_day
```

The schema can also include Python interposer functions, defined in a separate file:

```python
# File: sitcoms-schema.py
days_of_week = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

def validate_day(value, info):
    value = value.lower().capitalize()
    if not value in days_of_week: raise Exception('Value "{}" is not a valid day. Must be one of: "{}"'.format(value, '", "'.join(days_of_week)))
    return(value)

```

### Deserialization 

So previously, I introduced code to do read the YAML input file that looked like this:

```python
import yaml

sitcoms = yaml.load(fs.read_file('sitcoms-data.yml', True), Loader=yaml.FullLoader)
```

When you convert YAML formatted data into an object, the action is called ***deserialization***.  

Now, let's add the code that handles validation:

```python
import yaml, fs
from data.schema import DataManager

sitcoms = yaml.load(fs.read_file('sitcoms-data.yml', True), Loader=yaml.FullLoader)
schema = yaml.load(fs.read_file('sitcoms-schema.yml', True), Loader=yaml.FullLoader)
dm = DataManager(schema, 'sitcoms-schema.py')
dm.validate(sitcoms)
```
If there are errors, the `validate()` method will throw an exception.

### Serialization

Want to render the `sitcoms` as YAML (an action called ***serialization***)?  Simple. Just do:

```python
text = dm.to_yaml(sitcoms)
print(text)
```

## Nodes

As the old saying goes, the devil is in the details.  Defining a schema is not hard.  But it does require knowing some basic `Data-Schema` syntax.

While your data object may be multidimensional, the scheme that defines it is only two dimensional.  Basically, every object in the data -- whether a `str`, `int`, `float`, `list` or `dict` -- is defined as a **node**.  

In `Data-Schema`, the top node is called the **root node**:

```yaml
Sitcoms: 
    class: list
    rule: Sitcom
    root: true
    comment: Must See TV
```

The root node must have a `root` attribute that is set to `true`.  

**NOTE**: In YAML, Boolean values are lower case (i.e. `true`, `false`), not upper case as they are in Python (i.e. `True`, `False`).  Python's `yaml` module (installed using `pip install pyyaml`) accepts both forms.  So you can get away with universally using `True` and `False` if you like.  I don't recommend this though.  Because if and when you render as YAML, it will use `true` and `false`.  

In addition to having a `root` attribute, the root node also defines a `class` attribute, in this case `list`.  The `class` value can be any base Python type: `str`, `int`, `float`, `list` or `dict`.

If the root node has child nodes -- which is almost always the case for your data -- then you identify the child node with the `rule` attribute.  Here, `rule` has a value of "Sitcom", which appears next in the schema:

```yaml
Sitcom: 
    class: dict
    keys: 
    - {name: 'Name', rule: 'GenericValue', required: true, comment: 'Sitcom name'}
    - {name: 'Rating', rule: 'Rating', required: true}
    - {name: 'StillRunning', rule: 'Boolean', required: false}
    - {name: 'CastMembers', rule: 'CastMembers', required: true}
    - {name: 'Networks', rule: 'Network'}
    - {name: 'Reviews', rule: 'GenericList'}
    - {name: 'Episodes', rule: 'GenericDict'}
    - {name: 'Comment', rule: 'GenericValue'}
    default: {}
    comment: Sitcom
```

The child node "Sitcom" has a `class` value of `dict`.  All `dict` nodes must define a `keys` object.  In the `keys` object, you define valid keys in the order that you want them to be rendered.  In this case, the first defined key is a required element that will have a name of "Name".  The key defines a child node defined by the "GenericValue" rule, which appears as yet another schema node.  

```yaml
GenericValue: 
    class: str
```

Notice there is no `rule` specified for "GenericValue".  This is because it is the terminating node for this data branch. This is reflected in the original data:

```yaml
- Name: 'Modern Family'
```

Using schema nodes simplifies the way we can talk about the data. There are other data validators that model the validation structure on the data structure.  In principal, this may seem like a good idea.  But the validation structure often has its own nested hierarchy of attributes and data structures.  This very quickly becomes unwieldy.  

## Dict Nodes

A `class` of "dict" can defined the following attributes:

- `keys` - Defines the keys for the `dict` object.
- `root` - True for the root node, false or undefined for all others.
- `default` - Default value if desired e.g. [].
- `min-count` - Minimum number of list elements allowed.
- `max-count` - Maximum number of list elements required.
- `render` - Special rules for rendered.  For example, "render: {yaml: {collapse: true}}" collapses the list to a single line e.g. "[1, 2, 3]".  
- `pre-validation-func` - Additional validation in the form of a function that (1) returns the data value if valid, or (2) throws an exception otherwise.  This validation is done before any other validation on the list object.  See below for additional information on pre-validation functions.
- `post-validation-func` - Additional validation in the form of a function that (1) returns the data value if valid, or (2) throws an exception otherwise.  This validation is done after other validation on the list object. See below for additional information on post-validation functions.
- `comment` - A comment that will be printed when rendered.  

### The "keys" Attribute

The `keys` attribute of the "dict" object takes a list of dictionary objects.  Example:

```yaml
Network: 
    class: dict
    keys:
    - {name: 'NBC', rule: 'Days', required: false}
    - {name: 'ABC', rule: 'Days', required: false}
    - {name: 'CBS', rule: 'Days', required: false}
    - {name: '\w+', regx: true, rule: 'Days', required: false}
```
Each dictionary object can define the following parameters:

- `name`: The expected key name for the data object.
- `rule`: The schema rule that defines the keyed data object.
- `regx`: Boolean value.  If true, the name value should be a regular expression e.g. '\w+'.  One important thing here ... If you are setting `regx` to `true`, you must set `required` equal to `false`.  The reason is that when you indicate that at key is required, that key name must appear in the dictionary, else an exception error is thrown.  But a regular expression like '\w+' doesn't represent the actual key value.  To test keys, and keyed data, for keys matched by regular expression, use the `pre-validation-func` and `post-validation-func` function specifiers in the parent dictionary object.  
- `required`: Boolean value.  If true, the key is required in the dictionary object.  NOTE: This attribute only checks to see that the key is *exists*.  It does not check to see if the data value specified for the key is *defined*.  You can check data values in the base `str`, `int`, `float` and `bool` nodes.
- `default`: Specify a default value.  


## List Nodes

A `class` of "list" can defined the following attributes:

- `rule` - Defines the node for all list elements.
- `root` - True for the root node, false or undefined for all others.
- `default` - Default value if desired e.g. [].
- `min-count` - Minimum number of list elements allowed.
- `max-count` - Maximum number of list elements required.
- `render` - Special rules for rendered.  For example, "render: {yaml: {collapse: true}}" collapses the list to a single line e.g. "[1, 2, 3]".  
- `pre-validation-func` - Additional validation in the form of a function that (1) returns the data value if valid, or (2) throws an exception otherwise.  This validation is done before any other validation on the list object. See below for additional information on pre-validation functions.
- `post-validation-func` - Additional validation in the form of a function that (1) returns the data value if valid, or (2) throws an exception otherwise.  This validation is done after other validation on the list object.  See below for additional information on post-validation functions.
- `comment` - A comment that will be printed when rendered.  

## String Nodes

A `class` of "str" can define the following attributes:

- `root` - True for the root node, false or undefined for all others.
- `default` - Specifies a default value if not defined.
- `allow-null` - If true, allow null values (in yaml: ~).
- `validation-func` - Additional validation in the form of a function that (1) returns the data value if valid, or (2) throws an exception otherwise.  See below for additional information on validation functions.
- `matches` - Value must match the specified regular expression.
- `in` - Value must be a member of the specified list.
- `equals` - Value must equal the specified value.
- `comment` - A comment that will be printed when rendered.

## Numeric Nodes

A `class` of "int" or "float" can define the following attributes:

- `root` - True for the root node, false or undefined for all others.
- `min-value` - Minimum allowed value.
- `max-value` - Maximum allowed value.
- `default` - Specifies a default value if not defined.
- `allow-null` - If true, allow null values (in yaml: ~).
- `validation-func` - Additional validation in the form of a function that (1) returns the data value if valid, or (2) throws an exception otherwise.  See below for additional information on validation functions.
- `comment` - A comment that will be printed when rendered.

## Bool Node

A `class` of type "bool" can define the following attributes:

- `root` - True for the root node, false or undefined for all others.
- `default` - Specifies a default value if not defined.
- `allow-null` - If true, allow null values (in yaml: ~).
- `validation-func` - Additional validation in the form of a function that (1) returns the data value if valid, or (2) throws an exception otherwise.  See below for additional information on validation functions.
- `comment` - A comment that will be printed when rendered.

## Validation Functions

Pre- and post-validation functions (`pre-validation-func` and `post-validation-func`) are used by lists and dictionaries to do additional validation on the node object.  The `pre-validation-func` function is applied before validation of the data, the `post-validation-func` function is applied after.

The `validation-func` function is used for validation of base type classes: `str`, `int`, `float` and `bool`.

For example:

```python
days_of_week = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

def validate_day(value, obj):
    value = value.lower().capitalize()
    if not value in days_of_week: raise Exception('Value "{}" is not a valid day. Must be one of: "{}"'.format(value, '", "'.join(days_of_week)))
    return(value)
```

To see how validation works, change the data in the example so that "thursday" in list:

```yaml
  Networks:
    NBC: [monday, friday]
    ABC: [wednesday]
    TBS: [monday, thursday, friday]
```

to "blursday":

```yaml
  Networks:
    NBC: [monday, friday]
    ABC: [wednesday]
    TBS: [monday, blursday, friday]
```

Now, when you attempt to validate your data, you get:

```
Exception: Value "Blursday" is not a valid day. Must be one of: "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday" at Sitcoms[0]["Networks"]["TBS"][1].
```

Note that, in addition to *validating* data, you can also *edit* it.  In particular, the days specified in the raw data YAML were all lower case.  But the output data is upper case.  In line 1 of the function:

```python
value = value.lower().capitalize()
```

we take the value and modify it.  Then, on the last line of the function, we return the modified value:

```python
return(value)
```

The other thing to note with the return data is that the exception automatically appends the string 'at Sitcoms[0]["Networks"]["TBS"][1]' to the error message.  For this reason it is recommended that you leave punctuation off the error message list.  

But what about the unused `info` argument in the function prototype?

```python
def validate_day(value, info):
```

Good question!  In most cases you can get by with just passing `value`.  But `info` gives you additional information.  It is a `dict` object that maps the following keys: 

- `data` - The full data object.  Use this in case you need to get data from somewhere else in the data object to do validation.  WARNING: Do not modify data from other parts of the data object here.  It can have unpredictable results, primarily because you can't know if data elsewhere has already been validated or not.  And if validated, it could have been changed.
- `node` - A human readable string giving you the position of the node.  For the above example, you get the following: 'Sitcoms[0]["Networks"]["TBS"][1]'.  You can use this value to give a more meaningful indication in error messaged of exactly where the error occurred.  NOTE: This value is automatically appended to error messages as " at " + `node` + ".".
- `nodes` - The list view of the `node` parameter.  For the above example, it would be [0, 'Networks', 'NBC', 1].
- `rule` - Failing rule name.  Note, this is the name of the schema node, so it may not (and probably doesn't) correspond to anything in the raw data stream.
- `parent` - The parent data object.  In the above example, it would return [monday, blursday, friday].
- `parent_class` - The class, or base type, of the parent node.  In the above example, this would be "list".

## Rendering

The last piece of the puzzle, once you have imported and validated data, is to render is back as YAML (serialization).  

```python
text = dm.to_yml(sitcoms)
print(fs.write_file_if_changed('sitcoms-data-out.yml', text))
```
If you do this, the output file looks like this:

```yaml
# Must See TV
---
# Sitcom
- Name: Modern Family
  Rating: 4.2
  StillRunning: True
  CastMembers: 
  - {Character: 'Jay Pritchett', PlayedBy: 'Ed ONeill', Role: 'patriarch, father'}
  - {Character: 'Claire Dunphy', PlayedBy: 'Julie Brown', Role: 'Jay''s daughter'}
  - {Character: 'Mitchell Pritchett', PlayedBy: 'Jesse Tyler Ferguson', Role: 'Jay''s son'}
  - {Character: 'Phil Dunphy', PlayedBy: 'Ty Burrell', Role: 'Claire''s husband'}
  Networks: 
    NBC: [Monday, Friday]
    ABC: [Wednesday]
    TBS: [Monday, Thursday, Friday]
  Reviews: [I love it!, Never miss an episode., Early seasons were much better.]
  Episodes: {Others: {xxx: 111, yyy: 222, zzz: 333}, S08 E22: 'The Graduates', S10 E16: 'Red Alert', S11 E04: 'Pool Party'}
# Sitcom
- Name: The Office
  Rating: 2.0
  StillRunning: False
  CastMembers: 
  - {Character: 'Michael Scott', PlayedBy: 'Steve Carell', Role: manager}
  - {Character: 'Jim Halpert', PlayedBy: 'John Krasinski', Role: salesman}
  - {Character: 'Pam Beesly', PlayedBy: 'Jenna Fisher', Role: secretary}
  Networks: 
    ABC: [Thursday]
    OWN: [Saturday, Sunday]
    TBS: [Tuesday, Wednesday]
```

## Using the Render Parameter

The `dict` and `list` class nodes can populate and use the `render` attribute.  The general format for its use is:

```yaml
render:
  PROTOCOL:
    OPTION-0: VALUE-0
    OPTION-1: VALUE-1
    ...
    OPTION-n: VALUE-n
```

Currently, **Data-Schema** only supports one rendering protocol, and that is YAML.  There are a handful of options available:

- `padding-before`: Boolean value.  If true, insert a newline before the rendered YAML for the object.
- `padding-after-comment`: Boolean value.  If true, insert a newline after the comment, if one is specified.
- `collapse`: Boolean value.  If true, collapse the list or dict to a single line. 

Here is an example:

```yaml
render: {yaml: {collapse: true, padding-before: true}}
```
## Known Issues

If you do `render: {yaml: {collapse: true}}` on a list, the rendering may not generate correct YAML.  For example:

```yaml
Scrub:
- Trim()
- Match(r"^\d+$", msg="a positive integer (e.g. \"0\", \"2\", etc.)")
- CastInt()
- InRange(0, 31)
```

If you collapse this list, the rendered YAML output will be:

```yaml
Scrub: [Trim(), Match(r"^\d+$", msg="a positive integer (e.g. \"0\", \"2\", etc.)"), CastInt(), InRange(0, 31)]
```

But this rendering introduces unquoted commas into the list.  So if the data is loaded again using the YAML parser:

In other words, `render: {yaml: {collapse: true}}` needs to treat list data different than `render: {yaml: {collapse: false}}`.  Currently, it does not do so.  The equivalent Python list you end up with is:

```python
"Scrub": [
  "Trim()", 
  "Match(r\"^\\d+$\"", 
  "msg=\"a positive integer (e.g. \\\"0\\\"", 
  "\\\"2\\\"", 
  "etc.)\")", 
  "CastInt()", 
  "InRange(0", 
  "31)"
]
```

The collapsed format should have been rendered as:

```yaml
Scrub: [Trim(), 'Match(r"^\d+$", msg="a positive integer (e.g. \"0\", \"2\", etc.)")', CastInt(), 'InRange(0, 31)']
```

