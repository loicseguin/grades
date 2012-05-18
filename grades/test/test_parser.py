#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
Test table parsers.

"""


__author__ = "Loïc Séguin-C. <loicseguin@gmail.com>"
__license__ = "BSD"


from nose.tools import assert_equal, assert_raises
from grades import parsers


class TestParser:
    """Define some tables to test if they are parsed correctly."""
    rst_grid_table = """\
+------------------+-------+--------+--------+---------+
| Name             | Group | Test 1 | Test 2 | Midterm |
|                  |       | 70     | 100.00 | 100.00  |
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

    too_short_header = """\
| Name             | Group | Test 1 | Test 2 | Midterm |
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
            {'title': 'Name', 'is_num': False, 'evalu': None, 'width': 0},
            {'title': 'Group', 'is_num': False, 'evalu': None, 'width': 0},
            {'title': 'Test 1', 'is_num': True, 'evalu': test1, 'width': 0},
            {'title': 'Test 2', 'is_num': True, 'evalu': test2, 'width': 0},
            {'title': 'Midterm', 'is_num': True, 'evalu': midterm, 'width': 0}
            ]

    students = [
            {'Name': 'Bob Arthur', 'Group': '301', 'Test 1': 23.,
                'Test 2': 45., 'Midterm': ''},
            {'Name': 'Suzanne Tremblay', 'Group': '301',
                'Test 1': 67., 'Test 2': 78., 'Midterm': 80.},
            {'Name': 'Albert Prévert', 'Group': '302',
                'Test 1': '', 'Test 2': 'ABS', 'Midterm': 78.}
            ]


    def check_table_str(self, table_str):
        tparser = parsers.TableParser()
        table = tparser.parse(table_str.strip().split('\n'))
        assert_equal(self.columns, table.columns)
        assert_equal(self.students, table.students)

    def test_rst_table(self):
        self.check_table_str(self.rst_grid_table)

    def test_org_table(self):
        self.check_table_str(self.org_table)

    def test_short_header(self):
        tparser = parsers.TableParser()
        assert_raises(parsers.TableMarkupError, tparser.parse,
                      self.too_short_header)
