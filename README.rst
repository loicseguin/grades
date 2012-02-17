Grades
======

For managing student grades, most teachers use spreadsheet tools. With these
tools, it is hard to maintain grades in plain text files that are easily
readable by humans. The goal of **grades** is to let teachers manage their
students' grade in plain text file while providing tools to parse the file and
calculate students and group means.

**Grades** uses the same table format as Emacs `org-mode
<http://orgmode.org/index.html>`_. Using org-mode, grades tables can be
easily set up and then **grades** will happily compute all the required values.

Example
-------
A teacher as two groups of students. He created the following table in a text
file named ``mygrades.txt`` with his `favourite <http://www.vim.org/>`_ `editor
<http://www.gnu.org/software/emacs/>`_.

::

  * Grades for MATH101.
  I wonder what happened to Bob Arthur's midterm and to Albert Prévert's Test
  1. Maybe they've eaten the salmon mousse.

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

  * Next class: How to add numbers
  As an exercise, ask the students to count the number of pencils in their
  pencil case.

The teacher needs to know the cumulative grade for each student. He would also
like to see the mean for each evaluation for all the students as well as for
each group. It would be nice to have the results printed out so that the two
groups have a separator between them. To achieve all of this, the teacher
simply types

::

  grades -d 'Group' -mcg 'Group' mygrades.txt

and the following gets printed to his terminal screen

::

  * Grades for MATH101.
  I wonder what happened to Bob Arthur's midterm and to Albert Prévert's Test
  1. Maybe they've eaten the salmon mousse.
  
  | Nom               | Group | Test 1 | Test 2 | Midterm | /Cumul/ |
  |                   |       |  70.00 | 100.00 |  100.00 |         |
  |                   |       |  10.00 |  10.00 |   30.00 |         |
  |-------------------+-------+--------+--------+---------+---------|
  | Bob Arthur        | 301   |  23.00 |  45.00 |         |    7.79 |
  | Suzanne Tremblay  | 301   |  67.00 |  78.00 |   80.00 |   41.37 |
  | Albert Prévert    | 301   |        | ABS    |   78.00 |   23.40 |
  | André Arthur      | 301   |  75.00 |  91.00 |   65.00 |   39.31 |
  |-------------------+-------+--------+--------+---------+---------|
  | Roger Gagnon      | 302   |  67.00 |  78.00 |   80.00 |   41.37 |
  | Eleonor Brochu    | 302   |  67.00 |  78.00 |   80.00 |   41.37 |
  | Capitaine Haddock | 302   |  34.00 |  84.00 |   99.00 |   42.96 |
  | Buster Keaton     | 302   |  56.00 |  43.00 |   66.00 |   32.10 |
  | Alicia Keys       | 302   |  82.00 | ABS    |   73.00 |   33.61 |
  |-------------------+-------+--------+--------+---------+---------|
  | /Moyenne/         |       |  58.88 |  71.00 |   77.62 |   33.70 |
  | /Moyenne 301/     |       |  55.00 |  71.33 |   74.33 |   27.97 |
  | /Moyenne 302/     |       |  61.20 |  70.75 |   79.60 |   38.28 |
  
  * Next class: How to add numbers
  As an exercise, ask the students to count the number of pencils in their
  pencil case.

Notice how the text before and after the table was preserved.

The teacher also wants to see the list of students with the lowest cumulative
grades and he would like to hide the columns for the tests and group. Moreover,
he would like to print only the table, not the text that precedes and follows.
The following command does just that.

::

  grades -mc -C Nom,Midterm -s "/Cumul/<35" -t

::

  | Nom            | Midterm | /Cumul/ |
  |                |  100.00 |         |
  |                |   30.00 |         |
  |----------------+---------+---------|
  | Albert Prévert |   78.00 |   23.40 |
  | Buster Keaton  |   66.00 |   32.10 |
  | Alicia Keys    |   73.00 |   33.61 |
  |----------------+---------+---------|
  | /Moyenne/      |   72.33 |   29.70 |

Features
--------
* Calculate the weighted mean for each student.
* Calculate the mean for each evaluation (global mean or mean per group).
* Print the results with user chosen divisions.
* Print selected evaluations.
* Print selected students.

Installation
------------
To install, download the `tarball
<https://github.com/loicseguin/grades/tarball/master>`_ or clone the git
repository

::

  git clone git://github.com/loicseguin/grades.git

Then, proceed to the installation using the setup script.

::

  python setup.py install

Usage
-----
See ``grades --help`` for details.

