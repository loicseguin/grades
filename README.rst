Grades
======

For managing student grades, most teachers use spreadsheet tools. With these
tools, it is hard to maintain grades in plain text files that are easily
readable by humans. The goal of **grades** is to let teachers manage their
students' grade in plain text file while providing tools to parse the file and
calculate students and group means.

**Grades** uses reStructuredText_ tables (either the simple version or the grid
version) or Emacs's org-mode_ tables.

.. _reStructuredText: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html
.. _org-mode: http://orgmode.org/

Example
-------
A teacher as two groups of students. He created the following table in a text
file named ``Grades.rst`` with his `favourite <http://www.vim.org/>`_ `editor
<http://www.gnu.org/software/emacs/>`_.  ::

    # Grades for MATH101 #
    I wonder what happened to Bob Arthur's midterm and to Albert Prévert's Test
    1. Maybe they've eaten the salmon mousse.

    =================== ======= ======== ======== =========
     Name                Group   Test 1   Test 2   Midterm
                                  70.00   100.00    100.00
                                  10.00    10.00     30.00
    =================== ======= ======== ======== =========
     Bob Arthur          301      23.00    45.00
     Suzanne Tremblay    301      67.00    78.00     80.00
     Albert Prévert      301              ABS        78.00
     André Arthur        301      75.00    91.00     65.00
     Roger Gagnon        302      67.00    78.00     80.00
     Eleonor Brochu      302      67.00    78.00     80.00
     Capitaine Haddock   302      34      84         99.00
     Buster Keaton       302      56      43         66.00
     Alicia Keys         302      82      ABS        73.00
    =================== ======= ======== ======== =========

    Next class: How to add numbers
    As an exercise, ask the students to count the number of pencils in their
    pencil case.

The teacher needs to know the cumulative grade for each student. He would also
like to see the mean for each evaluation for all the students as well as for
each group. It would be nice to have the results printed out so that the two
groups have a separator between them. To achieve all of this, the teacher
simply types ::

    $ grades print -d 'Group' -mcg 'Group'

and the following gets printed to his terminal screen ::

    # Grades for MATH101 #
    I wonder what happened to Bob Arthur's midterm and to Albert Prévert's Test
    1. Maybe they've eaten the salmon mousse.

    =================== ======= ======== ======== ========= =========
     Name                Group   Test 1   Test 2   Midterm   *Cumul*
                                  70.00   100.00    100.00
                                  10.00    10.00     30.00
    =================== ======= ======== ======== ========= =========
     Bob Arthur          301      23.00    45.00               38.93
     Suzanne Tremblay    301      67.00    78.00     80.00     82.74
     Albert Prévert      301              ABS        78.00     78.00
     André Arthur        301      75.00    91.00     65.00     78.63
    ------------------- ------- -------- -------- --------- ---------
     Roger Gagnon        302      67.00    78.00     80.00     82.74
     Eleonor Brochu      302      67.00    78.00     80.00     82.74
     Capitaine Haddock   302      34.00    84.00     99.00     85.91
     Buster Keaton       302      56.00    43.00     66.00     64.20
     Alicia Keys         302      82.00   ABS        73.00     84.04
    ------------------- ------- -------- -------- --------- ---------
     *Mean*                       58.88    71.00     77.62     75.33
     *Mean 301*                   55.00    71.33     74.33     69.57
     *Mean 302*                   61.20    70.75     79.60     79.93
    =================== ======= ======== ======== ========= =========

    Next class: How to add numbers
    As an exercise, ask the students to count the number of pencils in their
    pencil case.

Notice how the text before and after the table was preserved.

The teacher also wants to see the list of students with the lowest cumulative
grades and he would like to hide the columns for the tests and group. Moreover,
he would like to print only the table, not the text that precedes and follows.
The following command does just that.  ::

    $ grades print -mct -C "Name, Midterm" -s "*Cumul*<70"

    =============== ========= =========
     Name            Midterm   *Cumul*
                      100.00
                       30.00
    =============== ========= =========
     Bob Arthur                  38.93
     Buster Keaton     66.00     64.20
    --------------- --------- ---------
     *Mean*            66.00     51.56
    =============== ========= =========

If the teacher does not like the simple table format, he can get the table in
another format by using the ``-f`` or ``--format`` option ::

    $ grades print -mct -C "Name, Midterm" -s "*Cumul*<70" -f org

    | Name          | Midterm | *Cumul* |
    |               |  100.00 |         |
    |               |   30.00 |         |
    |---------------+---------+---------|
    | Bob Arthur    |         |   38.93 |
    | Buster Keaton |   66.00 |   64.20 |
    |---------------+---------+---------|
    | *Mean*        |   66.00 |   51.56 |

    $ grades print -mct -C "Name, Midterm" -s "*Cumul*<70" -f grid_rst

    +---------------+---------+---------+
    | Name          | Midterm | *Cumul* |
    |               |  100.00 |         |
    |               |   30.00 |         |
    +===============+=========+=========+
    | Bob Arthur    |         |   38.93 |
    +---------------+---------+---------+
    | Buster Keaton |   66.00 |   64.20 |
    +---------------+---------+---------+
    | *Mean*        |   66.00 |   51.56 |
    +---------------+---------+---------+



Features
--------
* Calculate the weighted mean for each student.
* Calculate the mean for each evaluation (global mean or mean per group).
* Print the results with user chosen divisions.
* Print selected evaluations.
* Print selected students.
* Handle special *assignment* evaluation type.
* Handle special *supplemental* evaluation type.
* Read GnuPG encrypted file.
* Generate table skeleton with ``init`` subcommand.
* Add student to a table with ``add student`` subcommand.
* Add column to a table wit ``add column`` subcommand.

Installation
------------
To install, download the tarball_ or clone the git repository ::

  git clone git://github.com/loicseguin/grades.git

Then, proceed to the installation using the setup script. ::

  python setup.py install

.. _tarball: https://github.com/loicseguin/grades/tarball/master

Usage
-----
See ``grades --help`` for details.

