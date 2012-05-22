#-*- coding: utf-8 -*-
"""gradestable

This module provides a class that contains grades for students.

The methods offered by GradesTable can compute the mean for each evaluation,
the final grade of each student as well as the class mean for each evaluation.
The class mean uses one of the columns to group the students.

"""


__author__ = "Loïc Séguin-C. <loicseguin@gmail.com>"
__license__ = "BSD"


from collections import defaultdict
from copy import deepcopy
import re
from . import defaults


class GradesTable:
    """A GradesTable contains all the data in a table and can perform
    calculations and modify the table to include the results.

    """
    def __init__(self, data=None, calc_char=defaults.CALC_CHAR):
        """Instanciate a new GradesTable.

        Input
        -----
        data: GradesTable
           A GradesTable to copy.

        """
        self.columns = []
        self.students = []
        self.footers = []
        self.calc_char = calc_char

        if isinstance(data, GradesTable):
            self.columns = deepcopy(data.columns)
            self.students = deepcopy(data.students)
            self.footers = deepcopy(data.footers)

    def __getitem__(self, aslice):
        """A table can be indexed or sliced. The slicing mechanism work on rows
        of students. A new table is created that contains only the students
        included in ``aslice``. All the columns and their headers are copied
        into the new table.

        """
        atable = GradesTable()
        atable.columns = deepcopy(self.columns)
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
        """Simple string representation for the table."""
        return '\n'.join((str(self.columns),
                          str(self.students),
                          str(self.footers)))

    def __eq__(self, table):
        """Test for equality."""
        if (self.columns == table.columns and
            self.students == table.students and
            self.footers == table.footers and
            self.calc_char == table.calc_char):
            return True
        return False

    def __decorate(self, name):
        """Concatenate name with the calc_char string."""
        return self.calc_char + name + self.calc_char

    def compute_cumul(self):
        """Calculate the weighted mean for each student and add that result
        in a new column at the end of the table.

        """
        cumul = self.__decorate('Cumul')
        supp = None
        for column in self.columns:
            if column['title'].upper().startswith('SUPP'):
                supp = column
                break
        for student in self.students:
            student[cumul] = 0.
            tot_weight = 0.
            for column in self.columns:
                if (column['evalu']
                    and isinstance(student[column['title']], (float, int))
                    and column != supp):
                    student[cumul] += (student[column['title']] *
                        column['evalu']['weight'] /
                        column['evalu']['max_grade'])
                    tot_weight += column['evalu']['weight']
            student[cumul] /= (tot_weight or 1.) * 0.01
        self.columns.append({'title': cumul, 'is_num': True,
                             'evalu': None, 'width': 0})
        if supp:
            adj = self.__decorate('Adjustment')
            self.columns.append({'title': adj,
                                 'is_num': True,
                                 'evalu': None, 'width': 0})
            after_supp = self.__decorate('Cumul with supp')
            self.columns.append({'title': after_supp,
                                 'is_num': True,
                                 'evalu': None, 'width': 0})
            for student in self.students:
                if isinstance(student[supp['title']], (float, int)):
                    if student[supp['title']] < 60:
                        student[adj] = 0.
                        student[after_supp] = student[cumul]
                    else:
                        student[adj] = 60. - student[cumul]
                        student[after_supp] = 60.

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
        mean[self.columns[0]['title']] = self.__decorate(row_name)
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
