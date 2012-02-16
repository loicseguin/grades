#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""test_gradestable

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
import sys
import grades


class TestGrablesTable(object):
    """Test the functionalities of the GradesTable object."""
    in_str = """\
| Nom               | Group | Test 1 | Test 2 | Midterm |
|                   |       |  70.00 | 100.00 |  100.00 |
|                   |       |  10.00 |  10.00 |   30.00 |
|-------------------+-------+--------+--------+---------+
| Bob Arthur        | 301   |  23.00 |  45.00 |         |
| Suzanne Tremblay  | 301   |  67.00 |  78.00 |   80.00 |
| Albert Prévert    | 301   |        | ABS    |   78.00 |
| André Arthur      | 301   |  75.00 |  91.00 |   65.00 |
| Roger Gagnon      | 302   |  67.00 |  78.00 |   80.00 |
| Eleonor Brochu    | 302   |  67.00 |  78.00 |   80.00 |
| Capitaine Haddock | 302   |  34    | 84     |   99.00 |
| Buster Keaton     | 302   |  56    | 43     |   66.00 |
| Alicia Keys       | 302   |  82    | ABS    |   73.00 |
|-------------------+-------+--------+--------+---------+
| -- Moyenne --     |       |  45.00 |  61.50 |   79.00 |
| -- Moyenne 301 -- |       |  23.00 |  45.00 |         |
| -- Moyenne 302 -- |       |  67.00 |  78.00 |   79.00 |"""

    output_str0 = """| Nom            | Group | Test 1 | Test 2 | Midterm |
|                |       |  70.00 | 100.00 |  100.00 |
|                |       |  10.00 |  10.00 |   30.00 |
|----------------+-------+--------+--------+---------|
| Eleonor Brochu | 302   |  67.00 |  78.00 |   80.00 |
"""

    output_str1 = """\
| Nom              | Group | Test 1 | Test 2 | Midterm | -- Cumul -- |
|                  |       |  70.00 | 100.00 |  100.00 |             |
|                  |       |  10.00 |  10.00 |   30.00 |             |
|------------------+-------+--------+--------+---------+-------------|
| Bob Arthur       | 301   |  23.00 |  45.00 |         |        7.79 |
| Suzanne Tremblay | 301   |  67.00 |  78.00 |   80.00 |       41.37 |
| Albert Prévert   | 301   |        | ABS    |   78.00 |       23.40 |
"""

    output_str2 = """\
| Nom               | Group | Test 1 | Test 2 | Midterm |
|                   |       |  70.00 | 100.00 |  100.00 |
|                   |       |  10.00 |  10.00 |   30.00 |
|-------------------+-------+--------+--------+---------|
| Suzanne Tremblay  | 301   |  67.00 |  78.00 |   80.00 |
| André Arthur      | 301   |  75.00 |  91.00 |   65.00 |
|-------------------+-------+--------+--------+---------|
| Eleonor Brochu    | 302   |  67.00 |  78.00 |   80.00 |
|-------------------+-------+--------+--------+---------|
| -- Moyenne 301 -- |       |  71.00 |  84.50 |   72.50 |
| -- Moyenne 302 -- |       |  67.00 |  78.00 |   80.00 |
"""

    output_str3 = """\
| Nom               | Group | Test 1 | Test 2 | Midterm | -- Cumul -- |
|                   |       |  70.00 | 100.00 |  100.00 |             |
|                   |       |  10.00 |  10.00 |   30.00 |             |
|-------------------+-------+--------+--------+---------+-------------|
| Suzanne Tremblay  | 301   |  67.00 |  78.00 |   80.00 |       41.37 |
| André Arthur      | 301   |  75.00 |  91.00 |   65.00 |       39.31 |
|-------------------+-------+--------+--------+---------+-------------|
| Eleonor Brochu    | 302   |  67.00 |  78.00 |   80.00 |       41.37 |
|-------------------+-------+--------+--------+---------+-------------|
| -- Moyenne 301 -- |       |  71.00 |  84.50 |   72.50 |             |
| -- Moyenne 302 -- |       |  67.00 |  78.00 |   80.00 |             |
"""

    def test_indexing(self):
        """Test indexing a GradesTable."""
        gtable = grades.classes.GradesTable(self.in_str.split('\n'))
        gtable.compute_grouped_mean('Group')
        old_stdout = sys.stdout
        sys.stdout = mystdout = io.StringIO()
        subtable = gtable[5]
        writer = grades.classes.TableWriter(subtable)
        writer.printt(div_on=('Group',))
        sys.stdout = old_stdout
        assert_equal(mystdout.getvalue(), self.output_str0)

    def test_simple_slice(self):
        """Test slicing a GradesTable."""
        gtable = grades.classes.GradesTable(self.in_str.split('\n'))
        gtable.compute_cumul()
        gtable.compute_grouped_mean('Group')
        old_stdout = sys.stdout
        sys.stdout = mystdout = io.StringIO()
        subtable = gtable[0:3]
        writer = grades.classes.TableWriter(subtable)
        writer.printt(div_on=('Group',))
        sys.stdout = old_stdout
        assert_equal(mystdout.getvalue(), self.output_str1)

    def test_complex_slice(self):
        """Test a complex slice of a GradesTable."""
        gtable = grades.classes.GradesTable(self.in_str.split('\n'))
        gtable.compute_grouped_mean('Group')
        old_stdout = sys.stdout
        sys.stdout = mystdout = io.StringIO()
        subtable = gtable[1:7:2]
        subtable.compute_grouped_mean('Group')
        writer = grades.classes.TableWriter(subtable)
        writer.printt(div_on=('Group',))
        sys.stdout = old_stdout
        assert_equal(mystdout.getvalue(), self.output_str2)

    def test_wrong_order(self):
        """Test computing mean before cumul. Works with defaultdict."""
        gtable = grades.classes.GradesTable(self.in_str.split('\n'))
        gtable.compute_grouped_mean('Group')
        old_stdout = sys.stdout
        sys.stdout = mystdout = io.StringIO()
        subtable = gtable[1:7:2]
        subtable.compute_grouped_mean('Group')
        subtable.compute_cumul()
        writer = grades.classes.TableWriter(subtable)
        writer.printt(div_on=('Group',))
        sys.stdout = old_stdout
        assert_equal(mystdout.getvalue(), self.output_str3)

