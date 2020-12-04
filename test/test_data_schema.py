import fs
from data.schema import DataManager
import yaml
import ru

import unittest

dir = fs.get_dir_name(fs.get_abs_path(__file__))


class TestRex(unittest.TestCase):

    def test_001_example(self):
        self.data_schema_test('demo1')
        self.assertEqual(str(self.dm), 'DataManager')
        # Test rel module file path resolution.
        schema_py_file_rel = fs.get_rel_path(self.schema_py_file, fs.get_script_dir())
        schema = yaml.load(self.schema_yml_file_content, Loader=yaml.FullLoader)
        dm = DataManager(schema, schema_py_file_rel)
        schema_py_file_rel = fs.join_names('does_not_exist', schema_py_file_rel)
        # Test exception handling.
        with self.assertRaises(Exception): DataManager(schema, schema_py_file_rel)
        with self.assertRaises(Exception): DataManager(None)
        with self.assertRaises(Exception): DataManager([])
        with self.assertRaises(Exception): DataManager({})
        mod_schema = yaml.load(yaml.dump(schema, Dumper=yaml.SafeDumper), Loader=yaml.FullLoader)
        del mod_schema['Root']['root']
        with self.assertRaises(Exception): DataManager(mod_schema, root_rule_name=None)
        with self.assertRaises(Exception): DataManager(mod_schema, root_rule_name='xxx')

    def test_002_sitcoms(self):
        self.data_schema_test('demo2')
    
    def test_003_exceptions(self):
        pass

    def test_004_misc(self):
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