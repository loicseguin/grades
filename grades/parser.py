#-*- coding: utf-8 -*-
"""parser

This module provides a function that can parse a student grades table.
The table has the following form:

+-----------+----------+---------+---------+
| Header 1  | Header 2 | Eval 1  | Eval 2  |
|           |          | max1    | max2    |
|           |          | weight1 | weight2 |
+-----------+----------+---------+---------+
| A Name    | Info     | 45      |  56     |
| An Other  | More Inf | 57      | 43      |
+-----------+----------+---------+---------+

There is some flexibility in the layout for the table. It can use '=' instead
of hyphens and '+' can be substituted by pipes or hyphens. Moreover, the top
and bottom rows are optional.

Evaluations should have a name that starts with 'Test', 'Exam', 'Midterm',
'Eval' or 'Quiz' in order to be recognized as evaluations. Each evaluation has
a maximum grade and a weight towards the final grade. If a maximum is not
given, a value of 100 is assumed. If a weight is not given, a value of 0 is
assumed.

"""


__author__ = "Loïc Séguin-C. <loicseguin@gmail.com>"
__license__ = "BSD"


from collections import defaultdict
import re
from .gradestable import GradesTable


ROW_SEPS = ('--', '|-', '+-', '|=', '+=')
EVAL_NAMES = ('TEST', 'EXAM', 'MIDTERM', 'QUIZ', 'FINAL', 'EVAL')


def _to_float(val, default=100.):
    """Convert string val into float with fallback value default."""
    try:
        return float(val)
    except ValueError:
        return default


class TableMarkupError(Exception):
    """Exception raised when the table data contains a markup error."""


def parse_table(data, ignore_char='*'):
    """Parse lines into table row.

    Input
    -----
    data: iterable
       A list of all the rows in the table.

    ignore_char: string
       Character (or string) that indicates a row or column that should be
       ignored. A row or column header that starts with this character will be
       ignored.

    Output
    ------
    table: GradesTable

    """
    # The first three rows contains columns headers. If a column
    # corresponds to an evaluation, the first row is the title, the second
    # row is the maximum grade and the third row is the weight.
    # Otherwise, the first row is the title and the two other rows are
    # ignored.
    entry_sep = re.compile('\s*\|\s*')

    header_rows = []
    for end_headers, row in enumerate(data):
        if row.startswith(ROW_SEPS):
            if end_headers == 0:
                continue
            else:
                break
        header_rows.append(entry_sep.split(row)[1:-1])

    if len(header_rows) != 3:
        raise TableMarkupError("There should be 3 header rows")

    table = GradesTable()
    table.calc_char = ignore_char
    headers = zip(*header_rows)
    for name, max_grade, weight in headers:
        if name.startswith(ignore_char):  # Reserved for calculated columns
            continue
        if name.upper().startswith(EVAL_NAMES):
            evalu = {'max_grade': _to_float(max_grade, 100.),
                     'weight': _to_float(weight, 0.)}
            table.columns.append(
                    {'title': name, 'is_num': True, 'evalu': evalu,
                     'width': 0, 'to_print': True})
        else:
            table.columns.append(
                    {'title': name, 'is_num': False, 'evalu': None,
                     'width': 0, 'to_print': True})

    # The next rows contain student records. Students are stored as a
    # list of defaultdict keyed by column title with a str default factory.
    for row in data[end_headers + 1:]:
        if row.startswith(ROW_SEPS):  # Separator row in the table
            continue
        student = defaultdict(str)
        for i, entry in enumerate(entry_sep.split(row)[1:-1]):
            if i >= len(table.columns) or entry.startswith(ignore_char):
                break
            if table.columns[i]['is_num']:
                student.update(
                    [(table.columns[i]['title'], _to_float(entry, entry))])
            else:
                # This is necessary to avoid casting groups numbers into
                # floats, which looks weird when printed.
                student.update([(table.columns[i]['title'], entry)])
        if student:
            table.students.append(student)

    return table
