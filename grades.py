#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""grades

This module provides classes that can parse and process student grades stored
in plain text tables. The table has the following form.

| Header 1  | Header 2 | Eval 1  | Eval 2  |
|           |          | max1    | max2    |
|           |          | weight1 | weight2 |
|-----------+----------+---------+---------|
| A Name    | Info     | 45      |  56     |
| An Other  | More Inf | 57      | 43      |

Evaluations should have a name that starts with 'Test', 'Exam', 'Midterm',
'Eval' or 'Quiz' in order to be recognized as evaluations. Each evaluation has
a maximum grade and a weight towards the final grade. If a maximum is not
given, a value of 100 is assumed. If a weight is not given, a value of 0 is
assumed.

The methods offered by GradesTable can compute the mean for each evaluation,
the final grade of each student as well as the class mean for each evaluation.
The class mean uses one of the columns to group the students.

"""


from __future__ import print_function  # For Python 2 compatibility.


__author__ = "Loïc Séguin-C. <loicseguin@gmail.com>"
__license__ = "BSD"
__version__ = "0.1"


def _parse_line(line):
    """Read a line and split it into tokens. This is a generator that
    yields the tokens. A typical line looks like '| A Name | info | 78 | 90|'
    and gets parsed into the following tokens: 'A Name', 'info', 78, 90.

    """
    for entry in line.strip('|').split('|'):
        yield entry.strip()


def _to_float(val, default=100.):
    """Convert string val into float with fallback value default."""
    try:
        return float(val)
    except ValueError:
        return default


def _len(iterable):
    """Redefine len so it will be able to work with non-ASCII characters.
    This function is adapted from http://foutaise.org/code/texttable/texttable.
    Works with Python 2 and Python 3.

    """
    if not isinstance(iterable, str):
        return iterable.__len__()
    try:
        return len(unicode(iterable, 'utf'))
    except NameError:
        return iterable.__len__()


class GradesFile(object):
    """A GradesFile contains one table of grades. The GradesFile
    object is initialized with a filename. It takes care of safeguarding the
    content of the file before and after the table.

    """
    def __init__(self, filename):
        """Initialize the GradesFile object by parsing filename."""
        object.__init__(self)
        self.header = []
        self.footer = []
        tablelines = []
        lines = [line for line in open(filename, 'r')]
        for line in lines:
            line = line.strip()
            if not line.startswith('|'):
                if not tablelines:
                    # Reading the header.
                    self.header.append(line)
                else:
                    # Reading the footer.
                    self.footer.append(line)
            else:
                # Reading a table.
                tablelines.append(line)
        if len(tablelines) < 3:
            raise StandardError('Error: Malformed table in file ' + filename)
        self.table = GradesTable(tablelines)
        self.writer = TableWriter(self.table)

    def print_file(self):
        """Print the file and the table."""
        for line in self.header:
            print(line)
        self.writer.printt()
        for line in self.footer:
            print(line)


class GradesTable(object):
    """A GradesTable contains all the data in a table and can perform
    calculations and modify the table to include the results.

    """
    def __init__(self, data):
        """Instanciate a new GradesTable.

        Input
        -----
        data: list
           A list of all the rows in the table.

        """
        object.__init__(self)
        self.columns = []
        self.nb_col_headers = 3
        self.evals = []
        self.students = []
        self.footers = []
        # The first three lines contain information about the evaluations.
        self.columns = [entry for entry in _parse_line(data[0])
                        if not entry.startswith('-')]
        # Try to determine which column is an evaluation.  Evaluations are
        # stored as dictionaries with keys name, max_grade and weight.
        eval_colnum = [i for i, cname in enumerate(self.columns) if
                       cname.upper().startswith(('TEST', 'EXAM', 'MIDTERM',
                       'QUIZ', 'FINAL', 'EVAL'))]
        eval_names = [self.columns[i] for i in eval_colnum]
        self.num_columns = list(eval_names)
        eval_max = [_to_float(entry) for i, entry in
                    enumerate(_parse_line(data[1]))
                    if i in eval_colnum]
        eval_weight = [_to_float(entry, 0.) for i, entry in
                       enumerate(_parse_line(data[2]))
                       if i in eval_colnum]
        self.evals = [dict((('name', name), ('max_grade', maxg),
                           ('weight', weight))) for name, maxg, weight
                      in zip(eval_names, eval_max, eval_weight)]
        self.eval_names = eval_names

        # The next lines contain student records. Students are stored as a
        # list of dictionaries keyed by column name.
        for line in data[self.nb_col_headers:]:
            if line.startswith('|-'):
                # Separator line in the table.
                continue
            keyval = []
            for i, entry in enumerate(_parse_line(line)):
                if i >= len(self.columns) or entry.startswith('--'):
                    break
                if self.columns[i] in self.eval_names:
                    keyval.append((self.columns[i],
                        _to_float(entry, entry)))
                else:
                    keyval.append((self.columns[i], entry))

            if keyval:
                self.students.append(dict(keyval))

    def compute_cumul(self):
        """Calculate the weighted mean for each student and add that result
        in a new column at the end of the table.

        """
        for student in self.students:
            cumul = sum((student[evalu['name']] * evalu['weight'] /
                         evalu['max_grade']
                         for evalu in self.evals if
                         isinstance(student[evalu['name']], (float, int))))
            student['-- Cumul --'] = cumul
        self.columns.append('-- Cumul --')
        self.num_columns += ['-- Cumul --']

    def compute_mean(self, students=None, row_name='Moyenne'):
        """Calculate the mean for each evaluation and add the results to
        a new row at the bottom of the table. Blanks in the table are not taken
        into account, i.e., a blank does not count as a zero.

        Input
        -----
        students: iterable container
           Container for the students to include in the calculation. This list
           should be a subset of the students in the table.

        row_name: string
           Name to use for the new footer row that contains the mean values.

        """
        mean = {}
        mean[self.columns[0]] = '-- ' + row_name + ' --'
        if not students:
            students = self.students
        for column in self.columns[1:]:
            mean[column] = ''
            if column in self.eval_names or column.startswith('--'):
                nb_students = sum((1 for student in students if
                                  isinstance(student[column], (float, int))))
                sumg = sum((student[column] for student in students
                         if isinstance(student[column], (float, int))))
                if nb_students:
                    mean[column] = sumg / nb_students
        self.footers.append(mean)

    def compute_grouped_mean(self, group_by='Group'):
        """Calculate grouped means. The values for each evaluation and computed
        columns are added as footers to the table.

        Parameters
        ----------
        group_by: string
           A column name to be used to group students. The mean is calculated
           for groups of students that have the same value for the column
           group_by.

        Raises
        ------
        ValueError:
            This exception is raised if group_by is not a column name.

        """
        if not group_by in self.columns:
            raise ValueError(group_by + " is not a valid column name.")
        groups = {}
        for student in self.students:
            if not student[group_by] in groups:
                groups[student[group_by]] = [student]
            else:
                groups[student[group_by]].append(student)
        for group in groups:
            self.compute_mean(students=groups[group],
                              row_name='Moyenne ' + group)


class TableWriter(object):
    """A TableWriter takes care of formatting and printing a GradesTable."""
    def __init__(self, grade_table):
        """Initialize the writer. The default parameters for a writer are to
        use a minimum column width of 5, left and right padding of 1 and a
        precision for floating point values of 2.

        """
        object.__init__(self)
        self.min_width = 5
        self.padding_left = 1
        self.padding_right = 1
        self.table = grade_table
        self.precision = 2
        self.column_widths = []

    def printt(self, div_on=('Group',)):
        """Print the table.

        Parameters
        ----------
        div_on: tuple
           Horizontal divisions will be written between rows for which one of
           the values in the div_on tuple are different. div_on should contain
           column names.

        """
        self.__set_columns_width()
        self.print_header()
        self.print_rows(div_on)
        self.print_footer()

    def print_header(self):
        """Print headers for the table."""
        # Column names row.
        str_hdr = self.__row_str(self.table.columns)

        # Max and weight rows. These are filled only for evaluation columns.
        i = 0
        max_row = []
        weight_row = []
        for column in self.table.columns:
            if column in self.table.eval_names:
                max_row.append(self.table.evals[i]['max_grade'])
                weight_row.append(self.table.evals[i]['weight'])
                i += 1
            else:
                max_row.append('')
                weight_row.append('')
        str_hdr += self.__row_str(max_row) + self.__row_str(weight_row)
        str_hdr += self.__div_row()
        print(str_hdr, end='')

    def print_rows(self, div_on=None):
        """Print the data rows.

        Parameters
        ----------
        div_on: tuple
           Horizontal divisions will be written between rows for which one of
           the values in the div_on tuple are different. div_on should contain
           column names.

        """
        str_tbl = ''
        if div_on:
            prevs = [self.table.students[0][cname] for cname in div_on]
        for student in self.table.students:
            if div_on:
                curs = [student[cname] for cname in div_on]
                for prev, cur in zip(prevs, curs):
                    if prev != cur:
                        str_tbl += self.__div_row()
                        break
                prevs = curs
            str_tbl += self.__row_str(
                    (student[cname] for cname in self.table.columns))
        print(str_tbl, end='')

    def print_footer(self):
        """Print footer for the table."""
        str_ftr = ''
        if self.table.footers:
            str_ftr += self.__div_row()
            for footer in self.table.footers:
                str_ftr += self.__row_str((footer[cname] for cname in
                    self.table.columns))
        print(str_ftr, end='')

    def __set_columns_width(self):
        """Find the width of each column. The width of a column is the maximum
        width of an entry in this column plus the padding.

        """
        self.column_widths = []
        rows = self.table.students + self.table.footers
        for column in self.table.columns:
            col = [column]
            if column in self.table.num_columns:
                for row in rows:
                    if isinstance(row[column], (float, int)):
                        # Numerical data will be formatted to self.precision.
                        # Calculate the width of the formatted numbers.
                        col += [format(row[column], '.%df' % self.precision)]
                    else:
                        # Allow some cells to contain non numerical data such
                        # as 'ABS' for absences.
                        col += [row[column]]
            else:
                col += [row[column] for row in rows]
            self.column_widths.append(self.padding_left + self.padding_right +
                                      max(_len(str(row)) for row in col))

    def __row_str(self, row):
        """Create a string representation for a row in the table. The columns
        corresponding to evaluations have their numbers justified right.

        """
        padded = []
        for i, rowelmt in enumerate(row):
            width = self.column_widths[i]
            if (self.table.columns[i] in self.table.num_columns
                and isinstance(rowelmt, (float, int))):
                str_elmt = format(rowelmt, '.%df' % self.precision)
                padded.append(
                        ' ' * (width - _len(str_elmt) - self.padding_right)
                        + str_elmt + ' ' * self.padding_right)
            elif isinstance(rowelmt, (float, int)):
                padded.append(' ' * self.padding_left + str(rowelmt)
                    + ' ' * (width - _len(str(rowelmt)) - self.padding_left))
            else:
                padded.append(' ' * self.padding_left + str(rowelmt)
                        + ' ' * (width - _len(rowelmt) - self.padding_left))
        return '|' + '|'.join(padded) + '|\n'

    def __div_row(self):
        """Return a division that look like |-----+------+------|."""
        div = '|' + '+'.join(('-' * width for width in self.column_widths))
        return div + '|\n'


if __name__ == '__main__':
    test_data = """| Nom    |Group | Test 1 | Test 2 | Midterm | --Cumul-- |
|                   |   | 70     | 100    |     |           |
|                   |   | 10     | 10     | 30      |           |
|----------------------+--------+--------+---------+-----------|
| Bob Arthur        | 301   | 23     | 45     |         |           |
| Suzanne Tremblay  | 302   | 67     | 78     | 80      |           |
| Albert Prévert    | 302   |        | ABS    | 78      |           |
| -- Some stuff--   | This row | should | be |    | ignored |"""
    #grades_tbl = GradesTable(test_data.split('\n'))
    #writer = TableWriter(grades_tbl)
    #grades_tbl.compute_cumul()
    #grades_tbl.compute_mean()
    #grades_tbl.compute_grouped_mean()
    #writer.printt()
    gfile = GradesFile('some_grades.org')
    gfile.table.compute_cumul()
    gfile.table.compute_grouped_mean()

    gfile.print_file()
