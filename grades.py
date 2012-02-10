#!/usr/bin/env python

import fileinput

class GradesTable(object):
    def __init__(self, data=None):
        self.evals = []
        self.students = []
        if data:
            # The first three lines contain information about the evaluations.
            eval_names = [entry for entry in self._parse_line(data[0])
                          if not entry.startswith('-')][1:]
            eval_max = [_to_float(entry) for entry in
                        self._parse_line(data[1])][1:len(eval_names) + 1]
            eval_weight = [_to_float(entry, 0.) for entry in
                           self._parse_line(data[2])][1:len(eval_names) + 1]
            self.evals = list(zip(eval_names, eval_max, eval_weight))

            # The next lines contain student records.
            for line in data[3:]:
                if line.startswith('|-'):
                    continue
                self.students.append([_to_float(entry, entry) for entry in
                                      self._parse_line(line)])

    def __str__(self):
        return str(self.evals) + '\n' + str(self.students)

    def _parse_line(self, line):
        for entry in line.strip('|').split('|'):
            yield entry.strip()

    def compute_cumul(self):
        for student in self.students:
            cumul = sum((student[i + 1] * evalu[2] / evalu[1] for i, evalu in
                         enumerate(self.evals) if student[i+1]))
            student.append(cumul)
        self.evals.append(('--Cumul--', 100., ''))


def _to_float(val, default=100.):
    try:
        return float(val)
    except ValueError:
        return default


if __name__ == '__main__':
    test_data = """| Nom    | Test 1 | Test 2 | Midterm | --Cumul-- |
|                      | 70     | 100    |     |           |
|                      | 10     | 10     | 30      |           |
|----------------------+--------+--------+---------+-----------|
| Bob Arthur           | 23     | 45     |         |           |
| Suzanne Tremblay     | 67     | 78     |         |           |"""
    grades_tbl = GradesTable(test_data.split('\n'))
    print(grades_tbl)
    grades_tbl.compute_cumul()
    for student in grades_tbl.students:
        print(student)


