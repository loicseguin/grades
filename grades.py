#!/usr/bin/env python

class GradesTable(object):
    def __init__(self, data=None):
        self.columns = []
        self.evals = []
        self.students = []
        self.mean = {}
        self.min_width = 5
        self.padding_left = 1
        self.padding_right = 1
        if data:
            # The first three lines contain information about the evaluations.
            self.columns = [entry for entry in self._parse_line(data[0])
                            if not entry.startswith('-')]
            # Try to determine which column is an evaluation.
            eval_colnum = [i for i, cname in enumerate(self.columns) if
                           cname.upper().startswith(('TEST', 'EXAM', 'MIDTERM',
                           'QUIZ', 'FINAL'))]
            eval_names = [self.columns[i] for i in eval_colnum]
            eval_max = [_to_float(entry) for i, entry in
                        enumerate(self._parse_line(data[1]))
                        if i in eval_colnum]
            eval_weight = [_to_float(entry, 0.) for i, entry in
                           enumerate(self._parse_line(data[2]))
                           if i in eval_colnum]
            self.evals = list(zip(eval_names, eval_colnum, eval_max,
                                  eval_weight))
            self.eval_names = eval_names

            # The next lines contain student records. Students are stored as a
            # list of dictionaries keyed by column name.
            for line in data[3:]:
                if line.startswith('|-'):
                    continue
                self.students.append(
                        dict((self.columns[i], _to_float(entry, entry)) for
                            i, entry in enumerate(self._parse_line(line))
                            if i < len(self.columns)))

    def __str__(self):
        self._set_columns_width()
        # Header row.
        str_tbl = self._row_str(self.columns)

        # Max and weight rows. These are filled only for evaluation columns.
        i = 0
        max_row = []
        weight_row = []
        for column in self.columns:
            if column in self.eval_names:
                max_row.append(self.evals[i][2])
                weight_row.append(self.evals[i][3])
                i += 1
            else:
                max_row.append('')
                weight_row.append('')
        str_tbl += self._row_str(max_row) + self._row_str(weight_row)
        str_tbl += self._div_row()

        for student in self.students:
            str_tbl += self._row_str((student[cname] for cname in self.columns))

        str_tbl += self._div_row()
        if self.mean:
            str_tbl += self._row_str((self.mean[cname] for cname in
                self.columns))
        return str_tbl

    def _parse_line(self, line):
        for entry in line.strip('|').split('|'):
            yield entry.strip()

    def _set_columns_width(self):
        self.column_widths = []
        for i, column in enumerate(self.columns):
            self.column_widths.append(
                self.padding_left + self.padding_right +
                max([self.min_width, len(column)] +
                    [len(str(student[column])) for student in self.students]))

    def _row_str(self, row):
        padded = (' ' * self.padding_left + str(rowelmt) +
                  ' ' * (width - len(str(rowelmt)) - self.padding_left -
                      self.padding_right) + ' ' * self.padding_right
                  for rowelmt, width in zip(row, self.column_widths))
        return '|' + '|'.join(padded) + '|\n'

    def _div_row(self):
        div = '|' + '+'.join(('-' * width for width in self.column_widths))
        return div + '|\n'

    def compute_cumul(self):
        for student in self.students:
            cumul = sum((student[evalu[0]] * evalu[3] / evalu[2] for evalu in
                         self.evals if student[evalu[0]]))
            student['--Cumul--'] = cumul
        self.columns.append('--Cumul--')

    def compute_mean(self):
        self.mean = {}
        self.mean[self.columns[0]] = 'Mean'
        i = 0
        for column in self.columns[1:]:
            if column in self.eval_names:
                evalu = self.evals[i]
                s = sum((student[evalu[0]] for student in self.students
                         if student[evalu[0]]))
                self.mean[column] = (s / len(self.students))
                i += 1
            elif column.startswith('--'):
                s = sum((student['--Cumul--'] for student in self.students
                         if student['--Cumul--']))
                self.mean['--Cumul--'] = s / len(self.students)
            else:
                self.mean[column] = ''


def _to_float(val, default=100.):
    try:
        return float(val)
    except ValueError:
        return default


if __name__ == '__main__':
    test_data = """| Nom    |Group | Test 1 | Test 2 | Midterm | --Cumul-- |
|                   |   | 70     | 100    |     |           |
|                   |   | 10     | 10     | 30      |           |
|----------------------+--------+--------+---------+-----------|
| Bob Arthur        | 301   | 23     | 45     |         |           |
| Suzanne Tremblay  | 302   | 67     | 78     |         |           |"""
    grades_tbl = GradesTable(test_data.split('\n'))
    print(grades_tbl)
    grades_tbl.compute_cumul()
    grades_tbl.compute_mean()
    print(grades_tbl)


