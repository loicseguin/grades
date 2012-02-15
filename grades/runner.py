#-*- coding: utf-8 -*-
"""
runner
======

Module for parsing command line arguments and running the appropriate command.

"""


__author__ = "Loïc Séguin-C. <loicseguin@gmail.com>"
__license__ = "BSD"
__version__ = "0.1"


import argparse
from .classes import GradesFile


def run():
    """Make the runner run.

    Arguments from ``sys.argv`` are processed and are
    used to print the requested output.

    """
    clparser = argparse.ArgumentParser(
        description='A grade management tool with plain text tables storage.')
    clparser.add_argument('-v', '--version', action='version',
            version='%(prog)s 0.1')
    clparser.add_argument('-m', '--mean', action='store_true',
            help='print the mean for each evaluation')
    clparser.add_argument('-c', '--cumul', action='store_true',
            help='print the cumulative grade for each student')
    clparser.add_argument('-t', '--tableonly', action='store_true',
            help='print only the table')
    clparser.add_argument('-d', '--div', nargs='*',
            help='draw a horizontal division between students in different '
                 + 'DIV; DIV must be the name of one of the columns in '
                 + 'the table')
    clparser.add_argument('-C', '--columns', nargs='*',
            help='list of columns to print (default is to print all columns)')
    clparser.add_argument('-g', '--grouped', dest='group',
            help='print the mean for each GROUP for each evaluation; '
                 + 'GROUP must be the name of one of the columns in the '
                 + 'table')
    clparser.add_argument('filename', type=argparse.FileType('r'),
            help='grades file to read and parse')
    args = clparser.parse_args()

    gfile = GradesFile(args.filename)
    if args.cumul:
        gfile.table.compute_cumul()
        if args.columns:
            args.columns.append('-- Cumul --')
    if args.mean:
        gfile.table.compute_mean()
    if args.group:
        gfile.table.compute_grouped_mean(group_by=args.group)
    gfile.print_file(div_on=args.div, columns=args.columns,
                     tableonly=args.tableonly)


if __name__ == '__main__':
    run()
