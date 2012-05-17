#-*- coding: utf-8 -*-
"""Grades table writer

"""


from __future__ import print_function


__author__ = "Loïc Séguin-C. <loicseguin@gmail.com>"
__license__ = "BSD"


import sys
from . import parser


class GradesFile:
    """A GradesFile contains one table of grades. The GradesFile
    object is initialized with a filename. It takes care of safeguarding the
    content of the file before and after the table.

    """
    def __init__(self, fileh):
        """Initialize the GradesFile object by parsing fileh."""
        self.header = []
        self.footer = []
        tablerows = []
        if not hasattr(fileh, 'read'): # Not a file object, maybe a file name?
            fileh = open(fileh, 'r')
        for row in fileh:
            row = row.strip()
            if not row.startswith('|'):
                if not tablerows:
                    # Reading the header.
                    self.header.append(row)
                else:
                    # Reading the footer.
                    self.footer.append(row)
            else:
                # Reading a table.
                tablerows.append(row)
        if len(tablerows) < 3:
            raise Exception('Malformed table in file ' + fileh.name)
        self.table = parser.parse_table(tablerows)

    def print_file(self, div_on=None, columns=None, tableonly=False,
            file=sys.stdout):
        """Print the file and the table."""
        twriter = TableWriter(self.table)
        if tableonly:
            twriter.printt(div_on=div_on, columns=columns, file=file)
        else:
            print('\n'.join(self.header), file=file)
            twriter.printt(div_on=div_on, columns=columns, file=file)
            print('\n'.join(self.footer), file=file)


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


class TableWriter:
    """A TableWriter takes care of formatting and printing a GradesTable."""

    def __init__(self, grade_table):
        """Initialize the writer. The default parameters for a writer are to
        use a minimum column width of 5, left and right padding of 1 and a
        precision for floating point values of 2.

        """
        self.min_width = 5
        self.padding_left = 1
        self.padding_right = 1
        self.precision = 2
        self.table = grade_table
        self.columns_to_print = {}
        for column in self.table.columns:
            self.columns_to_print[column['title']] = True

    def __str__(self, div_on=None, columns=None):
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
                title = column['title']
                self.columns_to_print[title] = title in columns
        self.__set_columns_width()
        return self.header_str() + self.rows_str(div_on) + self.footer_str()

    def printt(self, div_on=None, columns=None, file=sys.stdout):
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

        file: stream object
           Stream where the ouput will be written.

        """
        print(self.__str__(div_on=div_on, columns=columns), end='', file=file)

    # Synonym for printt.
    write = printt

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
            col = self.table.columns[i]
            if not self.columns_to_print[col['title']]:
                continue
            width = col['width']
            if (col['is_num'] and isinstance(rowelmt, (float, int))):
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
                             self.table.columns if
                             self.columns_to_print[col['title']])
        return div + '|\n'
