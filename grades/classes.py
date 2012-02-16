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


from __future__ import print_function


__author__ = "Loïc Séguin-C. <loicseguin@gmail.com>"
__license__ = "BSD"
__version__ = "0.1"


from collections import defaultdict
from copy import deepcopy


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
    def __init__(self, fileh):
        """Initialize the GradesFile object by parsing filename."""
        object.__init__(self)
        self.header = []
        self.footer = []
        tablelines = []
        if not hasattr(fileh, 'read'):
            fileh = open(fileh, 'r')
        lines = [line for line in fileh]
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
            raise Exception('Malformed table in file ' + fileh.name)
        self.table = GradesTable(tablelines)
        self.writer = TableWriter(self.table)

    def print_file(self, div_on=None, columns=None, tableonly=False):
        """Print the file and the table."""
        if not tableonly:
            for line in self.header:
                print(line)
        self.writer.printt(div_on=div_on, columns=columns)
        if not tableonly:
            for line in self.footer:
                print(line)


class GradesTable(object):
    """A GradesTable contains all the data in a table and can perform
    calculations and modify the table to include the results.

    """
    def __init__(self, data=None):
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

        if isinstance(data, GradesTable):
            self = deepcopy(data)
        elif data:
            self.__parse_data(data)

    def __getitem__(self, aslice):
        """A table can be indexed or sliced. The slicing mechanism work on rows
        of students. A new table is created that contains only the students
        included in ``aslice``. All the columns and their headers are copied
        into the new table.

        """
        atable = GradesTable()
        atable.columns = deepcopy(self.columns)
        atable.nb_col_headers = self.nb_col_headers
        atable.evals = deepcopy(self.evals)
        if isinstance(aslice, slice):
            atable.students = self.students[aslice]
        else:
            atable.students = [self.students[aslice]]
        return atable

    def __parse_data(self, data):
        """Parse lines into table row.

        Input
        -----
        data: iterable
           A list of all the rows in the table.

        """
        # First line contains columns titles.
        col_titles = [entry for entry in _parse_line(data[0])
                     if not entry.startswith('-')]
        # Try to determine which column is an evaluation.
        eval_colnum = [i for i, ctitle in enumerate(col_titles) if
                       ctitle.upper().startswith(('TEST', 'EXAM', 'MIDTERM',
                       'QUIZ', 'FINAL', 'EVAL'))]
        eval_names = [col_titles[i] for i in eval_colnum]
        # Array that contains True for columns that are evaluations and False
        # for the other columns.
        is_num_col = [i in eval_colnum for i in range(len(col_titles))]

        # Second line contains the maximum grade for each evaluation. If
        # no maximum is provided, a default value of 100 is used.
        eval_max = [_to_float(entry, 100.) for i, entry in
                    enumerate(_parse_line(data[1]))
                    if i in eval_colnum]
        # Third line contains the weight of the evaluation (defaults to 0.)
        eval_weight = [_to_float(entry, 0.) for i, entry in
                       enumerate(_parse_line(data[2]))
                       if i in eval_colnum]

        # Evaluations are stored as a list of dictionaries.
        self.evals = [dict((('name', name), ('max_grade', maxg),
                            ('weight', weight)))
                      for name, maxg, weight
                      in zip(eval_names, eval_max, eval_weight)]

        # Generator that yields None for columns that are not evaluations and
        # that yields the evaluation for columns that are evaluations.
        evals_iter = self.evals.__iter__()
        col_evals = (next(evals_iter) if is_num else None
                     for is_num in is_num_col)

        # Columns are stored as a list of dictionaries.
        self.columns = [dict((('title', ctitle), ('is_num', isnum),
                              ('evalu', evalu), ('width', 0),
                              ('to_print', True)))
                        for ctitle, isnum, evalu in
                        zip(col_titles, is_num_col, col_evals)]

        # The next lines contain student records. Students are stored as a
        # list of defaultdict keyed by column title with a str default factory.
        for line in data[self.nb_col_headers:]:
            if line.startswith('|-'):
                # Separator line in the table.
                continue
            keyval = []
            for i, entry in enumerate(_parse_line(line)):
                if i >= len(self.columns) or entry.startswith('--'):
                    break
                if self.columns[i]['is_num']:
                    keyval.append((self.columns[i]['title'],
                                   _to_float(entry, entry)))
                else:
                    # This is necessary to avoid casting groups numbers into
                    # floats, which looks weird when printed.
                    keyval.append((self.columns[i]['title'], entry))

            if keyval:
                self.students.append(defaultdict(str, keyval))

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
        self.columns.append({'title': '-- Cumul --', 'is_num': True,
                             'evalu': None, 'width': 0, 'to_print': True})

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
        mean = defaultdict(str)
        mean[self.columns[0]['title']] = '-- ' + row_name + ' --'
        if not students:
            students = self.students
        for column in self.columns[1:]:
            col_title = column['title']
            if column['is_num']:
                nb_students = sum((1 for student in students if
                                  isinstance(student[col_title], (float, int))))
                sumg = sum((student[col_title] for student in students
                         if isinstance(student[col_title], (float, int))))
                if nb_students:
                    mean[col_title] = sumg / nb_students
        self.footers.append(mean)

    def compute_grouped_mean(self, group_by='Group'):
        """Calculate grouped means. The values for each evaluation and computed
        columns are added as footers to the table.

        Parameters
        ----------
        group_by: string
           A column title to be used to group students. The mean is calculated
           for groups of students that have the same value for the column
           group_by.

        Raises
        ------
        ValueError:
            This exception is raised if group_by is not a column title.

        """
        if not group_by in [col['title'] for col in self.columns]:
            raise ValueError(group_by + " is not a valid column title.")
        groups = defaultdict(list)
        for student in self.students:
            groups[student[group_by]].append(student)
        for group in groups:
            self.compute_mean(students=groups[group],
                              row_name='Moyenne ' + str(group))


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

    def __str__(self):
        """Used to print()."""
        self.__set_columns_width()
        return self.as_str()

    def as_str(self, div_on=None, columns=None):
        """Return a string representation of the table.

        Parameters
        ----------
        div_on: tuple
           Horizontal divisions will be written between rows for which one of
           the values in the div_on tuple are different. div_on should contain
           column names.

        columns: iterable
           List of columns to print. By default, this is None which prints all
           the columns.

        """
        if columns:
            for column in self.table.columns:
                column['to_print'] = column['title'] in columns
        self.__set_columns_width()
        return self.header_str() + self.rows_str(div_on) + self.footer_str()

    def printt(self, div_on=None, columns=None):
        """Print the table.

        Parameters
        ----------
        div_on: tuple
           Horizontal divisions will be written between rows for which one of
           the values in the div_on tuple are different. div_on should contain
           column names.

        columns: iterable
           List of columns to print. By default, this is None which prints all
           the columns.

        """
        print(self.as_str(div_on=div_on, columns=columns), end='')

    def header_str(self):
        """Generate a string containing the header for the table."""
        # Column names row.
        str_hdr = self.__row_str(col['title'] for col in self.table.columns)

        # Max and weight rows. These are filled only for evaluation columns.
        max_row = []
        weight_row = []
        for column in self.table.columns:
            if column['evalu']:
                max_row.append(column['evalu']['max_grade'])
                weight_row.append(column['evalu']['weight'])
            else:
                max_row.append('')
                weight_row.append('')
        str_hdr += self.__row_str(max_row) + self.__row_str(weight_row)
        str_hdr += self.__div_row()
        return str_hdr

    def print_header(self):
        """Print headers for the table."""
        print(self.header_str(), end='')

    def rows_str(self, div_on=None):
        """Generate a string containing all the rows for the table.

        Parameters
        ----------
        div_on: tuple
           Horizontal divisions will be written between rows for which one of
           the values in the div_on tuple are different. div_on should contain
           column titles.

        """
        str_tbl = ''
        col_titles = [col['title'] for col in self.table.columns]
        if div_on:
            for ctitle in div_on:
                if not ctitle in col_titles:
                    raise ValueError(ctitle + " is not a valid column title.")
            prevs = [self.table.students[0][ctitle] for ctitle in div_on]
        for student in self.table.students:
            if div_on:
                curs = [student[ctitle] for ctitle in div_on]
                for prev, cur in zip(prevs, curs):
                    if prev != cur:
                        str_tbl += self.__div_row()
                        break
                prevs = curs
            str_tbl += self.__row_str(student[ctitle] for ctitle in col_titles)
        return str_tbl

    def print_rows(self, div_on=None):
        """Print the data rows.

        Parameters
        ----------
        div_on: tuple
           Horizontal divisions will be written between rows for which one of
           the values in the div_on tuple are different. div_on should contain
           column titles.

        """
        print(self.rows_str(div_on), end='')

    def footer_str(self):
        """Generate string for the footer of the table."""
        str_ftr = ''
        if self.table.footers:
            str_ftr += self.__div_row()
            col_titles = [col['title'] for col in self.table.columns]
            for footer in self.table.footers:
                str_ftr += self.__row_str(footer[ctitle] for ctitle in
                        col_titles)
        return str_ftr

    def print_footer(self):
        """Print footer for the table."""
        print(self.footer_str(), end='')

    def __set_columns_width(self):
        """Find the width of each column. The width of a column is the maximum
        width of an entry in this column plus the padding.

        """
        rows = self.table.students + self.table.footers
        for column in self.table.columns:
            ctitle = column['title']
            col_contents = [ctitle]
            if column['is_num']:
                for row in rows:
                    if isinstance(row[ctitle], (float, int)):
                        # Numerical data will be formatted to self.precision.
                        # Calculate the width of the formatted numbers.
                        col_contents.append(
                                format(row[ctitle], '.%df' % self.precision))
                    else:
                        # Allow some cells to contain non numerical data such
                        # as 'ABS' for absences.
                        col_contents.append(row[ctitle])
            else:
                col_contents += [row[ctitle] for row in rows]
            column['width'] = (self.padding_left + self.padding_right +
                               max(_len(str(row)) for row in col_contents))

    def __row_str(self, row):
        """Create a string representation for a row in the table. The columns
        corresponding to evaluations have their numbers justified right.

        """
        padded = []
        for i, rowelmt in enumerate(row):
            if not self.table.columns[i]['to_print']:
                continue
            width = self.table.columns[i]['width']
            if (self.table.columns[i]['is_num']
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
        """Return a division that looks like |-----+------+------|."""
        div = '|' + '+'.join('-' * col['width'] for col in
                             self.table.columns if col['to_print'])
        return div + '|\n'


if __name__ == '__main__':
    test_data = """\
| Nom               |Group | Test 1 | Test 2 | Midterm | --Cumul-- |
|                   |      | 70     | 100    |         |           |
|                   |      | 10     | 10     | 30      |           |
|-------------------+------+--------+--------+---------+-----------|
| Bob Arthur        | 301  | 23     | 45     |         |           |
| Suzanne Tremblay  | 302  | 67     | 78     | 80      |           |
| Albert Prévert    | 302  |        | ABS    | 78      |           |
| -- Some stuff--   | This row | should | be |         | ignored   |
"""
    grades_tbl = GradesTable(test_data.strip().split('\n'))
    writer = TableWriter(grades_tbl)
    grades_tbl.compute_cumul()
    grades_tbl.compute_mean()
    grades_tbl.compute_grouped_mean()
    writer.printt()

    gfile = GradesFile('examples/math101.txt')
    gfile.table.compute_cumul()
    gfile.table.compute_grouped_mean()
    gfile.print_file(columns=('Nom', 'Test 2'))
