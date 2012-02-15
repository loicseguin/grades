#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""test_gradesfile

"""


__author__ = "Loïc Séguin-C. <loicseguin@gmail.com>"
__license__ = "BSD"


from nose.tools import assert_equal, assert_raises
import os
try:
    import cStringIO as io
except ImportError:
    try:
        import StringIO as io
    except ImportError:
        import io  # For Python 3
import sys
import tempfile
import grades


class TestGradesFile(object):
    """Test the functionalities of the GradesFile class."""
    file_str = """* Grades for a fictive class
This is an example of how a table should look like in order to be properly
processed by grades.py.

| Nom               | Group | Test 1 | Test 2 | Midterm | -- Cumul -- |
|                   |       |  70.00 | 100.00 |  100.00 |             |
|                   |       |  10.00 |  10.00 |   30.00 |             |
|-------------------+-------+--------+--------+---------+-------------|
| Bob Arthur        | 301   |  23.00 |  45.00 |         |        7.79 |
|-------------------+-------+--------+--------+---------+-------------|
| Suzanne Tremblay  | 302   |  67.00 |  78.00 |   80.00 |       41.37 |
| Albert Prévert    | 302   |        | ABS    |   78.00 |       23.40 |
|-------------------+-------+--------+--------+---------+-------------|
| -- Moyenne --     |       |  45.00 |  61.50 |   79.00 |       24.19 |
| -- Moyenne 301 -- |       |  23.00 |  45.00 |         |        7.79 |
| -- Moyenne 302 -- |       |  67.00 |  78.00 |   79.00 |       32.39 |

What precedes and what follows the table will be preserved if the class
GradesFile is used to process the file.

Note that the columns and the lines with an header that starts with '--' are
created by the script. When the script reads the table, it will ignore these
lines and columns.
"""

    file_str2 = """* Grades for a fictive class
This is an example of how a table should look like in order to be properly
processed by grades.py.

| Nom               | Group | Test 1 | Test 2 | Midterm | -- Cumul -- |
|                   |       |  70.00 | 100.00 |  100.00 |             |

What precedes and what follows the table will be preserved if the class
GradesFile is used to process the file.

Note that the columns and the lines with an header that starts with '--' are
created by the script. When the script reads the table, it will ignore these
lines and columns.
"""

    output_str = """* Grades for a fictive class
This is an example of how a table should look like in order to be properly
processed by grades.py.

| Nom               | Group | Test 1 | Test 2 | Midterm | -- Cumul -- |
|                   |       |  70.00 | 100.00 |  100.00 |             |
|                   |       |  10.00 |  10.00 |   30.00 |             |
|-------------------+-------+--------+--------+---------+-------------|
| Bob Arthur        | 301   |  23.00 |  45.00 |         |        7.79 |
|-------------------+-------+--------+--------+---------+-------------|
| Suzanne Tremblay  | 302   |  67.00 |  78.00 |   80.00 |       41.37 |
| Albert Prévert    | 302   |        | ABS    |   78.00 |       23.40 |
|-------------------+-------+--------+--------+---------+-------------|
| -- Moyenne 301 -- |       |  23.00 |  45.00 |         |        7.79 |
| -- Moyenne 302 -- |       |  67.00 |  78.00 |   79.00 |       32.39 |

What precedes and what follows the table will be preserved if the class
GradesFile is used to process the file.

Note that the columns and the lines with an header that starts with '--' are
created by the script. When the script reads the table, it will ignore these
lines and columns.
"""

    output_str2 = """* Grades for a fictive class
This is an example of how a table should look like in order to be properly
processed by grades.py.

| Nom               | Group | Test 1 | Test 2 | Midterm |
|                   |       |  70.00 | 100.00 |  100.00 |
|                   |       |  10.00 |  10.00 |   30.00 |
|-------------------+-------+--------+--------+---------|
| Bob Arthur        | 301   |  23.00 |  45.00 |         |
| Suzanne Tremblay  | 302   |  67.00 |  78.00 |   80.00 |
| Albert Prévert    | 302   |        | ABS    |   78.00 |
|-------------------+-------+--------+--------+---------|
| -- Moyenne 301 -- |       |  23.00 |  45.00 |         |
| -- Moyenne 302 -- |       |  67.00 |  78.00 |   79.00 |

What precedes and what follows the table will be preserved if the class
GradesFile is used to process the file.

Note that the columns and the lines with an header that starts with '--' are
created by the script. When the script reads the table, it will ignore these
lines and columns.
"""

    output_str3 = """* Grades for a fictive class
This is an example of how a table should look like in order to be properly
processed by grades.py.

| Nom              | Group | Test 1 | Test 2 | Midterm |
|                  |       |  70.00 | 100.00 |  100.00 |
|                  |       |  10.00 |  10.00 |   30.00 |
|------------------+-------+--------+--------+---------|
| Bob Arthur       | 301   |  23.00 |  45.00 |         |
|------------------+-------+--------+--------+---------|
| Suzanne Tremblay | 302   |  67.00 |  78.00 |   80.00 |
|------------------+-------+--------+--------+---------|
| Albert Prévert   | 302   |        | ABS    |   78.00 |
|------------------+-------+--------+--------+---------|
| -- Moyenne --    |       |  45.00 |  61.50 |   79.00 |

What precedes and what follows the table will be preserved if the class
GradesFile is used to process the file.

Note that the columns and the lines with an header that starts with '--' are
created by the script. When the script reads the table, it will ignore these
lines and columns.
"""

    output_str4 = """* Grades for a fictive class
This is an example of how a table should look like in order to be properly
processed by grades.py.

| Nom              | Test 1 | Test 2 | -- Cumul -- |
|                  |  70.00 | 100.00 |             |
|                  |  10.00 |  10.00 |             |
|------------------+--------+--------+-------------|
| Bob Arthur       |  23.00 |  45.00 |        7.79 |
|------------------+--------+--------+-------------|
| Suzanne Tremblay |  67.00 |  78.00 |       41.37 |
| Albert Prévert   |        | ABS    |       23.40 |
|------------------+--------+--------+-------------|
| -- Moyenne --    |  45.00 |  61.50 |       24.19 |

What precedes and what follows the table will be preserved if the class
GradesFile is used to process the file.

Note that the columns and the lines with an header that starts with '--' are
created by the script. When the script reads the table, it will ignore these
lines and columns.
"""
    def test_grouped_cumul_div(self):
        """Read the file and print it with the cumulative grade for each
        student as well as with divisions between groups."""
        fdesc, fname = tempfile.mkstemp()
        tfile = os.fdopen(fdesc, 'w')
        tfile.write(self.file_str)
        tfile.close()
        gfile = grades.classes.GradesFile(fname)
        os.unlink(fname)
        gfile.table.compute_cumul()
        gfile.writer.cols_to_print.append('-- Cumul --')
        gfile.table.compute_grouped_mean('Group')
        old_stdout = sys.stdout
        sys.stdout = mystdout = io.StringIO()
        gfile.print_file(div_on=('Group',))
        sys.stdout = old_stdout
        assert_equal(mystdout.getvalue(), self.output_str)

    def test_grouped(self):
        """Calculate the grouped mean, grouping the students by the 'Group'
        column."""
        fdesc, fname = tempfile.mkstemp()
        tfile = os.fdopen(fdesc, 'w')
        tfile.write(self.file_str)
        tfile.close()
        gfile = grades.classes.GradesFile(fname)
        os.unlink(fname)
        gfile.table.compute_grouped_mean('Group')
        old_stdout = sys.stdout
        sys.stdout = mystdout = io.StringIO()
        gfile.print_file()
        sys.stdout = old_stdout
        assert_equal(mystdout.getvalue(), self.output_str2)

    def test_malformed(self):
        """If the table is too short, an exception should be raised."""
        fdesc, fname = tempfile.mkstemp()
        tfile = os.fdopen(fdesc, 'w')
        tfile.write(self.file_str2)
        tfile.close()
        assert_raises(Exception, grades.classes.GradesFile, fname)
        os.unlink(fname)

    def test_mean_div(self):
        """Calculate the mean and print the table with divisions between groups
        and test 1 results."""
        fdesc, fname = tempfile.mkstemp()
        tfile = os.fdopen(fdesc, 'w')
        tfile.write(self.file_str)
        tfile.close()
        gfile = grades.classes.GradesFile(fname)
        os.unlink(fname)
        gfile.table.compute_mean()
        old_stdout = sys.stdout
        sys.stdout = mystdout = io.StringIO()
        gfile.print_file(div_on=('Group', 'Test 1'))
        sys.stdout = old_stdout
        assert_equal(mystdout.getvalue(), self.output_str3)

    def test_cols(self):
        """Write only certain columns of a table."""
        fdesc, fname = tempfile.mkstemp()
        tfile = os.fdopen(fdesc, 'w')
        tfile.write(self.file_str)
        tfile.close()
        gfile = grades.classes.GradesFile(fname)
        os.unlink(fname)
        gfile.table.compute_cumul()
        gfile.table.compute_mean()
        old_stdout = sys.stdout
        sys.stdout = mystdout = io.StringIO()
        gfile.print_file(div_on=('Group',),
                         columns=('Nom', 'Test 1', 'Test 2',
                         '-- Cumul --'))
        sys.stdout = old_stdout
        assert_equal(mystdout.getvalue(), self.output_str4)

