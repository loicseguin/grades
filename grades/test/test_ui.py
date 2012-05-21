#-*- coding: utf-8 -*-
"""test_ui

"""


__author__ = "Loïc Séguin-C. <loicseguin@gmail.com>"
__license__ = "BSD"


from nose.tools import assert_equal, assert_raises, assert_true
try:
    import cStringIO as io
except ImportError:
    try:
        import StringIO as io
    except ImportError:
        import io  # For Python 3
import os
import sys
import uuid
import tempfile
from grades import ui

class TestUIPrint:
    def setUp(self):
        self.in_str = """\
* Grades for MATH101.
I wonder what happened to Bob Arthur's midterm and to Albert Prévert's Test
1. Maybe they've eaten the salmon mousse.

| Nom               | Group | Test 1 | Test 2 | Midterm |
|                   |       |  70.00 | 100.00 |  100.00 |
|                   |       |  10.00 |  10.00 |   30.00 |
|-------------------+-------+--------+--------+---------|
| Bob Arthur        | 301   |  23.00 |  45.00 |         |
| Suzanne Tremblay  | 301   |  67.00 |  78.00 |   80.00 |
| Albert Prévert    | 301   |        | ABS    |   78.00 |
| André Arthur      | 301   |  75.00 |  91.00 |   65.00 |
|-------------------+-------+--------+--------+---------|
| Roger Gagnon      | 302   |  67.00 |  78.00 |   80.00 |
| Eleonor Brochu    | 302   |  67.00 |  78.00 |   80.00 |
| Capitaine Haddock | 302   |  34.00 |  84.00 |   99.00 |
| Buster Keaton     | 302   |  56.00 |  43.00 |   66.00 |
| Alicia Keys       | 302   |  82.00 | ABS    |   73.00 |

* Next class: How to add numbers
As an exercise, ask the students to count the number of pencils in their
pencil case.
"""
        self.fd, self.fname = tempfile.mkstemp()
        of = open(self.fname, 'w')
        of.write(self.in_str)
        of.close()
        self.old_stream = sys.stdout
        sys.stdout = self.mystdout = io.StringIO()
        self.runner = ui.Runner()

    def teardown(self):
        os.close(self.fd)
        os.unlink(self.fname)
        sys.stdout = self.old_stream

    out_str1 = """\
| Nom               | Group | Test 1 | *Cumul* |
|                   |       |  70.00 |         |
|                   |       |  10.00 |         |
|-------------------+-------+--------+---------|
| Bob Arthur        | 301   |  23.00 |   38.93 |
| Suzanne Tremblay  | 301   |  67.00 |   82.74 |
| Albert Prévert    | 301   |        |   78.00 |
| André Arthur      | 301   |  75.00 |   78.63 |
|-------------------+-------+--------+---------|
| Roger Gagnon      | 302   |  67.00 |   82.74 |
| Eleonor Brochu    | 302   |  67.00 |   82.74 |
| Capitaine Haddock | 302   |  34.00 |   85.91 |
| Buster Keaton     | 302   |  56.00 |   64.20 |
| Alicia Keys       | 302   |  82.00 |   84.04 |
|-------------------+-------+--------+---------|
| *Mean*            |       |  58.88 |   75.33 |
| *Mean 301*        |       |  55.00 |   69.57 |
| *Mean 302*        |       |  61.20 |   79.93 |
"""

    out_str2 = """\
| Nom               | Test 1 |
|                   |  70.00 |
|                   |  10.00 |
|-------------------+--------|
| Bob Arthur        |  23.00 |
| Suzanne Tremblay  |  67.00 |
| Albert Prévert    |        |
| André Arthur      |  75.00 |
| Roger Gagnon      |  67.00 |
| Eleonor Brochu    |  67.00 |
| Capitaine Haddock |  34.00 |
| Buster Keaton     |  56.00 |
| Alicia Keys       |  82.00 |
"""

    out_str3 = """\
| Nom        | Group | Test 1 | Test 2 | Midterm |
|            |       |  70.00 | 100.00 |  100.00 |
|            |       |  10.00 |  10.00 |   30.00 |
|------------+-------+--------+--------+---------|
| Bob Arthur | 301   |  23.00 |  45.00 |         |
"""

    out_str4 = """\
| Nom               | Group | Test 1 | Test 2 | Midterm |
|                   |       |  70.00 | 100.00 |  100.00 |
|                   |       |  10.00 |  10.00 |   30.00 |
|-------------------+-------+--------+--------+---------|
| Bob Arthur        | 301   |  23.00 |  45.00 |         |
| Albert Prévert    | 301   |        | ABS    |   78.00 |
| André Arthur      | 301   |  75.00 |  91.00 |   65.00 |
| Eleonor Brochu    | 302   |  67.00 |  78.00 |   80.00 |
| Capitaine Haddock | 302   |  34.00 |  84.00 |   99.00 |
| Buster Keaton     | 302   |  56.00 |  43.00 |   66.00 |
| Alicia Keys       | 302   |  82.00 | ABS    |   73.00 |
"""

    out_str5 = """\
| Nom               | Group | Test 1 | Test 2 | Midterm |
|                   |       |  70.00 | 100.00 |  100.00 |
|                   |       |  10.00 |  10.00 |   30.00 |
|-------------------+-------+--------+--------+---------|
| André Arthur      | 301   |  75.00 |  91.00 |   65.00 |
| Capitaine Haddock | 302   |  34.00 |  84.00 |   99.00 |
"""

    out_str6 = """\
| Nom               | Group | Test 1 | Test 2 | Midterm |
|                   |       |  70.00 | 100.00 |  100.00 |
|                   |       |  10.00 |  10.00 |   30.00 |
|-------------------+-------+--------+--------+---------|
| Bob Arthur        | 301   |  23.00 |  45.00 |         |
| Suzanne Tremblay  | 301   |  67.00 |  78.00 |   80.00 |
| André Arthur      | 301   |  75.00 |  91.00 |   65.00 |
| Roger Gagnon      | 302   |  67.00 |  78.00 |   80.00 |
| Eleonor Brochu    | 302   |  67.00 |  78.00 |   80.00 |
| Capitaine Haddock | 302   |  34.00 |  84.00 |   99.00 |
| Buster Keaton     | 302   |  56.00 |  43.00 |   66.00 |
"""

    out_str7 = """\
| Nom | Group | Test 1 | Test 2 | Midterm |
|     |       |  70.00 | 100.00 |  100.00 |
|     |       |  10.00 |  10.00 |   30.00 |
|-----+-------+--------+--------+---------|
"""

    def check_output(self, argv, output_str):
        self.runner.run(argv)
        assert_equal(self.mystdout.getvalue().strip(), output_str.strip())

    #def test_no_opt(self):
        #"""When called without any argument, grades tries to open Grades.txt
        #and prints the file. In this case, Grades.txt does not exist and an
        #error message should be printed out."""
        #self.check_output([], "error: can't find file Grades.txt",
                #out_stream=sys.stderr)

    def test_non_existing_file(self):
        nonexistent = str(uuid.uuid1())
        argv = ['print', nonexistent]
        oldstderr = sys.stderr
        sys.stderr = myerr = io.StringIO()
        self.runner.run(argv)
        sys.stderr = oldstderr
        assert_true('No such file or directory'
                    in myerr.getvalue().strip())

    def test_print(self):
        """Calling ``grades print fname`` should print the file fname without
        any row separator between students."""
        in_rows = self.in_str.split('\n')
        out_str = '\n'.join(in_rows[:12] + in_rows[13:])
        self.check_output(['print', self.fname], out_str)

    def test_print_all_opts(self):
        argv = ['print', '-mctd', 'Group', '-g', 'Group', '-C',
                'Nom,Group,Test 1', self.fname]
        self.check_output(argv, self.out_str1)

    def test_invalid_column_div(self):
        argv = ['print', '-d', 'Spam', self.fname]
        assert_raises(ValueError, self.runner.run, argv)

    def test_invalid_column_group(self):
        argv = ['print', '-g', 'Spam', self.fname]
        assert_raises(ValueError, self.runner.run, argv)

    def test_invalid_column_C(self):
        argv = ['print', '-tC', 'Nom,Spam,Test 1', self.fname]
        self.check_output(argv, self.out_str2)

    def test_select_name(self):
        argv = ['print', '-ts', 'Nom=Bob Arthur', self.fname]
        self.check_output(argv, self.out_str3)

    def test_select_name2(self):
        argv = ['print', '-ts', 'Nom == Bob Arthur', self.fname]
        self.check_output(argv, self.out_str3)

    def test_select_name3(self):
        argv = ['print', '-ts', 'Nom < Mon', self.fname]
        self.check_output(argv, self.out_str4)

    def test_select_test_2(self):
        argv = ['print', '-ts', 'Test 2 >= 80', self.fname]
        self.check_output(argv, self.out_str5)

    def test_select_ne(self):
        argv = ['print', '-ts', 'Test 2 != ABS', self.fname]
        self.check_output(argv, self.out_str6)

    def test_invalid_select(self):
        argv = ['print', '-ts', 'Test / 2', self.fname]
        assert_raises(Exception, self.runner.run, argv)

    def test_select_empty(self):
        argv = ['print', '-ts', 'Test 2 = -1', self.fname]
        self.check_output(argv, self.out_str7)


class TestUIInit:
    def setUp(self):
        self.fname = str(uuid.uuid1())
        self.runner = ui.Runner()

    def teardown(self):
        os.unlink(self.fname)

    def check_output(self, argv, output_str):
        self.runner.run(argv)
        file_str = open(self.fname).read()
        assert_equal(file_str.strip(), output_str.strip())

    def test_init(self):
        argv = ['init', self.fname]
        init_table = """\
| Name | Group | Test 1 | Test 2 | Test 3 | Midterm | Test 4 | Test 5 | Test 6 | Final |
|      |       |  20.00 |  20.00 |  20.00 |  100.00 |  20.00 |  20.00 |  20.00 |100.00 |
|      |       |   5.00 |   5.00 |   5.00 |   30.00 |   5.00 |   5.00 |   5.00 | 40.00 |
|------+-------+--------+--------+--------+---------+--------+--------+--------+-------|
"""
        self.check_output(argv, init_table)

    def test_init_simple_rst(self):
        argv = ['init', self.fname, '-f', 'simple_rst']
        init_table = """\
====== ======= ======== ======== ======== ========= ======== ======== ======== =======
 Name   Group   Test 1   Test 2   Test 3   Midterm   Test 4   Test 5   Test 6   Final 
                 20.00    20.00    20.00    100.00    20.00    20.00    20.00  100.00 
                  5.00     5.00     5.00     30.00     5.00     5.00     5.00   40.00 
====== ======= ======== ======== ======== ========= ======== ======== ======== =======
====== ======= ======== ======== ======== ========= ======== ======== ======== =======
"""
        self.check_output(argv, init_table)

    def test_init_grid_rst(self):
        argv = ['init', self.fname, '-f', 'grid_rst']
        init_table = """\
+------+-------+--------+--------+--------+---------+--------+--------+--------+-------+
| Name | Group | Test 1 | Test 2 | Test 3 | Midterm | Test 4 | Test 5 | Test 6 | Final |
|      |       |  20.00 |  20.00 |  20.00 |  100.00 |  20.00 |  20.00 |  20.00 |100.00 |
|      |       |   5.00 |   5.00 |   5.00 |   30.00 |   5.00 |   5.00 |   5.00 | 40.00 |
+======+=======+========+========+========+=========+========+========+========+=======+
"""
        self.check_output(argv, init_table)

    def test_nbevals_1(self):
        argv = ['init', '-n', '1', self.fname]
        init_table = """\
| Name | Group | Final |
|      |       |100.00 |
|      |       |100.00 |
|------+-------+-------|
"""
        self.check_output(argv, init_table)

    def test_nbevals_2(self):
        argv = ['init', '-n', '2', self.fname]
        init_table = """\
| Name | Group | Midterm | Final |
|      |       |  100.00 |100.00 |
|      |       |   40.00 | 60.00 |
|------+-------+---------+-------|
"""
        self.check_output(argv, init_table)

    def test_nbevals_5(self):
        argv = ['init', '-n', '5', self.fname]
        init_table = """\
| Name | Group | Test 1 | Test 2 | Midterm | Test 3 | Final |
|      |       |  20.00 |  20.00 |  100.00 |  20.00 |100.00 |
|      |       |  10.00 |  10.00 |   30.00 |  10.00 | 40.00 |
|------+-------+--------+--------+---------+--------+-------|
"""
        self.check_output(argv, init_table)


class TestUIAdd:
    def setUp(self):
        """Set up class for each test."""
        self.in_str = """\
| Nom               | Group | Test 1 | Test 2 | Midterm |
|                   |       |  70.00 | 100.00 |  100.00 |
|                   |       |  10.00 |  10.00 |   30.00 |
|-------------------+-------+--------+--------+---------|
| Bob Arthur        | 301   |  23.00 |  45.00 |         |
| Suzanne Tremblay  | 301   |  67.00 |  78.00 |   80.00 |
| Albert Prévert    | 301   |        | ABS    |   78.00 |
| André Arthur      | 301   |  75.00 |  91.00 |   65.00 |
|-------------------+-------+--------+--------+---------|
| Roger Gagnon      | 302   |  67.00 |  78.00 |   80.00 |
| Eleonor Brochu    | 302   |  67.00 |  78.00 |   80.00 |
| Capitaine Haddock | 302   |  34.00 |  84.00 |   99.00 |
| Buster Keaton     | 302   |  56.00 |  43.00 |   66.00 |
| Alicia Keys       | 302   |  82.00 | ABS    |   73.00 |
"""
        self.fd, self.fname = tempfile.mkstemp()
        of = open(self.fname, 'w')
        of.write(self.in_str)
        of.close()
        self.old_stream = sys.stdout
        sys.stdout = self.mystdout = io.StringIO()
        self.runner = ui.Runner()

    def teardown(self):
        os.close(self.fd)
        os.unlink(self.fname)
        sys.stdout = self.old_stream

    def check_output(self, argv, output_str, specs):
        sys.stdin = io.StringIO('\n'.join(specs))
        self.runner.run(argv)
        sys.stdin = sys.__stdin__
        file_str = open(self.fname).read()
        assert_equal(file_str.strip(), output_str.strip())

    def test_add_student(self):
        argv = ['add', 'student', self.fname]
        output_str = """\
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
| Simon Groulx      | 301   |        |        |         |
"""

        self.check_output(argv, output_str, ['Simon Groulx', '301'])

    def test_add_column(self):
        argv = ['add', 'column', self.fname]
        output_str = """\
| Nom               | Group | Test 1 | Exam Surprise | Test 2 | Midterm |
|                   |       |  70.00 |         60.00 | 100.00 |  100.00 |
|                   |       |  10.00 |         23.00 |  10.00 |   30.00 |
|-------------------+-------+--------+---------------+--------+---------|
| Bob Arthur        | 301   |  23.00 |               |  45.00 |         |
| Suzanne Tremblay  | 301   |  67.00 |               |  78.00 |   80.00 |
| Albert Prévert    | 301   |        |               | ABS    |   78.00 |
| André Arthur      | 301   |  75.00 |               |  91.00 |   65.00 |
| Roger Gagnon      | 302   |  67.00 |               |  78.00 |   80.00 |
| Eleonor Brochu    | 302   |  67.00 |               |  78.00 |   80.00 |
| Capitaine Haddock | 302   |  34.00 |               |  84.00 |   99.00 |
| Buster Keaton     | 302   |  56.00 |               |  43.00 |   66.00 |
| Alicia Keys       | 302   |  82.00 |               | ABS    |   73.00 |
"""

        self.check_output(argv, output_str, ['Exam Surprise', '3', 'y', '60.', '23.'])

    def test_add_column_default_pos(self):
        argv = ['add', 'column', self.fname]
        output_str = """\
| Nom               | Group | Test 1 | Test 2 | Midterm | Exam Surprise |
|                   |       |  70.00 | 100.00 |  100.00 |         60.00 |
|                   |       |  10.00 |  10.00 |   30.00 |         23.00 |
|-------------------+-------+--------+--------+---------+---------------|
| Bob Arthur        | 301   |  23.00 |  45.00 |         |               |
| Suzanne Tremblay  | 301   |  67.00 |  78.00 |   80.00 |               |
| Albert Prévert    | 301   |        | ABS    |   78.00 |               |
| André Arthur      | 301   |  75.00 |  91.00 |   65.00 |               |
| Roger Gagnon      | 302   |  67.00 |  78.00 |   80.00 |               |
| Eleonor Brochu    | 302   |  67.00 |  78.00 |   80.00 |               |
| Capitaine Haddock | 302   |  34.00 |  84.00 |   99.00 |               |
| Buster Keaton     | 302   |  56.00 |  43.00 |   66.00 |               |
| Alicia Keys       | 302   |  82.00 | ABS    |   73.00 |               |
"""

        self.check_output(argv, output_str, ['Exam Surprise', '', 'y', '60.', '23.'])
