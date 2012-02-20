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


from collections import defaultdict
from copy import deepcopy
import re


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
        """Initialize the GradesFile object by parsing fileh."""
        object.__init__(self)
        self.header = []
        self.footer = []
        tablelines = []
        if not hasattr(fileh, 'read'): # Not a file object, maybe a file name?
            fileh = open(fileh, 'r')
        for line in fileh:
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

    def print_file(self, div_on=None, columns=None, tableonly=False):
        """Print the file and the table."""
        writer = TableWriter(self.table)
        if tableonly:
            writer.printt(div_on=div_on, columns=columns)
        else:
            print('\n'.join(self.header))
            writer.printt(div_on=div_on, columns=columns)
            print('\n'.join(self.footer))


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
        self.students = []
        self.footers = []

        if isinstance(data, GradesTable):
            self.nb_col_headers = data.nb_col_headers
            self.columns = deepcopy(data.columns)
            self.students = deepcopy(data.students)
            self.footers = deepcopy(data.footers)
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
        if isinstance(aslice, slice):
            atable.students = self.students[aslice]
        else:
            atable.students = [self.students[aslice]]
        return atable

    def __iter__(self):
        """Iterating over the table iterates through the list of students."""
        return self.students.__iter__()

    def __add__(self, atable):
        """Adding a table to a table creates a new table with the union of the
        students in both tables. Adding a student to a table, appends the
        student to the list of students."""
        sumtable = GradesTable(self)
        if isinstance(atable, GradesTable):
            if self.columns != atable.columns:
                raise TypeError('Cannot add tables with different headers.')
            for student in atable:
                sumtable.students.append(student)
        elif isinstance(atable, defaultdict):
            if set(atable.keys()) != set(col['title'] for col in self.columns):
                raise TypeError('Cannot add a student with different keys.')
            sumtable.students.append(atable)
        return sumtable

    def __str__(self):
        """String representation for the table using a TableWriter."""
        writer = TableWriter(self)
        return writer.as_str()

    def __parse_data(self, data):
        """Parse lines into table row.

        Input
        -----
        data: iterable
           A list of all the rows in the table.

        """
        # The first three line contains columns headers. If a column
        # corresponds to an evaluation, the first line is the title, the second
        # line is the maximum grade and the third line is the weight.
        # Otherwise, the first line is the title and the two other lines are
        # ignored.
        entry_sep = re.compile('\s*\|\s*')
        header_lines = (entry_sep.split(line)[1:-1] for line in data[:3])
        headers = zip(*header_lines)
        for header in headers:
            if header[0].startswith('/'):  # Reserved for calculated columns
                continue
            if header[0].upper().startswith(('TEST', 'EXAM', 'MIDTERM',
                                             'QUIZ', 'FINAL', 'EVAL')):
                evalu = {'max_grade': _to_float(header[1], 100.),
                         'weight': _to_float(header[2], 0.)}
                self.columns.append(
                        {'title': header[0], 'is_num': True, 'evalu': evalu,
                         'width': 0, 'to_print': True})
            else:
                self.columns.append(
                        {'title': header[0], 'is_num': False, 'evalu': None,
                         'width': 0, 'to_print': True})

        # The next lines contain student records. Students are stored as a
        # list of defaultdict keyed by column title with a str default factory.
        for line in data[self.nb_col_headers:]:
            if line.startswith('|-'):  # Separator line in the table
                continue
            student = defaultdict(str)
            for i, entry in enumerate(entry_sep.split(line)[1:-1]):
                if i >= len(self.columns) or entry.startswith('/'):
                    break
                if self.columns[i]['is_num']:
                    student.update(
                        [(self.columns[i]['title'], _to_float(entry, entry))])
                else:
                    # This is necessary to avoid casting groups numbers into
                    # floats, which looks weird when printed.
                    student.update([(self.columns[i]['title'], entry)])
            if student:
                self.students.append(student)

    def compute_cumul(self):
        """Calculate the weighted mean for each student and add that result
        in a new column at the end of the table.

        """
        for student in self.students:
            student['/Cumul/'] = sum(
                    (student[column['title']] * column['evalu']['weight']
                     / column['evalu']['max_grade']
                     for column in self.columns
                     if column['evalu']
                     and isinstance(student[column['title']], (float, int))))
        self.columns.append({'title': '/Cumul/', 'is_num': True,
                             'evalu': None, 'width': 0, 'to_print': True})

    def compute_mean(self, students=None, row_name='Mean'):
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
        mean[self.columns[0]['title']] = '/' + row_name + '/'
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
                              row_name='Mean ' + str(group))

    def select(self, expression):
        """Select a subset of students based on expression.

        Parameter
        ---------
        expression: string
           An expression is composed of a column name, one of the symbols '>',
           '>=', '<', '<=' or '=' and a value.
        """
        sep = re.compile('(==?|[<>]=?|!=)')
        splitted = sep.split(expression, maxsplit=1)
        if len(splitted) == 3:
            sel_table = GradesTable()
            col_title, sep, value = splitted
            col_title = col_title.strip()
            value = value.strip()
            if not col_title in [col['title'] for col in self.columns]:
                raise KeyError('%s is not a column title.' % col_title)
            sel_table.columns = deepcopy(self.columns)
            sel_table.nb_col_headers = self.nb_col_headers
            if sep == '=':
                sep = '=='
            for student in self.students:
                try:
                    if student[col_title]:
                        if eval('"' + str(student[col_title]) + '"'
                                + sep + '"' + value + '"',
                                {"__builtins__": None},{}):
                            sel_table += student
                except ValueError:
                    pass
        else:
            raise Exception("Invalid SELECT statement: %s" % expression)
        return sel_table


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

        if not self.table.students:
            # Empty table, nothing to return.
            return str_tbl

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
| Nom               |Group | Test 1 | Test 2 | Midterm | /Cumul/   |
|                   |      | 70     | 100    |         |           |
|                   |      | 10     | 10     | 30      |           |
|-------------------+------+--------+--------+---------+-----------|
| Bob Arthur        | 301  | 23     | 45     |         |           |
| Suzanne Tremblay  | 302  | 67     | 78     | 80      |           |
| Albert Prévert    | 302  |        | ABS    | 78      |           |
| /Some stuff/      | This row | should | be |         | ignored   |
"""
    grades_tbl = GradesTable(test_data.strip().split('\n'))
    twriter = TableWriter(grades_tbl)
    grades_tbl.compute_cumul()
    grades_tbl.compute_mean()
    grades_tbl.compute_grouped_mean()
    twriter.printt()

    gfile = GradesFile('examples/math101.txt')
    gfile.table.compute_cumul()
    gfile.table.compute_grouped_mean()
    gfile.print_file(columns=('Nom', 'Test 2'))
