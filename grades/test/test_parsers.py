#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
Test table parsers.

"""


__author__ = "Loïc Séguin-C. <loicseguin@gmail.com>"
__license__ = "BSD"


from nose.tools import assert_equal
try:
    import cStringIO as io
except ImportError:
    try:
        import StringIO as io
    except ImportError:
        import io  # For Python 3
from grades import parsers



class TestParsers:
    """Define some tables to test if they are parsed correctly."""
    rst_grid_table = """\
+------------------+-------+--------+--------+---------+
| Name             | Group | Test 1 | Test 2 | Midterm |
|                  |       +--------+--------+---------+
|                  |       | 70     | 100.00 | 100.00  |
|                  |       +--------+--------+---------+
|                  |       | 30.00  | 30     | 40.00   |
+==================+=======+========+========+=========+
| Bob Arthur       | 301   | 23.00  | 45.00  |         |
+------------------+-------+--------+--------+---------+
| Suzanne Tremblay | 301   | 67     | 78.00  | 80.00   |
+------------------+-------+--------+--------+---------+
| Albert Prévert   | 302   |        | ABS    | 78.00   |
+------------------+-------+--------+--------+---------+
"""

    org_table = """\
| Name             | Group | Test 1 | Test 2 | Midterm |
|                  |       |  70    | 100.00 |  100.00 |
|                  |       |  30.00 |  30    |   40.00 |
|------------------+-------+--------+--------+---------|
| Bob Arthur       | 301   |  23.00 |  45.00 |         |
| Suzanne Tremblay | 301   |  67    |  78.00 |   80.00 |
| Albert Prévert   | 302   |        | ABS    |   78.00 |
"""

    test1 = {'max_grade': 70., 'weight': 30.}
    test2 = {'max_grade': 100., 'weight': 30.}
    midterm = {'max_grade': 100., 'weight': 40.}
    columns = [
            {'title': 'Name', 'is_num': False, 'evalu': None, 'width': 0,
                'to_print': True},
            {'title': 'Group', 'is_num': False, 'evalu': None,
                'width': 0, 'to_print': True},
            {'title': 'Test 1', 'is_num': True, 'evalu': test1,
                'width': 0, 'to_print': True},
            {'title': 'Test 2', 'is_num': True, 'evalu': test2,
                'width': 0, 'to_print': True},
            {'title': 'Midterm', 'is_num': True, 'evalu': midterm,
                'width': 0, 'to_print': True}
            ]

    students = [
            {'Name': 'Bob Arthur', 'Group': '301', 'Test 1': 23.,
                'Test 2': 45., 'Midterm': ''},
            {'Name': 'Suzanne Tremblay', 'Group': '301',
                'Test 1': 67., 'Test 2': 78., 'Midterm': 80.},
            {'Name': 'Albert Prévert', 'Group': '302',
                'Test 1': '', 'Test 2': 'ABS', 'Midterm': 78.}
            ]


    def check_with_parser_and_str(self, parser, table_str):
        table = parser.parse(table_str.strip().split('\n'))
        assert_equal(columns, table.columns)
        assert_equal(students, table.students)
    
    def test_rst_parser(self):
        self.check_with_parser_and_str(parsers.RSTTableParser(), self.rst_grid_table)
    
    def test_org_parser(self):
        self.check_with_parser_and_str(parsers.OrgTableParser(), self.org_table)
