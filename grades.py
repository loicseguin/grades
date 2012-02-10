#!/usr/bin/env python

import sys

class GradesFile(object):
    """A GradesFile contains one table of grades. The GradesFile
    object is initialized with a filename. It takes care of safeguarding the
    content of the file before and after the table."""
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
            sys.stderr.write('Error: Malformed table in file ' + filename)
            sys.exit(1)
        self.table = GradesTable(tablelines)


class GradesTable(object):
    """A GradesTable contains all the data in a table and can perform
    calculations and modify the table to include the results."""
    def __init__(self, data):
        """To instanciate a new GradesTable, one must provide data in the form
        of a list of lines."""
        object.__init__(self)
        self.columns = []
        self.evals = []
        self.students = []
        self.mean = {}
        # The first three lines contain information about the evaluations.
        self.columns = [entry for entry in self.__parse_line(data[0])
                        if not entry.startswith('-')]
        # Try to determine which column is an evaluation.  Evaluations are
        # stored as dictionaries with keys name, max_grade and weight.
        eval_colnum = [i for i, cname in enumerate(self.columns) if
                       cname.upper().startswith(('TEST', 'EXAM', 'MIDTERM',
                       'QUIZ', 'FINAL'))]
        eval_names = [self.columns[i] for i in eval_colnum]
        eval_max = [self.__to_float(entry) for i, entry in
                    enumerate(self.__parse_line(data[1]))
                    if i in eval_colnum]
        eval_weight = [self.__to_float(entry, 0.) for i, entry in
                       enumerate(self.__parse_line(data[2]))
                       if i in eval_colnum]
        self.evals = [dict((('name', name), ('max_grade', maxg),
                           ('weight', weight))) for name, maxg, weight
                      in zip(eval_names, eval_max, eval_weight)]
        self.eval_names = eval_names

        # The next lines contain student records. Students are stored as a
        # list of dictionaries keyed by column name.
        for line in data[3:]:
            if line.startswith('|-'):
                # Separator line in the table.
                continue
            keyval = []
            for i, entry in enumerate(self.__parse_line(line)):
                if i >= len(self.columns) or entry.startswith('--'):
                    break
                if self.columns[i] in self.eval_names:
                    keyval.append((self.columns[i],
                        self.__to_float(entry, entry)))
                else:
                    keyval.append((self.columns[i], entry))

            if keyval:
                self.students.append(dict(keyval))


    def __parse_line(self, line):
        """Read a line and split it into tokens. This is a generator that
        yields the tokens. A typical line looks like
            | Some Name | Extra info | 78 | 89 | 90|
        and gets parsed into the following list:
            ['Some Name', 'Extra info', 78, 89, 90]."""
        for entry in line.strip('|').split('|'):
            yield entry.strip()


    def __to_float(self, val, default=100.):
        """Convert string val into float with fallback value default."""
        try:
            return float(val)
        except ValueError:
            return default

    def compute_cumul(self):
        """Calculate the weighted mean for each student and add that result
        in a new column at the end of the table."""
        for student in self.students:
            cumul = sum((student[evalu['name']] * evalu['weight'] /
                         evalu['max_grade']
                         for evalu in self.evals if student[evalu['name']]))
            student['-- Cumul --'] = cumul
        self.columns.append('-- Cumul --')

    def compute_mean(self):
        """Calculate the class mean for each evaluation and add the results to
        a new row at the bottom of the table. Blanks in the table are not taken
        into account, i.e., a blank does not count as a zero."""
        self.mean = {}
        self.mean[self.columns[0]] = '-- Moyenne --'
        for column in self.columns[1:]:
            self.mean[column] = ''
            if column in self.eval_names or column.startswith('--'):
                nb_students = sum((1 for student in self.students if
                                  student[column]))
                s = sum((student[column] for student in self.students
                         if student[column]))
                if nb_students:
                    self.mean[column] = s / nb_students


class TableWriter(object):
    def __init__(self, grade_table):
        self.min_width = 5
        self.padding_left = 1
        self.padding_right = 1
        self.table = grade_table
        self.num_columns = list(grade_table.eval_names)
        self.num_rows = list(grade_table.students)
        self.precision = 2

    def printt(self):
        if ('-- Cumul --' in self.table.columns and not '-- Cumul --' in
            self.num_columns):
            self.num_columns += ['-- Cumul --']
        if (self.table.mean and not self.table.mean in self.num_rows):
            self.num_rows += [self.table.mean]
        self.__set_columns_width()
        # Header row.
        str_tbl = self.__row_str(self.table.columns)

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
        str_tbl += self.__row_str(max_row) + self.__row_str(weight_row)
        str_tbl += self.__div_row()

        for student in self.table.students:
            str_tbl += self.__row_str(
                    (student[cname] for cname in self.table.columns))

        if self.table.mean:
            str_tbl += self.__div_row()
            str_tbl += self.__row_str((self.table.mean[cname] for cname in
                self.table.columns))
        print(str_tbl)

    def __set_columns_width(self):
        self.column_widths = []
        for column in self.table.columns:
            col = [column]
            if column in self.num_columns:
                for student in self.num_rows:
                    if not isinstance(student[column], str):
                        col += [format(student[column], '.%df'%self.precision)]
                    else:
                        col += [student[column]]
            else:
                col += [str(student[column]) for student in self.table.students]
            self.column_widths.append(
                self.padding_left + self.padding_right +
                max(len(row) for row in col))

    def __row_str(self, row):
        """Create a string representation for a row in the table. The columns
        corresponding to evaluations have their numbers justified right."""
        padded = []
        for i, rowelmt in enumerate(row):
            width = self.column_widths[i]
            if (self.table.columns[i] in self.num_columns
                and not isinstance(rowelmt, str)):
                str_elmt = format(rowelmt, '.%df' % self.precision)
                padded.append(
                        ' ' * (width - len(str_elmt) - self.padding_right)
                        + str_elmt + ' ' * self.padding_right)
            else:
                padded.append(' ' * self.padding_left + str(rowelmt)
                        + ' ' * (width - len(str(rowelmt)) - self.padding_left))
        return '|' + '|'.join(padded) + '|\n'

    def __div_row(self):
        div = '|' + '+'.join(('-' * width for width in self.column_widths))
        return div + '|\n'


if __name__ == '__main__':
    test_data = """| Nom    |Group | Test 1 | Test 2 | Midterm | --Cumul-- |
|                   |   | 70     | 100    |     |           |
|                   |   | 10     | 10     | 30      |           |
|----------------------+--------+--------+---------+-----------|
| Bob Arthur        | 301   | 23     | 45     |         |           |
| Suzanne Tremblay  | 302   | 67     | 78     |         |           |
| -- Some stuff--   | This row | should | be |    | ignored |"""
    grades_tbl = GradesTable(test_data.split('\n'))
    writer = TableWriter(grades_tbl)
    writer.printt()
    grades_tbl.compute_cumul()
    grades_tbl.compute_mean()
    writer.printt()


