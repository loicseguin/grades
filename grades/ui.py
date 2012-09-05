#-*- coding: utf-8 -*-
"""
ui
==

Module for parsing command line arguments and running the appropriate command.

"""


from __future__ import print_function


__author__ = "Loïc Séguin-C. <loicseguin@gmail.com>"
__license__ = "BSD"


import argparse
import os
import sys
from collections import defaultdict
from . import __version__
from . import defaults
from . import writers
from .gradestable import GradesTable

try:
    if raw_input:
        input = raw_input
except NameError:
    pass


def _calc_weights(nbevals):
    """Calculate the weight of each evaluation in a scheme with nbeval
    evaluations. In general, there are one final exam, one midterm and nbeval -
    2 small tests."""
    if nbevals < 1:
        print(sys.argv[0] +
            ' init: error: argument -n/--nbevals: must be greater than 0',
            file=sys.stderr)
        sys.exit(1)
    if nbevals == 1:
        midterm_weight = 0.
        final_weight = 100.
        test_weight = 0.
    elif nbevals == 2:
        midterm_weight = 40.
        final_weight = 60.
        test_weight = 0.
    else:
        midterm_weight = 30.
        final_weight = 40.
        test_weight = 30. / (nbevals - 2)
    return final_weight, midterm_weight, test_weight


class Runner:
    """Set the options and execute the chosen subcommands."""

    def __init__(self):
        """Define default values."""
        self.input_filename = defaults.INPUT_FILENAME
        self.output_filename = defaults.OUTPUT_FILENAME
        self.ignore_char = defaults.IGNORE_CHAR
        self.calc_char = defaults.CALC_CHAR
        self.precision = defaults.PRECISION
        self.padding_left = defaults.PADDING_LEFT
        self.padding_right = defaults.PADDING_RIGHT
        self.min_cell_width = defaults.MIN_CELL_WIDTH
        self.columns = defaults.COLUMNS

    def read_config(self):
        pass

    def print_table(self, args):
        """Print the table using options specified in command line arguments
        ``args``."""
        try:
            args.filename = open(args.filename)
        except IOError as e:
            print(e, file=sys.stderr)
            #sys.exit(1)
            return

        gfile = writers.GradesFile(args.filename, self.ignore_char)
        if self.calc_char != self.ignore_char:
            gfile.table.calc_char = self.calc_char
        if args.columns:
            args.columns = args.columns.split(',')
        if args.divs:
            args.divs = args.divs.split(',')
        if args.groups:
            args.groups = args.groups.split(',')
        if args.cumul:
            gfile.table.compute_cumul()
            if args.columns:
                args.columns.append(self.calc_char +
                                    'Cumul' + self.calc_char)
        if args.assignments:
            gfile.table.compute_assignment_mean()
            if args.columns:
                args.columns.append(self.calc_char + 'Assignments' +
                        self.calc_char)
        if args.students:
            gfile.table = gfile.table.select(args.students)
        if args.mean:
            gfile.table.compute_mean()
        if args.groups:
            for group in args.groups:
                gfile.table.compute_grouped_mean(group_by=group)
        if args.table_format:
            gfile.table_format = args.table_format
        #if args.output:
            #output = arg.output
        #else:
        output = sys.stdout
        gfile.print_file(div_on=args.divs, columns=args.columns,
                         tableonly=args.tableonly, file=output,
                         min_width=self.min_cell_width,
                         padding_left=self.padding_left,
                         padding_right=self.padding_right,
                         precision=self.precision)

    def init(self, args):
        """Initialize a file containing a grades table.

        This function creates a set of evaluations (7 by default) and writes
        them to a grades file. The user can specify the number of evaluations
        using the -n/--nbevals command line argument.
        
        There is always a final exam. If more than one evaluation is requested,
        there will be a midterm. If more than two evaluations are requested,
        there will be tests. The weights are assigned by the ``_calc_weights``
        function. For more complicated evaluation grids, the user should create
        the file by hand.

        """
        if os.path.exists(args.filename):
            print('Do you want to overwrite the file ' + args.filename +
                  '? [y/N]  ', end='')
            answer = input()
            if not answer.lower() in ('y', 'yes'):
                return
        args.filename = open(args.filename, 'w')
        table = GradesTable(calc_char=self.calc_char)
        table.columns = self.columns
        if args.nbevals:
            for col in table.columns[:]:
                if col['evalu']:
                    table.columns.remove(col)

            final_w, midterm_w, test_w = _calc_weights(args.nbevals)

            for i in range((args.nbevals - 1) // 2):
                table.columns.append(
                    {'title': 'Test ' + str(i + 1), 'is_num': True, 'width': 0,
                     'evalu': {'max_grade': 20., 'weight': test_w}})
            if midterm_w > 0:
                table.columns.append(
                    {'title': 'Midterm', 'is_num': True, 'width': 0,
                     'evalu': {'max_grade': 100., 'weight': midterm_w}})
            for i in range((args.nbevals - 1) // 2, args.nbevals - 2):
                table.columns.append(
                    {'title': 'Test ' + str(i + 1), 'is_num': True, 'width': 0,
                     'evalu': {'max_grade': 20., 'weight': test_w}})
            table.columns.append(
                {'title': 'Final', 'is_num': True, 'width': 0,
                 'evalu': {'max_grade': 100., 'weight': final_w}})
        table_writer = writers.TableWriter
        if args.table_format:
            if args.table_format == 'simple_rst':
                table_writer = writers.SimpleRSTWriter
            elif args.table_format == 'grid_rst':
                table_writer = writers.GridRSTWriter
        table_writer = table_writer(table, min_width=self.min_cell_width,
                padding_left=self.padding_left,
                padding_right=self.padding_right, precision=self.precision)
        table_writer.write(file=args.filename)
        args.filename.close()

    def add_column(self, args):
        gfile = writers.GradesFile(args.filename, self.ignore_char)
        col_name = input('Enter column name: ')
        if col_name in [col['title'] for col in gfile.table.columns]:
            print(sys.argv[0] +
                ' add column: error: column name already in table',
                file=sys.stderr)
            sys.exit(1)
        position = input('Enter column number [' +
                         str(len(gfile.table.columns)) + ']: ')
        if position == '':
            position = len(gfile.table.columns)
        else:
            position = int(position)
            if position < 0 or position > len(gfile.table.columns):
                print(sys.argv[0] +
                    ' add column: error: invalid column number',
                    file=sys.stderr)
                sys.exit(1)

        is_eval = input('Is this column an evaluation? [Y/n] ')
        if is_eval.lower() not in ('n', 'no'):
            max_grade = float(
                    input('What is the maximum grade for this evaluation? '))
            weight = float(
                    input('What is the weight for this evaluation? '))
            gfile.table.columns.insert(position,
                {'title': col_name, 'is_num': True, 'width': 0,
                 'evalu': {'max_grade': max_grade, 'weight': weight}})
        else:
            gfile.table.columns.insert(position,
                {'title': col_name, 'is_num': False, 'width': 0,
                 'evalu': None})

        ofile = open(args.filename, 'w')
        gfile.print_file(file=ofile,
                         min_width=self.min_cell_width,
                         padding_left=self.padding_left,
                         padding_right=self.padding_right,
                         precision=self.precision)
        ofile.close()

    def add_student(self, args):
        """Add a student to the table and update the file.

        Let the user interactively specify the entry for each non-evaluation
        column. Inserting the student's grades should be done with the update
        command.

        """
        gfile = writers.GradesFile(args.filename, self.ignore_char)

        student = defaultdict(str)
        for col in gfile.table.columns:
            if not col['evalu']:
                student[col['title']] = input("Enter student's " +
                                              col['title'] + ': ')
        gfile.table.students.append(student)

        ofile = open(args.filename, 'w')
        gfile.print_file(file=ofile,
                         min_width=self.min_cell_width,
                         padding_left=self.padding_left,
                         padding_right=self.padding_right,
                         precision=self.precision)
        ofile.close()

    def run(self, argv=sys.argv[1:]):
        """Make the runner run.

        Arguments from ``sys.argv`` are processed and are
        used to print the requested output.

        """
        self.read_config()

        clparser = argparse.ArgumentParser(
            description='A grade management tool with plain text tables storage.')
        clparser.add_argument('-v', '--version', action='version',
                version='%(prog)s ' + __version__)

        subparsers = clparser.add_subparsers()
        printparser = subparsers.add_parser('print', help='print the grades table')
        printparser.add_argument('-m', '--mean', action='store_true',
                help='print the mean for each evaluation')
        printparser.add_argument('-c', '--cumul', action='store_true',
                help='print the cumulative grade for each student')
        printparser.add_argument('-a', '--assignments', action='store_true',
                help='print the assignment grade for each student')
        printparser.add_argument('-t', '--tableonly', action='store_true',
                help='print only the table')
        printparser.add_argument('-d', '--divs',
                help='draw a horizontal division between students in different '
                     + 'DIVS; DIVS is a comma separated list of column titles')
        printparser.add_argument('-C', '--columns',
                help='comma separated list of columns to print (default is to print'
                     + ' all columns)')
        printparser.add_argument('-g', '--grouped', dest='groups',
                help='print the mean for each GROUP for each evaluation; '
                     + 'GROUP must be a column title')
        printparser.add_argument('-f', '--format', dest='table_format',
                help='table format for printing (org, simple_rst, grid_rst)',
                choices=['org', 'simple_rst', 'grid_rst'])
        printparser.add_argument('-s', '--students',
                help='expression specifying students to print')
        #printparser.add_argument('-o', '--output', type=argparse.FileType('w'),
                #help='write output in file name')
        printparser.add_argument('filename',
                help='grades file to read and parse', nargs='?',
                default=self.input_filename)
        printparser.set_defaults(func=self.print_table)

        initparser = subparsers.add_parser('init',
                help='initialize a new grades file')
        initparser.add_argument('filename', nargs='?',
                help='file where grades table skeleton will be written',
                default=self.output_filename)
        initparser.add_argument('-f', '--format', dest='table_format',
                help='table format for printing (org, simple_rst, grid_rst)',
                choices=['org', 'simple_rst', 'grid_rst'])
        initparser.add_argument('-n', '--nbevals', type=int,
                help='number of evaluations in table')
        initparser.set_defaults(func=self.init)

        addparser = subparsers.add_parser('add',
                help='add a new student or evaluation')
        sub_add = addparser.add_subparsers()
        add_column_parser = sub_add.add_parser('column',
                help='add a new column')
        add_column_parser.add_argument('filename',
                help='grades file to read and parse', nargs='?',
                default=self.input_filename)
        add_column_parser.set_defaults(func=self.add_column)

        add_student_parser = sub_add.add_parser('student',
                help='add a new student')
        add_student_parser.add_argument('filename',
                help='grades file to read and parse', nargs='?',
                default=self.input_filename)
        add_student_parser.set_defaults(func=self.add_student)

        args = clparser.parse_args(argv)
        args.func(args)
