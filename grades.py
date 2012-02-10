#!/usr/bin/env python

import sys

class GradesFile(object):
    """A GradesFile contains one table of grades. The GradesFile
    object is initialized with a filename and has methods to parse the file. It
    recognizes grade tables and creates new GradesTable objects as needed."""
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
    def __init__(self, data):
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
        for entry in line.strip('|').split('|'):
            yield entry.strip()


    def __to_float(self, val, default=100.):
        try:
            return float(val)
        except ValueError:
            return default

    def compute_cumul(self):
        for student in self.students:
            cumul = sum((student[evalu['name']] * evalu['weight'] /
                         evalu['max_grade']
                         for evalu in self.evals if student[evalu['name']]))
            student['-- Cumul --'] = cumul
        self.columns.append('-- Cumul --')

    def compute_mean(self):
        self.mean = {}
        self.mean[self.columns[0]] = '-- Moyenne --'
        i = 0
        for column in self.columns[1:]:
            if column in self.eval_names:
                evalu = self.evals[i]
                s = sum((student[evalu['name']] for student in self.students
                         if student[evalu['name']]))
                self.mean[column] = (s / len(self.students))
                i += 1
            elif column.startswith('--'):
                s = sum((student['-- Cumul --'] for student in self.students
                         if student['-- Cumul --']))
                self.mean['-- Cumul --'] = s / len(self.students)
            else:
                self.mean[column] = ''


class TableWriter(object):
    def __init__(self, grade_table):
        self.min_width = 5
        self.padding_left = 1
        self.padding_right = 1
        self.table = grade_table

    def printt(self):
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

        str_tbl += self.__div_row()
        if self.table.mean:
            str_tbl += self.__row_str((self.table.mean[cname] for cname in
                self.table.columns))
        print(str_tbl)

    def __set_columns_width(self):
        self.column_widths = []
        for column in self.table.columns:
            col = [column]
            col += [str(student[column]) for student in self.table.students]
            if self.table.mean:
                col += [str(self.table.mean[column])]
            self.column_widths.append(
                self.padding_left + self.padding_right +
                max(len(row) for row in col))

    def __row_str(self, row):
        """Create a string representation for a row in the table. The columns
        corresponding to evaluations have their numbers justified right."""
        padded = []
        for i, rowelmt in enumerate(row):
            width = self.column_widths[i]
            if (self.table.columns[i] in self.table.eval_names
                    and not isinstance(rowelmt, str)):
                padded.append(
                        ' ' * (width - len(str(rowelmt)) - self.padding_right)
                        + str(rowelmt) + ' ' * self.padding_right)
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
| Suzanne Tremblay  | 302   | 67     | 78     |         |           |"""
    grades_tbl = GradesTable(test_data.split('\n'))
    writer = TableWriter(grades_tbl)
    writer.printt()
    grades_tbl.compute_cumul()
    grades_tbl.compute_mean()
    writer.printt()


