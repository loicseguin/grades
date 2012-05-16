#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
Test GradesTable functionality.

"""


__author__ = "Loïc Séguin-C. <loicseguin@gmail.com>"
__license__ = "BSD"


from collections import defaultdict
from nose.tools import assert_equal, assert_not_equal, assert_almost_equal
import grades


class TestGrablesTable(object):
    """Test the functionalities of the GradesTable object."""
    in_str = """\
| Name              | Group | Test 1 | Test 2 | Midterm |
|                   |       |  70.00 | 100.00 |  100.00 |
|                   |       |  10.00 |  10.00 |   30.00 |
|-------------------+-------+--------+--------+---------|
| Bob Arthur        | 301   |  23.00 |  45.00 |         |
| Suzanne Tremblay  | 301   |  67.00 |  78.00 |   80.00 |
| Albert Prévert    | 301   |        | ABS    |   78.00 |
| André Arthur      | 301   |  75.00 |  91.00 |   65.00 |
| Roger Gagnon      | 302   |  67.00 |  78.00 |   80.00 |
| Eleonor Brochu    | 302   |  67.00 |  78.00 |   80.00 |
| Capitaine Haddock | 302   |  34.00 |  84.00 |   99.00 |
| Buster Keaton     | 302   |  56.00 |  43.00 |   66.00 |
| Alicia Keys       | 302   |  82.00 | ABS    |   73.00 |
|-------------------+-------+--------+--------+---------|
| /Mean/            |       |  45.00 |  61.50 |   79.00 |
| /Mean 301/        |       |  23.00 |  45.00 |         |
| /Mean 302/        |       |  67.00 |  78.00 |   79.00 |"""


    def test_ignore_char(self):
        """Some rows and column should be ignored."""
        gtable1 = grades.parser.parse_table(self.in_str.split('\n'))
        gtable2 = grades.parser.parse_table(self.in_str.split('\n'),
                ignore_char='/')
        assert_not_equal(gtable1, gtable2)
        assert_equal(len(gtable2.footers), 0)

    def test_cumul(self):
        gtable = grades.parser.parse_table(self.in_str.split('\n')[:7])
        gtable.compute_cumul()
        students = [
                {'Name': 'Bob Arthur', 'Group': '301',
                    'Test 1': 23.00, 'Test 2': 45.00, 'Midterm': '',
                    '*Cumul*': 38.9285714},
                {'Name': 'Suzanne Tremblay', 'Group': '301',
                    'Test 1': 67.00, 'Test 2': 78.00, 'Midterm': 80.,
                    '*Cumul*': 82.7428571},
                {'Name': 'Albert Prévert', 'Group': '301',
                    'Test 1': '', 'Test 2': 'ABS', 'Midterm': 78.,
                    '*Cumul*': 78.}]
        assert_equal(gtable.columns[5]['title'], '*Cumul*')
        for i, student in enumerate(students):
            for key in student:
                assert_almost_equal(student[key], gtable.students[i][key])

    def test_indexing(self):
        """Test indexing a GradesTable."""
        gtable = grades.parser.parse_table(self.in_str.split('\n'))
        subtable = gtable[5]
        assert_equal(len(subtable.students), 1)
        assert_equal(subtable.columns, gtable.columns)
        assert_equal(subtable.students[0],
                {'Name': 'Eleonor Brochu', 'Group': '302',
                 'Test 1': 67.00, 'Test 2': 78.00, 'Midterm': 80.00})

    def test_simple_slice(self):
        """Test slicing a GradesTable."""
        gtable = grades.parser.parse_table(self.in_str.split('\n'))
        subtable = gtable[0:3]
        students = [
                {'Name': 'Bob Arthur', 'Group': '301',
                    'Test 1': 23.00, 'Test 2': 45.00, 'Midterm': ''},
                {'Name': 'Suzanne Tremblay', 'Group': '301',
                    'Test 1': 67.00, 'Test 2': 78.00, 'Midterm': 80.},
                {'Name': 'Albert Prévert', 'Group': '301',
                    'Test 1': '', 'Test 2': 'ABS', 'Midterm': 78.}]
        assert_equal(len(subtable.students), 3)
        assert_equal(subtable.columns, gtable.columns)
        assert_equal(subtable.students, students)

    def test_complex_slice(self):
        """Test a complex slice of a GradesTable."""
        gtable = grades.parser.parse_table(self.in_str.split('\n'))
        subtable = gtable[1:7:2]
        subtable.compute_grouped_mean('Group')
        students = [
                {'Name': 'Suzanne Tremblay', 'Group': '301',
                 'Test 1': 67.00, 'Test 2': 78.00, 'Midterm': 80.00},
                {'Name': 'André Arthur', 'Group': '301',
                 'Test 1': 75.00, 'Test 2': 91.00, 'Midterm': 65.00},
                {'Name': 'Eleonor Brochu', 'Group': '302',
                 'Test 1': 67.00, 'Test 2': 78.00, 'Midterm': 80.00}]
        footers = [
                {'Name': '*Mean 301*', 'Test 1': 71.00, 'Test 2': 84.50,
                 'Midterm': 72.50},
                {'Name': '*Mean 302*', 'Test 1': 67.00, 'Test 2': 78.00,
                 'Midterm': 80.00}]
        assert_equal(subtable.columns, gtable.columns)
        assert_equal(subtable.students, students)
        assert_equal(subtable.footers, footers)

    def test_wrong_order(self):
        """Test computing mean before cumul. Works with defaultdict."""
        gtable = grades.parser.parse_table(self.in_str.split('\n'),
                ignore_char='/')
        gtable.compute_grouped_mean('Group')
        gtable.compute_cumul()
        meanrows = [{'Name': '/Mean 301/', 'Test 1': 55., 'Test 2': 71.33,
                     'Midterm': 74.33},
                    {'Name': '/Mean 302/', 'Test 1': 61.2, 'Test 2': 70.75,
                     'Midterm': 79.60}]
        for i, row in enumerate(meanrows):
            for key in row:
                assert_almost_equal(row[key], gtable.footers[i][key], places=2)

    def test_iteration(self):
        """Iterating over the table should go through the list of students."""
        gtable = grades.parser.parse_table(self.in_str.split('\n')[:7])
        students = [
                {'Name': 'Bob Arthur', 'Group': '301', 'Test 1': 23.00,
                 'Test 2': 45.00, 'Midterm': ''},
                {'Name': 'Suzanne Tremblay', 'Group': '301', 'Test 1': 67.00,
                 'Test 2': 78.00, 'Midterm': 80.00},
                {'Name': 'Albert Prévert', 'Group': '301', 'Test 1': '',
                 'Test 2': 'ABS', 'Midterm': 78.00}]
        for i, student in enumerate(gtable):
            assert_equal(student, students[i])

    def test_copy(self):
        """Initializing a new table with another table creates a copy."""
        gtable = grades.parser.parse_table(self.in_str.split('\n'))
        gtable2 = grades.gradestable.GradesTable(gtable)
        assert_equal(gtable.students, gtable2.students)
        assert_equal(gtable.columns, gtable2.columns)

    def test_add_tables(self):
        """Add two tables."""
        gtable1 = grades.parser.parse_table(self.in_str.split('\n')[:7])
        gtable2 = grades.parser.parse_table(self.in_str.split('\n')[:4]
                                            + self.in_str.split('\n')[7:])
        gtable = grades.parser.parse_table(self.in_str.split('\n'))
        sumtable = gtable1 + gtable2
        assert_equal(gtable, sumtable)

    def test_add_student(self):
        """Add a student to a table."""
        gtable = grades.parser.parse_table(self.in_str.split('\n')[:7])
        student = defaultdict(str, (('Name', 'André Arthur'), ('Group', '301'),
                    ('Test 1', 75.00), ('Test 2', 91.00), ('Midterm', 65.00)))
        sumtable = gtable + student
        students = [
                {'Name': 'Bob Arthur', 'Group': '301', 'Test 1': 23.00,
                 'Test 2': 45.00, 'Midterm': ''},
                {'Name': 'Suzanne Tremblay', 'Group': '301', 'Test 1': 67.00,
                 'Test 2': 78.00, 'Midterm': 80.00},
                {'Name': 'Albert Prévert', 'Group': '301', 'Test 1': '',
                 'Test 2': 'ABS', 'Midterm': 78.},
                {'Name': 'André Arthur', 'Group': '301', 'Test 1': 75.00,
                 'Test 2': 91.00, 'Midterm': 65.00}]
        assert_equal(gtable.columns, sumtable.columns)
        assert_equal(sumtable.students, students)

    def test_select(self):
        """Test selection of students."""
        gtable = grades.parser.parse_table(self.in_str.split('\n'),
                ignore_char='/')
        stable = gtable.select('Test 2<46')
        students = [
                {'Name': 'Bob Arthur', 'Group': '301', 'Test 1': 23.00,
                 'Test 2': 45.00, 'Midterm': ''},
                {'Name': 'Buster Keaton', 'Group': '302', 'Test 1': 56.00,
                 'Test 2': 43.00, 'Midterm': 66.00}]
        assert_equal(gtable.columns, stable.columns)
        assert_equal(students, stable.students)
