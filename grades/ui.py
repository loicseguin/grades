#-*- coding: utf-8 -*-
"""
ui
==

Module for parsing command line arguments and running the appropriate command.

"""


__author__ = "Loïc Séguin-C. <loicseguin@gmail.com>"
__license__ = "BSD"


import argparse
import sys
from . import __version__
from .writer import GradesFile


class Runner:
    def __init__(self):
        """Define default values."""
        self.input_filename = 'Grades.txt'
        self.ignore_char = '*'
        self.calc_char = '*'
        self.precision = 2
        self.padding_left = 1
        self.padding_right = 1
        self.min_cell_width = 5

    def read_config(self):
        pass

    def print_table(self, args):
        if args.filename:
            gfile = GradesFile(args.filename, self.ignore_char)
        else:
            gfile = GradesFile(self.input_filename, self.ignore_char)
        if args.columns:
            args.columns = args.columns.split(',')
        if args.divs:
            args.divs = args.divs.split(',')
        if args.groups:
            args.groups = args.groups.split(',')
        if args.cumul:
            gfile.table.compute_cumul()
            if args.columns:
                args.columns.append(self.ignore_char +
                                    'Cumul' + self.ignore_char)
        if args.students:
            gfile.table = gfile.table.select(args.students)
        if args.mean:
            gfile.table.compute_mean()
        if args.groups:
            for group in args.groups:
                gfile.table.compute_grouped_mean(group_by=group)
        if args.output:
            output = arg.output
        else:
            output = sys.stdout
        gfile.print_file(div_on=args.divs, columns=args.columns,
                         tableonly=args.tableonly, file=output,
                         min_width=self.min_cell_width,
                         padding_left=self.padding_left,
                         padding_right=self.padding_right,
                         precision=self.precision)

    def init(self, args):
        pass

    def add(self, args):
        pass

    def run(self, argv=sys.argv[1:]):
        """Make the runner run.

        Arguments from ``sys.argv`` are processed and are
        used to print the requested output.

        """
        clparser = argparse.ArgumentParser(
            description='A grade management tool with plain text tables storage.')
        clparser.add_argument('-v', '--version', action='version',
                version='%(prog)s ' + __version__)

        subparsers = clparser.add_subparsers()
        printparser = subparsers.add_parser('print', help='print the grades table')

        initparser = subparsers.add_parser('init', 
                                           help='initialize a new grades file')
        initparser.set_defaults(func=self.init)
        addparser = subparsers.add_parser('add',
                                          help='add a new student or evaluation')
        addparser.set_defaults(func=self.add)

        printparser.add_argument('-m', '--mean', action='store_true',
                help='print the mean for each evaluation')
        printparser.add_argument('-c', '--cumul', action='store_true',
                help='print the cumulative grade for each student')
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
        printparser.add_argument('-s', '--students',
                help='expression specifying students to print')
        printparser.add_argument('-o', '--output', type=argparse.FileType('w'),
                help='write output in file name')
        printparser.add_argument('filename', type=argparse.FileType('r'),
                help='grades file to read and parse')
        printparser.set_defaults(func=self.print_table)

        args = clparser.parse_args(argv)
        args.func(args)


if __name__ == '__main__':
    runner = Runner()
    runner.run()
