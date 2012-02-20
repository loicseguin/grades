#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""test_runner

"""


__author__ = "Loïc Séguin-C. <loicseguin@gmail.com>"
__license__ = "BSD"


from nose.tools import assert_equal, assert_raises
try:
    import cStringIO as io
except ImportError:
    try:
        import StringIO as io
    except ImportError:
        import io  # For Python 3
import sys
from grades import runner

class TestRunner(object):
    out_str0 = """\
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
| Roger Gagnon      | 302   |  67.00 |  78.00 |   80.00 |
| Eleonor Brochu    | 302   |  67.00 |  78.00 |   80.00 |
| Capitaine Haddock | 302   |  34.00 |  84.00 |   99.00 |
| Buster Keaton     | 302   |  56.00 |  43.00 |   66.00 |
| Alicia Keys       | 302   |  82.00 | ABS    |   73.00 |

* Next class: How to add numbers
As an exercise, ask the students to count the number of pencils in their
pencil case.
"""
    out_str1 = """\
| Nom               | Group | Test 1 | /Cumul/ |
|                   |       |  70.00 |         |
|                   |       |  10.00 |         |
|-------------------+-------+--------+---------|
| Bob Arthur        | 301   |  23.00 |    7.79 |
| Suzanne Tremblay  | 301   |  67.00 |   41.37 |
| Albert Prévert    | 301   |        |   23.40 |
| André Arthur      | 301   |  75.00 |   39.31 |
|-------------------+-------+--------+---------|
| Roger Gagnon      | 302   |  67.00 |   41.37 |
| Eleonor Brochu    | 302   |  67.00 |   41.37 |
| Capitaine Haddock | 302   |  34.00 |   42.96 |
| Buster Keaton     | 302   |  56.00 |   32.10 |
| Alicia Keys       | 302   |  82.00 |   33.61 |
|-------------------+-------+--------+---------|
| /Mean/            |       |  58.88 |   33.70 |
| /Mean 301/        |       |  55.00 |   27.97 |
| /Mean 302/        |       |  61.20 |   38.28 |
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

    def test_no_opt(self):
        argv = ['examples/math101.txt']
        old_stdout = sys.stdout
        sys.stdout = mystdout = io.StringIO()
        runner.run(argv)
        sys.stdout = old_stdout
        assert_equal(mystdout.getvalue().strip(), self.out_str0.strip())

    def test_all_opts(self):
        argv = ['-mctd', 'Group', '-g', 'Group', '-C', 'Nom,Group,Test 1',
                'examples/math101.txt']
        old_stdout = sys.stdout
        sys.stdout = mystdout = io.StringIO()
        runner.run(argv)
        sys.stdout = old_stdout
        assert_equal(mystdout.getvalue().strip(), self.out_str1.strip())

    def test_invalid_column_div(self):
        argv = ['-d', 'Spam', 'examples/math101.txt']
        assert_raises(ValueError, runner.run, argv)

    def test_invalid_column_group(self):
        argv = ['-g', 'Spam', 'examples/math101.txt']
        assert_raises(ValueError, runner.run, argv)

    def test_invalid_column_C(self):
        argv = ['-tC', 'Nom,Spam,Test 1', 'examples/math101.txt']
        old_stdout = sys.stdout
        sys.stdout = mystdout = io.StringIO()
        runner.run(argv)
        sys.stdout = old_stdout
        assert_equal(mystdout.getvalue().strip(), self.out_str2.strip())

    def test_select_name(self):
        argv = ['-ts', 'Nom=Bob Arthur', 'examples/math101.txt']
        old_stdout = sys.stdout
        sys.stdout = mystdout = io.StringIO()
        runner.run(argv)
        sys.stdout = old_stdout
        assert_equal(mystdout.getvalue().strip(), self.out_str3.strip())

    def test_select_name2(self):
        argv = ['-ts', 'Nom == Bob Arthur', 'examples/math101.txt']
        old_stdout = sys.stdout
        sys.stdout = mystdout = io.StringIO()
        runner.run(argv)
        sys.stdout = old_stdout
        assert_equal(mystdout.getvalue().strip(), self.out_str3.strip())

    def test_select_name3(self):
        argv = ['-ts', 'Nom < Mon', 'examples/math101.txt']
        old_stdout = sys.stdout
        sys.stdout = mystdout = io.StringIO()
        runner.run(argv)
        sys.stdout = old_stdout
        assert_equal(mystdout.getvalue().strip(), self.out_str4.strip())

    def test_select_test_2(self):
        argv = ['-ts', 'Test 2 >= 80', 'examples/math101.txt']
        old_stdout = sys.stdout
        sys.stdout = mystdout = io.StringIO()
        runner.run(argv)
        sys.stdout = old_stdout
        assert_equal(mystdout.getvalue().strip(), self.out_str5.strip())

    def test_select_ne(self):
        argv = ['-ts', 'Test 2 != ABS', 'examples/math101.txt']
        old_stdout = sys.stdout
        sys.stdout = mystdout = io.StringIO()
        runner.run(argv)
        sys.stdout = old_stdout
        assert_equal(mystdout.getvalue().strip(), self.out_str6.strip())

    def test_invalid_select(self):
        argv = ['-ts', 'Test / 2', 'examples/math101.txt']
        assert_raises(Exception, runner.run, argv)

    def test_select_empty(self):
        argv = ['-ts', 'Test 2 = -1', 'examples/math101.txt']
        old_stdout = sys.stdout
        sys.stdout = mystdout = io.StringIO()
        runner.run(argv)
        sys.stdout = old_stdout
        assert_equal(mystdout.getvalue().strip(), self.out_str7.strip())
