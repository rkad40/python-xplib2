import fs
from data.schema import DataManager
import yaml
import ru

import unittest

dir = fs.get_dir_name(fs.get_abs_path(__file__))
DataManager.coverage_testing = True

class TestRex(unittest.TestCase):

    def test_001_example(self):
        self.data_schema_test('demo1')
        self.assertEqual(str(self.dm), '<DataManager>')
        # Test rel module file path resolution.
        schema_py_file_rel = fs.get_rel_path(self.schema_py_file, fs.get_script_dir())
        schema = yaml.load(self.schema_yml_file_content, Loader=yaml.FullLoader)
        dm = DataManager(schema, schema_py_file_rel)
        # Test exception handling.
        # Affirm exception for non-existing schema module.
        with self.assertRaises(Exception): DataManager(schema, 'not_a_file_' + schema_py_file_rel)
        # Affirm exception if schema is not defined.
        with self.assertRaises(Exception): DataManager()
        # Affirm exception if schema is None.
        with self.assertRaises(Exception): DataManager(None)
        # Affirm exception if schema is a list.
        with self.assertRaises(Exception): DataManager([])
        # Affirm exception if schema is an empty hash.
        with self.assertRaises(Exception): DataManager({})
        mod_schema = yaml.load(yaml.dump(schema, Dumper=yaml.SafeDumper), Loader=yaml.FullLoader)
        del mod_schema['Root']['root']
        # Affirm exception if no root node is specified.
        with self.assertRaises(Exception): DataManager(mod_schema, root_rule_name=None)
        # Affirm exception if non-existing root node is specified.
        with self.assertRaises(Exception): DataManager(mod_schema, root_rule_name='xxx')
        # Test no module specified.
        self.dm = DataManager(schema)
        # Test no module specified.
        self.dm = DataManager(schema)
        # Test class attribute print_warnings.
        DataManager.print_warnings = False
        self.dm = DataManager(schema)
        DataManager.print_warnings = True
        # Test fake rule.
        mod_schema = yaml.load(yaml.dump(schema, Dumper=yaml.SafeDumper), Loader=yaml.FullLoader)
        mod_schema['FakeRule'] = {'class': 'dict'}
        self.dm = DataManager(mod_schema)
        mod_schema['AnotherFakeRule'] = {'class': 'dict'}
        self.dm = DataManager(mod_schema)

    def test_002_sitcoms(self):
        self.data_schema_test('demo2')
    
    def test_003_miscellaneous(self):
        self.data_schema_test('demo3')
        schema = yaml.load(self.schema_yml_file_content, Loader=yaml.FullLoader)
        mod_schema = yaml.load(yaml.dump(schema, Dumper=yaml.SafeDumper), Loader=yaml.FullLoader)
        dm = DataManager(mod_schema, self.schema_py_file)
        dm.validate(self.data)
        # Test 'min-value' and 'max-value' validators.
        mod_schema = yaml.load(yaml.dump(schema, Dumper=yaml.SafeDumper), Loader=yaml.FullLoader)
        mod_schema['Integer']['min-value'] = 30
        dm = DataManager(mod_schema, self.schema_py_file)
        with self.assertRaises(Exception): dm.validate(self.data)
        mod_schema['Integer']['min-value'] = 20
        mod_schema['Integer']['max-value'] = 25
        dm = DataManager(mod_schema, self.schema_py_file)
        with self.assertRaises(Exception): dm.validate(self.data)
        # Test 'matches' validator.
        mod_schema = yaml.load(yaml.dump(schema, Dumper=yaml.SafeDumper), Loader=yaml.FullLoader)
        data = yaml.load(yaml.dump(self.data, Dumper=yaml.SafeDumper), Loader=yaml.FullLoader)
        data['Color'] = 'green'
        dm = DataManager(mod_schema, self.schema_py_file)
        with self.assertRaises(Exception): dm.validate(data)
        mod_schema['Color']['matches'] = '/GREEN/i'
        mod_schema['Color']['equals'] = 'green'
        dm = DataManager(mod_schema, self.schema_py_file)
        dm.validate(data)
        mod_schema['Color']['matches'] = '/black/i'
        with self.assertRaises(Exception): dm.validate(data)
    
    def test_004_exceptions(self):
        pass

    def test_005_misc(self):
        pass

    def data_schema_test(self, name):
        # Defined file names.  
        self.schema_yml_file = fs.join_names(dir, 'data-schema', f'{name}-schema.yml')
        self.schema_py_file = fs.join_names(dir, 'data-schema', f'{name}-schema.py')
        self.src_data_yml_file = fs.join_names(dir, 'data-schema', f'{name}-data.yml')
        self.tar_data_yml_file = fs.join_names(dir, 'data-schema', 'target', f'{name}-data.yml')
        self.exp_data_yml_file = fs.join_names(dir, 'data-schema', 'expect', f'{name}-data.yml')
        # Get schema data.
        self.schema_yml_file_content = fs.read_file(self.schema_yml_file, True)
        self.schema = yaml.load(self.schema_yml_file_content, Loader=yaml.FullLoader)
        # Get source data.  
        self.src_data_yml_file_content = fs.read_file(self.src_data_yml_file, True)
        self.data = yaml.load(self.src_data_yml_file_content, Loader=yaml.FullLoader)
        # Validate the data.
        self.dm = DataManager(self.schema, self.schema_py_file)
        is_valid = True
        try: self.dm.validate(self.data)
        except: is_valid = False
        self.assertTrue(is_valid)
        # Write output YML file.
        tar_data_yml_file_content1 = self.dm.to_yml(self.data)
        fs.write_file_if_changed(self.tar_data_yml_file, tar_data_yml_file_content1)
        # Validate the validated YML content.
        data = yaml.load(tar_data_yml_file_content1, Loader=yaml.FullLoader)
        is_valid = True
        try: self.dm.validate(data)
        except: is_valid = False
        self.assertTrue(is_valid)
        tar_data_yml_file_content2 = self.dm.to_yml(data)
        self.assertTrue(tar_data_yml_file_content1 == tar_data_yml_file_content2)
        # Compare against saved expect file.
        self.exp_data_yml_file_content = fs.read_file(self.exp_data_yml_file, True)
        self.assertTrue(tar_data_yml_file_content1 == self.exp_data_yml_file_content)



if __name__ == '__main__': # pragma: no cover
    unittest.main()