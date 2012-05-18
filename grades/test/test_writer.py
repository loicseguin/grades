#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
Test table writer.

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
import grades


class TestTableWriter:
    def setUp(self):
        """Test the functionalities of the table writer."""
        in_str = """\
| Nom               | Group | Test 1 | Test 2 | Midterm |
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
| *Mean*            |       |  45.00 |  61.50 |   79.00 |
| *Mean 301*        |       |  23.00 |  45.00 |         |
| *Mean 302*        |       |  67.00 |  78.00 |   79.00 |"""

        self.gtable = grades.parser.parse_table(in_str.split('\n'))

        self.output_str0 = """\
| Nom            | Group | Test 1 | Test 2 | Midterm |
|                |       |  70.00 | 100.00 |  100.00 |
|                |       |  10.00 |  10.00 |   30.00 |
|----------------+-------+--------+--------+---------|
| Eleonor Brochu | 302   |  67.00 |  78.00 |   80.00 |
"""

        self.output_str1 = """\
| Nom              | Group | Test 1 | Test 2 | Midterm | *Cumul* |
|                  |       |  70.00 | 100.00 |  100.00 |         |
|                  |       |  10.00 |  10.00 |   30.00 |         |
|------------------+-------+--------+--------+---------+---------|
| Bob Arthur       | 301   |  23.00 |  45.00 |         |   38.93 |
| Suzanne Tremblay | 301   |  67.00 |  78.00 |   80.00 |   82.74 |
| Albert Prévert   | 301   |        | ABS    |   78.00 |   78.00 |
"""

        self.output_str2 = """\
| Nom              | Group | Test 1 | Test 2 | Midterm |
|                  |       |  70.00 | 100.00 |  100.00 |
|                  |       |  10.00 |  10.00 |   30.00 |
|------------------+-------+--------+--------+---------|
| Suzanne Tremblay | 301   |  67.00 |  78.00 |   80.00 |
| André Arthur     | 301   |  75.00 |  91.00 |   65.00 |
|------------------+-------+--------+--------+---------|
| Eleonor Brochu   | 302   |  67.00 |  78.00 |   80.00 |
|------------------+-------+--------+--------+---------|
| *Mean 301*       |       |  71.00 |  84.50 |   72.50 |
| *Mean 302*       |       |  67.00 |  78.00 |   80.00 |
"""

        self.output_str3 = """\
| Nom              | Group | Test 1 | Test 2 | Midterm | *Cumul* |
|                  |       |  70.00 | 100.00 |  100.00 |         |
|                  |       |  10.00 |  10.00 |   30.00 |         |
|------------------+-------+--------+--------+---------+---------|
| Suzanne Tremblay | 301   |  67.00 |  78.00 |   80.00 |   82.74 |
| André Arthur     | 301   |  75.00 |  91.00 |   65.00 |   78.63 |
|------------------+-------+--------+--------+---------+---------|
| Eleonor Brochu   | 302   |  67.00 |  78.00 |   80.00 |   82.74 |
|------------------+-------+--------+--------+---------+---------|
| *Mean 301*       |       |  71.00 |  84.50 |   72.50 |         |
| *Mean 302*       |       |  67.00 |  78.00 |   80.00 |         |
"""

        self.output_str4 = """\
| Nom           | Group | Test 1 | Test 2 | Midterm |
|               |       |  70.00 | 100.00 |  100.00 |
|               |       |  10.00 |  10.00 |   30.00 |
|---------------+-------+--------+--------+---------|
| Bob Arthur    | 301   |  23.00 |  45.00 |         |
| Buster Keaton | 302   |  56.00 |  43.00 |   66.00 |
"""

        self.output_str5 = """\
| Nom               | Test 2 |
|                   | 100.00 |
|                   |  10.00 |
|-------------------+--------|
| Bob Arthur        |  45.00 |
| Suzanne Tremblay  |  78.00 |
| Albert Prévert    | ABS    |
| André Arthur      |  91.00 |
| Roger Gagnon      |  78.00 |
| Eleonor Brochu    |  78.00 |
| Capitaine Haddock |  84.00 |
| Buster Keaton     |  43.00 |
| Alicia Keys       | ABS    |
"""

    def check_printed_table(self, table_str, table, **kwargs):
        mystdout = io.StringIO()
        writer = grades.writer.TableWriter(table)
        writer.write(file=mystdout, **kwargs)
        assert_equal(mystdout.getvalue(), table_str)

    def test_indexing(self):
        """Test indexing a GradesTable."""
        self.gtable.compute_grouped_mean('Group')
        subtable = self.gtable[5]
        self.check_printed_table(self.output_str0, subtable,
                                 div_on=('Group',))

    def test_simple_slice(self):
        """Test slicing a GradesTable."""
        self.gtable.compute_cumul()
        self.gtable.compute_grouped_mean('Group')
        subtable = self.gtable[0:3]
        self.check_printed_table(self.output_str1, subtable,
                                 div_on=('Group',))

    def test_complex_slice(self):
        """Test a complex slice of a GradesTable."""
        self.gtable.compute_grouped_mean('Group')
        subtable = self.gtable[1:7:2]
        subtable.compute_grouped_mean('Group')
        self.check_printed_table(self.output_str2, subtable,
                                 div_on=('Group',))

    def test_wrong_order(self):
        """Test computing mean before cumul. Works with defaultdict."""
        self.gtable.compute_grouped_mean('Group')
        subtable = self.gtable[1:7:2]
        subtable.compute_grouped_mean('Group')
        subtable.compute_cumul()
        self.check_printed_table(self.output_str3, subtable,
                                 div_on=('Group',))

    def test_select(self):
        """Test selection of students."""
        self.gtable = self.gtable.select('Test 2<46')
        self.check_printed_table(self.output_str4, self.gtable)

    def test_columns(self):
        """Test selection of columns."""
        self.check_printed_table(self.output_str5, self.gtable,
                                 columns=['Nom', 'Test 2'])

    def test_simple_rst(self):
        """Test reStructuredText simple table format writer."""
        mystdout = io.StringIO()
        subtable = self.gtable[1:7:2]
        subtable.compute_grouped_mean('Group')
        subtable.compute_cumul()
        writer = grades.writer.SimpleRSTWriter(subtable)
        writer.write(file=mystdout, div_on=('Group',))
        table_str = """\
================== ======= ======== ======== ========= =========
 Nom                Group   Test 1   Test 2   Midterm   *Cumul* 
                             70.00   100.00    100.00           
                             10.00    10.00     30.00           
================== ======= ======== ======== ========= =========
 Suzanne Tremblay   301      67.00    78.00     80.00     82.74 
 André Arthur       301      75.00    91.00     65.00     78.63 
------------------ ------- -------- -------- --------- ---------
 Eleonor Brochu     302      67.00    78.00     80.00     82.74 
------------------ ------- -------- -------- --------- ---------
 *Mean 301*                  71.00    84.50     72.50           
 *Mean 302*                  67.00    78.00     80.00           
================== ======= ======== ======== ========= =========
"""
        assert_equal(mystdout.getvalue(), table_str)

    def test_grid_rst(self):
        """Test reStructuredText simple table format writer."""
        mystdout = io.StringIO()
        subtable = self.gtable[1:7:2]
        subtable.compute_grouped_mean('Group')
        subtable.compute_cumul()
        writer = grades.writer.GridRSTWriter(subtable)
        writer.write(file=mystdout, div_on=('Group',))
        table_str = """\
+------------------+-------+--------+--------+---------+---------+
| Nom              | Group | Test 1 | Test 2 | Midterm | *Cumul* |
|                  |       |  70.00 | 100.00 |  100.00 |         |
|                  |       |  10.00 |  10.00 |   30.00 |         |
+==================+=======+========+========+=========+=========+
| Suzanne Tremblay | 301   |  67.00 |  78.00 |   80.00 |   82.74 |
+------------------+-------+--------+--------+---------+---------+
| André Arthur     | 301   |  75.00 |  91.00 |   65.00 |   78.63 |
+------------------+-------+--------+--------+---------+---------+
| Eleonor Brochu   | 302   |  67.00 |  78.00 |   80.00 |   82.74 |
+------------------+-------+--------+--------+---------+---------+
| *Mean 301*       |       |  71.00 |  84.50 |   72.50 |         |
+------------------+-------+--------+--------+---------+---------+
| *Mean 302*       |       |  67.00 |  78.00 |   80.00 |         |
+------------------+-------+--------+--------+---------+---------+
"""
        assert_equal(mystdout.getvalue(), table_str)
