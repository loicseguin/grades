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
    def setUp(self):
        """Test the functionalities of the GradesFile class."""
        self.file_str = """* Grades for a fictive class
This is an example of how a table should look like in order to be properly
processed by grades.py.

| Nom              | Group | Test 1 | Test 2 | Midterm | *Cumul* |
|                  |       |  70.00 | 100.00 |  100.00 |         |
|                  |       |  10.00 |  10.00 |   30.00 |         |
|------------------+-------+--------+--------+---------+---------|
| Bob Arthur       | 301   |  23.00 |  45.00 |         |   38.93 |
|------------------+-------+--------+--------+---------+---------|
| Suzanne Tremblay | 302   |  67.00 |  78.00 |   80.00 |   82.74 |
| Albert Prévert   | 302   |        | ABS    |   78.00 |   78.00 |
|------------------+-------+--------+--------+---------+---------|
| *Mean*           |       |  45.00 |  61.50 |   79.00 |   66.56 |
| *Mean 301*       |       |  23.00 |  45.00 |         |   38.93 |
| *Mean 302*       |       |  67.00 |  78.00 |   79.00 |   80.37 |

What precedes and what follows the table will be preserved if the class
GradesFile is used to process the file.

Note that the columns and the lines with an header that starts with '*' are
created by the script. When the script reads the table, it will ignore these
lines and columns.
"""
        self.fd, self.fname = tempfile.mkstemp()
        of = open(self.fname, 'w')
        of.write(self.file_str)
        of.close()

    def teardown(self):
        os.close(self.fd)
        os.unlink(self.fname)


    file_str2 = """* Grades for a fictive class
This is an example of how a table should look like in order to be properly
processed by grades.py.

| Nom               | Group | Test 1 | Test 2 | Midterm | *Cumul* |
|                   |       |  70.00 | 100.00 |  100.00 |         |

What precedes and what follows the table will be preserved if the class
GradesFile is used to process the file.

Note that the columns and the lines with an header that starts with '*' are
created by the script. When the script reads the table, it will ignore these
lines and columns.
"""

    output_str = """* Grades for a fictive class
This is an example of how a table should look like in order to be properly
processed by grades.py.

| Nom              | Group | Test 1 | Test 2 | Midterm | *Cumul* |
|                  |       |  70.00 | 100.00 |  100.00 |         |
|                  |       |  10.00 |  10.00 |   30.00 |         |
|------------------+-------+--------+--------+---------+---------|
| Bob Arthur       | 301   |  23.00 |  45.00 |         |   38.93 |
|------------------+-------+--------+--------+---------+---------|
| Suzanne Tremblay | 302   |  67.00 |  78.00 |   80.00 |   82.74 |
| Albert Prévert   | 302   |        | ABS    |   78.00 |   78.00 |
|------------------+-------+--------+--------+---------+---------|
| *Mean 301*       |       |  23.00 |  45.00 |         |   38.93 |
| *Mean 302*       |       |  67.00 |  78.00 |   79.00 |   80.37 |

What precedes and what follows the table will be preserved if the class
GradesFile is used to process the file.

Note that the columns and the lines with an header that starts with '*' are
created by the script. When the script reads the table, it will ignore these
lines and columns.
"""

    output_str2 = """* Grades for a fictive class
This is an example of how a table should look like in order to be properly
processed by grades.py.

| Nom              | Group | Test 1 | Test 2 | Midterm |
|                  |       |  70.00 | 100.00 |  100.00 |
|                  |       |  10.00 |  10.00 |   30.00 |
|------------------+-------+--------+--------+---------|
| Bob Arthur       | 301   |  23.00 |  45.00 |         |
| Suzanne Tremblay | 302   |  67.00 |  78.00 |   80.00 |
| Albert Prévert   | 302   |        | ABS    |   78.00 |
|------------------+-------+--------+--------+---------|
| *Mean 301*       |       |  23.00 |  45.00 |         |
| *Mean 302*       |       |  67.00 |  78.00 |   79.00 |

What precedes and what follows the table will be preserved if the class
GradesFile is used to process the file.

Note that the columns and the lines with an header that starts with '*' are
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
| *Mean*           |       |  45.00 |  61.50 |   79.00 |

What precedes and what follows the table will be preserved if the class
GradesFile is used to process the file.

Note that the columns and the lines with an header that starts with '*' are
created by the script. When the script reads the table, it will ignore these
lines and columns.
"""

    output_str4 = """* Grades for a fictive class
This is an example of how a table should look like in order to be properly
processed by grades.py.

| Nom              | Test 1 | Test 2 | *Cumul* |
|                  |  70.00 | 100.00 |         |
|                  |  10.00 |  10.00 |         |
|------------------+--------+--------+---------|
| Bob Arthur       |  23.00 |  45.00 |   38.93 |
|------------------+--------+--------+---------|
| Suzanne Tremblay |  67.00 |  78.00 |   82.74 |
| Albert Prévert   |        | ABS    |   78.00 |
|------------------+--------+--------+---------|
| *Mean*           |  45.00 |  61.50 |   66.56 |

What precedes and what follows the table will be preserved if the class
GradesFile is used to process the file.

Note that the columns and the lines with an header that starts with '*' are
created by the script. When the script reads the table, it will ignore these
lines and columns.
"""

    output_str5 = """\
================== ======== ======== =========
 Nom                Test 1   Test 2   *Cumul* 
                     70.00   100.00           
                     10.00    10.00           
================== ======== ======== =========
 Bob Arthur          23.00    45.00     38.93 
------------------ -------- -------- ---------
 Suzanne Tremblay    67.00    78.00     82.74 
 Albert Prévert              ABS        78.00 
------------------ -------- -------- ---------
 *Mean*              45.00    61.50     66.56 
================== ======== ======== =========
"""

    output_str6 = """\
+------------------+--------+--------+---------+
| Nom              | Test 1 | Test 2 | *Cumul* |
|                  |  70.00 | 100.00 |         |
|                  |  10.00 |  10.00 |         |
+==================+========+========+=========+
| Bob Arthur       |  23.00 |  45.00 |   38.93 |
+------------------+--------+--------+---------+
| Suzanne Tremblay |  67.00 |  78.00 |   82.74 |
+------------------+--------+--------+---------+
| Albert Prévert   |        | ABS    |   78.00 |
+------------------+--------+--------+---------+
| *Mean*           |  45.00 |  61.50 |   66.56 |
+------------------+--------+--------+---------+
"""

    def check_output(self, table_str, gfile, **kwargs):
        mystdout = io.StringIO()
        gfile.print_file(file=mystdout, **kwargs)
        assert_equal(mystdout.getvalue().strip(), table_str.strip())

    def test_grouped_cumul_div(self):
        """Read the file and print it with the cumulative grade for each
        student as well as with divisions between groups."""
        gfile = grades.writers.GradesFile(self.fname)
        gfile.table.compute_cumul()
        gfile.table.compute_grouped_mean('Group')
        self.check_output(self.output_str, gfile, div_on=('Group',))

    def test_grouped(self):
        """Calculate the grouped mean, grouping the students by the 'Group'
        column."""
        gfile = grades.writers.GradesFile(self.fname)
        gfile.table.compute_grouped_mean('Group')
        self.check_output(self.output_str2, gfile)

    def test_malformed(self):
        """If the table is too short, an exception should be raised."""
        fdesc, fname = tempfile.mkstemp()
        tfile = os.fdopen(fdesc, 'w')
        tfile.write(self.file_str2)
        tfile.close()
        assert_raises(Exception, grades.writers.GradesFile, fname)
        os.unlink(fname)

    def test_mean_div(self):
        """Calculate the mean and print the table with divisions between groups
        and test 1 results."""
        gfile = grades.writers.GradesFile(self.fname)
        gfile.table.compute_mean()
        self.check_output(self.output_str3, gfile, div_on=('Group', 'Test 1'))

    def test_cols(self):
        """Write only certain columns of a table."""
        gfile = grades.writers.GradesFile(self.fname)
        gfile.table.compute_cumul()
        gfile.table.compute_mean()
        self.check_output(self.output_str4, gfile, div_on=('Group',),
                         columns=('Nom', 'Test 1', 'Test 2', '*Cumul*'))

    def test_simple_rst_format(self):
        gfile = grades.writers.GradesFile(self.fname)
        gfile.table.compute_cumul()
        gfile.table.compute_mean()
        gfile.table_format = 'simple_rst'
        self.check_output(self.output_str5, gfile, div_on=('Group',),
                         columns=('Nom', 'Test 1', 'Test 2', '*Cumul*'),
                         tableonly=True)

    def test_grid_rst_format(self):
        gfile = grades.writers.GradesFile(self.fname)
        gfile.table.compute_cumul()
        gfile.table.compute_mean()
        gfile.table_format = 'grid_rst'
        self.check_output(self.output_str6, gfile, div_on=('Group',),
                         columns=('Nom', 'Test 1', 'Test 2', '*Cumul*'),
                         tableonly=True)

    def test_read_grid_rst(self):
        file_str = """* Grades for a fictive class
This is an example of how a table should look like in order to be properly
processed by grades.py.

+------------------+-------+--------+--------+---------+---------+
| Nom              | Group | Test 1 | Test 2 | Midterm | *Cumul* |
|                  |       |  70.00 | 100.00 |  100.00 |         |
|                  |       |  10.00 |  10.00 |   30.00 |         |
+==================+=======+========+========+=========+=========+
| Bob Arthur       | 301   |  23.00 |  45.00 |         |   38.93 |
+------------------+-------+--------+--------+---------+---------+
| Suzanne Tremblay | 302   |  67.00 |  78.00 |   80.00 |   82.74 |
+------------------+-------+--------+--------+---------+---------+
| Albert Prévert   | 302   |        | ABS    |   78.00 |   78.00 |
+------------------+-------+--------+--------+---------+---------+
| *Mean*           |       |  45.00 |  61.50 |   79.00 |   66.56 |
+------------------+-------+--------+--------+---------+---------+
| *Mean 301*       |       |  23.00 |  45.00 |         |   38.93 |
+------------------+-------+--------+--------+---------+---------+
| *Mean 302*       |       |  67.00 |  78.00 |   79.00 |   80.37 |
+------------------+-------+--------+--------+---------+---------+

What precedes and what follows the table will be preserved if the class
GradesFile is used to process the file.

Note that the columns and the lines with an header that starts with '*' are
created by the script. When the script reads the table, it will ignore these
lines and columns.
"""
        fd, fname = tempfile.mkstemp()
        of = open(fname, 'w')
        of.write(file_str)
        of.close()

        gfile = grades.writers.GradesFile(fname)
        gfile.table.compute_cumul()
        gfile.table.compute_mean()
        self.check_output(self.output_str4, gfile, div_on=('Group',),
                         columns=('Nom', 'Test 1', 'Test 2', '*Cumul*'))

        os.close(fd)
        os.unlink(fname)

    def test_read_simple_rst(self):
        file_str = """* Grades for a fictive class
This is an example of how a table should look like in order to be properly
processed by grades.py.

================== ======= ======== ======== ========= =========
 Nom                Group   Test 1   Test 2   Midterm   *Cumul* 
                             70.00   100.00    100.00           
                             10.00    10.00     30.00           
================== ======= ======== ======== ========= =========
 Bob Arthur         301      23.00    45.00               38.93 
------------------ ------- -------- -------- --------- ---------
 Suzanne Tremblay   302      67.00    78.00     80.00     82.74 
 Albert Prévert     302              ABS        78.00     78.00 
------------------ ------- -------- -------- --------- ---------
 *Mean*                      45.00    61.50     79.00     66.56 
 *Mean 301*                  23.00    45.00               38.93 
 *Mean 302*                  67.00    78.00     79.00     80.37 
================== ======= ======== ======== ========= =========

What precedes and what follows the table will be preserved if the class
GradesFile is used to process the file.

Note that the columns and the lines with an header that starts with '*' are
created by the script. When the script reads the table, it will ignore these
lines and columns.
"""
        fd, fname = tempfile.mkstemp()
        of = open(fname, 'w')
        of.write(file_str)
        of.close()

        gfile = grades.writers.GradesFile(fname)
        gfile.table.compute_cumul()
        gfile.table.compute_mean()
        self.check_output(self.output_str4, gfile, div_on=('Group',),
                         columns=('Nom', 'Test 1', 'Test 2', '*Cumul*'))

        os.close(fd)
        os.unlink(fname)
