#-*- coding: utf-8 -*-
"""Grades table writer

"""


from __future__ import print_function


__author__ = "Loïc Séguin-C. <loicseguin@gmail.com>"
__license__ = "BSD"


import sys
try:
    import cStringIO as io
except ImportError:
    try:
        import StringIO as io
    except ImportError:
        import io  # For Python 3
from . import defaults
from . import parsers


class GradesFile:
    """A GradesFile contains one table of grades. The GradesFile object is
    initialized with a file handle. It takes care of safeguarding the content
    of the file before and after the table.

    """
    def __init__(self, fileh, ignore_char=defaults.IGNORE_CHAR):
        """Initialize the GradesFile object by parsing fileh."""
        self.header = []
        self.table_format = defaults.TABLE_FORMAT
        self.footer = []
        tablerows = []
        if not hasattr(fileh, 'read'): # Not a file object, maybe a file name?
            fileh = open(fileh, 'r')
        if fileh.name.endswith('.asc'):
            try:
                import gnupg
            except ImportError:
                print("GradesFile: error: cannot import gnupg.  To read " +
                      "encrypted files, install python-gnupg.",
                      file=sys.stderr)
                sys.exit(10)
            gpg = gnupg.GPG()
            data = gpg.decrypt(fileh.read())
            fileh = io.StringIO(data.data.decode())
        is_table = False
        line = fileh.readline()
        while line:
            # Reading header
            line = line.strip()
            if line.startswith(('|', '+', '=')):
                break
            self.header.append(line)
            line = fileh.readline()
        while line.strip():
            # Reading table
            tablerows.append(line)
            line = fileh.readline()
        while line:
            # Reading footer
            line = line.strip()
            self.footer.append(line)
            line = fileh.readline()

        if len(tablerows) < 3:
            raise Exception('Malformed table in file ' + fileh.name)
        if tablerows[0][0] == '=':
            tparser = parsers.SimpleRSTParser(tablerows[0],
                    ignore_char=ignore_char)
        else:
            tparser = parsers.TableParser(ignore_char=ignore_char)
        self.table = tparser.parse(tablerows)

    def print_file(self, div_on=None, columns=None, tableonly=False,
            file=sys.stdout, **kwargs):
        """Print the file and the table."""
        if self.table_format == 'simple_rst':
            twriter = SimpleRSTWriter(self.table, **kwargs)
        elif self.table_format == 'grid_rst':
            twriter = GridRSTWriter(self.table, **kwargs)
        else:
            if self.table_format != 'org':
                print(sys.argv[0] +
                      ': error: invalid table format. '
                      'Using org table format instead.', file=sys.stderr)
            twriter = TableWriter(self.table, **kwargs)
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
    """A TableWriter takes care of formatting and printing a GradesTable.
    Write the table using the table format from org-mode.

    The format looks as follows::

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
    def __init__(self, grade_table, min_width=defaults.MIN_CELL_WIDTH,
                 padding_left=defaults.PADDING_LEFT,
                 padding_right=defaults.PADDING_RIGHT,
                 precision=defaults.PRECISION):
        """Initialize the writer. The default parameters for a writer are to
        use a minimum column width of 5, left and right padding of 1 and a
        precision for floating point values of 2.

        """
        self.min_width = min_width
        self.padding_left = padding_left
        self.padding_right = padding_right
        self.precision = precision
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
        self._set_columns_width()
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
        str_hdr = self._div_top()
        str_hdr += self._row_str(col['title'] for col in self.table.columns)

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
        str_hdr += self._row_str(max_row) + self._row_str(weight_row)
        str_hdr += self._div_head()
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
                        str_tbl += self._div_row()
                        break
                prevs = curs
            str_tbl += self._row_str(student[ctitle] for ctitle in col_titles)
        return str_tbl

    def footer_str(self):
        """Generate string for the footer of the table."""
        str_ftr = ''
        if self.table.footers:
            str_ftr += self._div_row()
            col_titles = [col['title'] for col in self.table.columns]
            for footer in self.table.footers:
                str_ftr += self._row_str(footer[ctitle] for ctitle in
                        col_titles)
        return str_ftr + self._div_bottom()

    def _set_columns_width(self):
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

    def _pad_cells(self, row):
        """Return list of padded cells."""
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
        return padded

    def _row_str(self, row):
        """Create a string representation for a row in the table. The columns
        corresponding to evaluations have their numbers justified right.

        """
        padded = self._pad_cells(row)
        return '|' + '|'.join(padded) + '|\n'

    def _div_row(self):
        """Return a division to separate student rows.
        Such a division looks like |-----+------+------|."""
        div = '|' + '+'.join('-' * col['width'] for col in
                             self.table.columns if
                             self.columns_to_print[col['title']])
        return div + '|\n'

    def _div_top(self):
        """Return a division for the top of the table."""
        return ''

    def _div_bottom(self):
        """Return a division for the bottom of the table."""
        return ''

    def _div_head(self):
        """Return a division to separate the header from the rest of the table.
        Such a division looks like |-----+------+------|."""
        return self._div_row()


class SimpleRSTWriter(TableWriter):
    """Write the table using the simple table format from reStructuredText.

    The format looks as follows::

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
    def _row_str(self, row):
        """Create a string representation for a row in the table. The columns
        corresponding to evaluations have their numbers justified right.

        """
        padded = self._pad_cells(row)
        return ' '.join(padded) + '\n'

    def _div_row(self):
        """Return a division that looks like '------- ------ ----- -------'."""
        div = ' '.join('-' * col['width'] for col in
                             self.table.columns if
                             self.columns_to_print[col['title']])
        return div + '\n'

    def _div_top(self):
        """Return a division for the top of the table.
        Such a division looks like '======= ====== ===== ======='."""
        div = ' '.join('=' * col['width'] for col in
                             self.table.columns if
                             self.columns_to_print[col['title']])
        return div + '\n'

    def _div_bottom(self):
        """Return a division for the bottom of the table.
        Such a division looks like '======= ====== ===== ======='."""
        return self._div_top()

    def _div_head(self):
        """Return a division to separate the header from the rest of the table.
        Such a division looks like '======= ====== ===== ======='."""
        return self._div_top()


class GridRSTWriter(TableWriter):
    """Write the table using the grid table format from reStructuredText.

    The format looks as follows::

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
    def _div_row(self):
        """Return a division that looks like '+------+---------+-----+'."""
        div = '+' + '+'.join('-' * col['width'] for col in
                             self.table.columns if
                             self.columns_to_print[col['title']])
        return div + '+\n'

    def _div_top(self):
        """Return a division for the top of the table.
        Such a division looks like '+------+---------+-----+'."""
        return self._div_row()

    def _div_bottom(self):
        """Return a division for the bottom of the table.
        Such a division looks like '+------+---------+-----+'."""
        return self._div_row()

    def _div_head(self):
        """Return a division to separate the header from the rest of the table.
        Such a division looks like '+======+=========+=====+'."""
        div = '+' + '+'.join('=' * col['width'] for col in
                             self.table.columns if
                             self.columns_to_print[col['title']])
        return div + '+\n'

    def rows_str(self, div_on=None):
        """Generate a string containing all the rows for the table.

        Parameters
        ----------
        div_on: tuple
            For reStructuredText tables, this parameter is ignored.

        """
        str_tbl = ''

        if not self.table.students:
            # Empty table, nothing to return.
            return str_tbl

        col_titles = [col['title'] for col in self.table.columns]
        first = True
        for student in self.table.students:
            if not first:
                str_tbl += self._div_row()
            first = False
            str_tbl += self._row_str(student[ctitle] for ctitle in col_titles)
        return str_tbl

    def footer_str(self):
        """Generate string for the footer of the table."""
        str_ftr = ''
        if self.table.footers:
            str_ftr += self._div_row()
            col_titles = [col['title'] for col in self.table.columns]
            for footer in self.table.footers:
                str_ftr += self._row_str(footer[ctitle] for ctitle in
                        col_titles)
                str_ftr += self._div_row()
        return str_ftr
