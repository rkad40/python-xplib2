from rex import Rex

import unittest
import re

str0 = '''
This is a test.
This is only a test.
Test this!
Test that!
'''

str1 = '''
This is a test.
This is only a test.
Foobar this!
Foobar that!
'''

poem = '''
Oh my beloved belly button.
The squidgy ring in my midriff mutton.
Your mystery is such tricky stuff:
Why are you so full of fluff?
'''
# Source: https://www.familyfriendpoems.com/poems/funny/short/

class TestRex(unittest.TestCase):

    def test_001_simple_match(self):
        # r'Simple match case 1 (no groups, single match search)'
        rex = Rex()
        s0 = 'My favorite color is blue.  My favorite number is 7.'
        result = rex.m(s0, r'favorite\s+\w+\s+is\s+\w+')
        self.assertTrue(result)
        self.assertTrue(rex.result)
        self.assertEqual(rex.flags, 0)
        self.assertEqual(rex.sets(), 1)
        self.assertEqual(len(rex.matrix), 1)
        self.assertEqual(rex.cnt(), 1)
        self.assertEqual(rex.cnt(0), 1)
        self.assertEqual(rex.cnt(1), 0)
        self.assertEqual(rex.i, 0)
        self.assertEqual(rex.d(0), 'favorite color is blue')
        self.assertEqual(rex.d(0, 0), 'favorite color is blue')
        rex.next()
        self.assertEqual(rex.cnt(), 0)
        self.assertEqual(rex.i, 1)
        self.assertIsNone(rex.d(0))

    def test_002_simple_no_match(self):
        # r'Simple no match case 1 (no groups, single match search)'
        rex = Rex()
        s0 = 'My favorite color is blue.  My favorite number is 7.'
        result = rex.m(s0, r'most hated\s+\w+\s+is\s+\w+')
        self.assertFalse(result)
        self.assertFalse(rex.result)
        self.assertEqual(rex.flags, 0)
        self.assertEqual(rex.sets(), 0)
        self.assertEqual(len(rex.matrix), 0)
        self.assertEqual(rex.cnt(), 0)
        self.assertEqual(rex.cnt(0), 0)
        self.assertEqual(rex.cnt(1), 0)
        self.assertEqual(rex.i, 0)
        self.assertIsNone(rex.d(0))
        rex.next()
        self.assertEqual(rex.cnt(), 0)
        self.assertEqual(rex.i, 1)
        self.assertIsNone(rex.d(0))

    def test_003_group_match(self):
        # r'Group match case 1 (with groups, single match search)'
        rex = Rex()
        s0 = 'My favorite color is blue.  My favorite number is 7.'
        result = rex.m(s0, r'(favorite\s+(\w+)\s+is\s+(\w+))')
        self.assertTrue(result)
        self.assertTrue(rex.result)
        self.assertEqual(rex.flags, 0)
        self.assertEqual(rex.sets(), 1)
        self.assertEqual(rex.cnt(), 4)
        self.assertEqual(rex.cnt(0), 4)
        self.assertEqual(rex.cnt(1), 0)
        self.assertEqual(rex.i, 0)
        self.assertEqual(rex.d(0), 'favorite color is blue')
        self.assertEqual(rex.d(1), 'favorite color is blue')
        self.assertEqual(rex.d(2), 'color')
        self.assertEqual(rex.d(3), 'blue')
        self.assertEqual(rex.d(0, 0), 'favorite color is blue')
        self.assertEqual(rex.d(0, 1), 'favorite color is blue')
        self.assertEqual(rex.d(0, 2), 'color')
        self.assertEqual(rex.d(0, 3), 'blue')
        rex.next()
        self.assertEqual(rex.cnt(), 0)
        self.assertIsNone(rex.d(0))

    def test_004_group_match(self):
        # r'Group match case 2 (with groups, global match search)'
        rex = Rex()
        s0 = 'My favorite color is blue.  My favorite number is 7.'
        result = rex.m(s0, r'(favorite\s+(\w+)\s+is\s+(\w+))', 'g')
        self.assertTrue(result)
        self.assertTrue(rex.result)
        self.assertEqual(rex.flags, 0)
        self.assertEqual(rex.sets(), 2)
        self.assertEqual(rex.cnt(), 4)
        self.assertEqual(rex.cnt(0), 4)
        self.assertEqual(rex.cnt(1), 4)
        self.assertEqual(rex.i, 0)
        self.assertEqual(rex.d(0), 'favorite color is blue')
        self.assertEqual(rex.d(1), 'favorite color is blue')
        self.assertEqual(rex.d(2), 'color')
        self.assertEqual(rex.d(3), 'blue')
        self.assertEqual(rex.d(0, 0), 'favorite color is blue')
        self.assertEqual(rex.d(0, 1), 'favorite color is blue')
        self.assertEqual(rex.d(0, 2), 'color')
        self.assertEqual(rex.d(0, 3), 'blue')
        rex.next()
        self.assertEqual(rex.d(0), 'favorite number is 7')
        self.assertEqual(rex.d(1), 'favorite number is 7')
        self.assertEqual(rex.d(2), 'number')
        self.assertEqual(rex.d(3), '7')
        self.assertEqual(rex.d(1, 0), 'favorite number is 7')
        self.assertEqual(rex.d(1, 1), 'favorite number is 7')
        self.assertEqual(rex.d(1, 2), 'number')
        self.assertEqual(rex.d(1, 3), '7')
        rex.next()
        self.assertEqual(rex.cnt(), 0)
        self.assertIsNone(rex.d(0))

    def test_005_match_options(self):
        # r'Group match options test 1'
        rex = Rex()    
        self.assertTrue(rex.m(poem, r'RING', 'i'))
        self.assertTrue(rex.m(poem, r'ring', ''))
        self.assertFalse(rex.m(poem, r'RING', ''))
        self.assertTrue(rex.m(poem, r'^Your', 'm'))
        self.assertFalse(rex.m(poem, r'^Your', ''))
        self.assertTrue(rex.m(poem, r'mutton\..*?Your', 's'))
        self.assertFalse(rex.m(poem, r'mutton\..*?Your', ''))
        with self.assertRaises(Exception): rex.m(poem, r'RING', 'smigx')

    def test_006_split(self):
        # r'''Split string test 1'''
        rex = Rex()
        old = '1,2, 3, 4,5 ,6'
        new = rex.split(old, r'\s*,\s*')
        exp = ['1','2','3','4','5','6']
        self.assertEqual(new, exp)

    def test_007_or_match_expression(self):
        # r'''OR match expressions test 1'''
        rex = Rex()
        s0 = "The rain in Spain ain't stopping nobody."
        rex.m(s0, r'xxx') or rex.m(s0, r'\b(\w*?ai.*?)\b', 'i') or rex.m(s0, r'xxx')
        self.assertTrue(rex.result)
        self.assertEqual(rex.d(0), 'rain')
        self.assertEqual(rex.d(1), 'rain')

    def test_008_or_match_expression(self):
        # r'''OR match expressions test 2'''
        rex = Rex()
        s0 = "The rain in Spain ain't stopping nobody."
        rex.m(s0, r'xxx') or rex.m(s0, r'\b(\w*?ai\w*?)\b', 'ig') or rex.m(s0, r'xxx')
        self.assertTrue(rex.result)
        self.assertEqual(rex.d(0, 1), 'rain')
        self.assertEqual(rex.d(1, 1), 'Spain')
        self.assertEqual(rex.d(2, 1), 'ain')
        self.assertIsNone(rex.d(3, 1))

    def test_009_replace_with_backslash_1(self):
        # r'Do replace using inline "\1" variable.'
        rex = Rex()
        s0 = "The rain in Spain ain't stopping nobody."
        s1 = "The rain in Madrid, Spain ain't stopping nobody."
        s2 = rex.s(s0, r'(S\w+n)', r'Madrid, \1', '=')
        self.assertEqual(s2, s1)    
        self.assertEqual(rex.cnt(), 2)
        self.assertEqual(rex.d(0), 'Spain')
        self.assertTrue(rex.s(s0, r'(s\w+n)', r'Madrid, \1', 'i'))
        self.assertEqual(rex.new, s1)
        self.assertFalse(rex.s(s0, r'(xxx)', r'Madrid, \1', ''))

    def test_010_replace_using_func(self):
        def replace_country(m):
            if m[1] == 'Canada': return('Montreal')
            if m[1] == 'Spain': return('Madrid')
            if m[1] == 'Germany': return('Berlin')
            return('Timbuktu')
        rex = Rex()
        s0 = "The rain in Spain ain't stopping nobody."
        s1 = "The rain in Madrid ain't stopping nobody."
        s2 = rex.s(s0, r'(Canada|Spain|Germany)', replace_country, '=')
        self.assertEqual(s2, s1)
        s0 = "Cities of the world: Spain, Canada, Germany, Mexico"
        s1 = "Cities of the world: Madrid, Montreal, Berlin, Timbuktu"
        s2 = rex.s(s0, r'(Canada|Spain|Mexico|Germany)', replace_country, 'g=')
        self.assertEqual(s2, s1)
        s0 = "Cities of the world: Spain, Canada, Germany, Mexico"
        s2 = rex.s(s0, r'xxx', replace_country, 'g=')
        self.assertEqual(s2, s0)

    def test_011_sub_options(self):
        # r'Group match options test 1'
        rex = Rex()
        s0 = 'aaa bbb\nccc ddd\neee fff\nggg hhh'
        self.assertTrue(rex.s(s0, r'AAA', '---', 'i')); s0 = rex.new
        self.assertTrue(rex.s(s0, r'bbb', '---', '')); s0 = rex.new
        self.assertTrue(rex.s(s0, r'^ccc', '---', 'm')); s0 = rex.new
        self.assertFalse(rex.s(s0, r'^ddd', '---', '')); s0 = rex.new
        self.assertTrue(rex.s(s0, r'ddd.*eee', '---', 's')); s0 = rex.new
        self.assertFalse(rex.s(s0, r'fff.*ggg', '---', '')); s0 = rex.new
        with self.assertRaises(Exception): rex.s(s0, r'hhh', '---', 'smigx'); s0 = rex.new
        self.assertEqual(s0, '--- ---\n--- --- fff\nggg hhh')
    
    def test_012_sub_options(self):
        # r'Group match options test 1'
        rex = Rex()
        s0 = '0123 456 789 01 2 345 6 789'
        s1 = rex.s(s0, '(\d+)', '-', 'g=')
        self.assertEqual(s1, '- - - - - - - -')
        self.assertEqual(rex.d(0), '0123')

    def test_013_trim_spaces(self):
        # r'''Trim spaces'''
        rex = Rex()
        name = 'trim spaces'
        old = ' This is a test.   '
        cmp = 'This is a test.'
        new = rex.s(old, r'^\s*(.*?)\s*$', r'\1', '=')
        self.assertEqual(new, cmp)       
        old = ' This is a test.   '
        cmp = 'This is a test.'
        new = rex.trim(old)
        self.assertEqual(new, cmp)       

    def test_014_unquote(self):
        # r'''Unquote'''
        rex = Rex()
        old = ' "This is a test."   '
        cmp = 'This is a test.'
        new = rex.s(old, r'^\s*(\'|\")(.*?)\1\s*$', r'\2', '=')
        self.assertEqual(new, cmp)       
        old = ' "This is a test."   '
        cmp = 'This is a test.'
        new = rex.unquote(old)
        self.assertEqual(new, cmp)      

    def test_015_escape(self):
        rex = Rex()
        val = rex.escape(r'^\1')
        self.assertEqual(val, r'\^\\1')   

    def test_016_while_loop_sub(self):
        # This test is coverage for a bug in version 1.000 of rex.py.  The sub() method was never 
        # returning True for single instance with a replace function.  
        rex = Rex()
        original = "=A4+2*C10"
        expected = "=xxx+2*xxx"
        def replace_first_pass(m): return 'xxx'
        # This test, without a replace function, was passing in 1.000.
        old = original
        new = original
        while rex.s(new, r'(\!{0,1})\${0,1}([a-zA-Z]{1,3})\${0,1}(\d+)', 'xxx', ''):
            new = rex.new
        self.assertEqual(new, expected)
        # This test, with a replace function, was failing in 1.000.
        old = original
        new = original
        while rex.s(new, r'(\!{0,1})\${0,1}([a-zA-Z]{1,3})\${0,1}(\d+)', replace_first_pass, ''):
            new = rex.new
        self.assertEqual(new, expected)
        # In this version, sub() with replace function should fail first match attempt.
        old = original
        new = original
        while rex.s(new, r'(\!{1})\${0,1}([a-zA-Z]{1,3})\${0,1}(\d+)', replace_first_pass, ''):
            new = rex.new
        self.assertNotEqual(new, expected)

if __name__ == '__main__': # pragma: no cover
    unittest.main()
