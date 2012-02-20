#-*- coding: utf-8 -*-
"""
runner
======

Module for parsing command line arguments and running the appropriate command.

"""


__author__ = "Loïc Séguin-C. <loicseguin@gmail.com>"
__license__ = "BSD"


import argparse
import sys
from . import __version__
from .classes import GradesFile


def run(argv=sys.argv[1:]):
    """Make the runner run.

    Arguments from ``sys.argv`` are processed and are
    used to print the requested output.

    """
    clparser = argparse.ArgumentParser(
        description='A grade management tool with plain text tables storage.')
    clparser.add_argument('-v', '--version', action='version',
            version='%(prog)s ' + __version__)
    clparser.add_argument('-m', '--mean', action='store_true',
            help='print the mean for each evaluation')
    clparser.add_argument('-c', '--cumul', action='store_true',
            help='print the cumulative grade for each student')
    clparser.add_argument('-t', '--tableonly', action='store_true',
            help='print only the table')
    clparser.add_argument('-d', '--divs',
            help='draw a horizontal division between students in different '
                 + 'DIVS; DIVS is a comma separated list of column titles')
    clparser.add_argument('-C', '--columns',
            help='comma separated list of columns to print (default is to print'
                 + ' all columns)')
    clparser.add_argument('-g', '--grouped', dest='group',
            help='print the mean for each GROUP for each evaluation; '
                 + 'GROUP must be a column title')
    clparser.add_argument('-s', '--students',
            help='expression specifying students to print')
    clparser.add_argument('filename', type=argparse.FileType('r'),
            help='grades file to read and parse')
    args = clparser.parse_args(argv)

    gfile = GradesFile(args.filename)
    if args.columns:
        args.columns = args.columns.split(',')
    if args.divs:
        args.divs = args.divs.split(',')
    if args.cumul:
        gfile.table.compute_cumul()
        if args.columns:
            args.columns.append('/Cumul/')
    if args.students:
        gfile.table = gfile.table.select(args.students)
    if args.mean:
        gfile.table.compute_mean()
    if args.group:
        gfile.table.compute_grouped_mean(group_by=args.group)
    gfile.print_file(div_on=args.divs, columns=args.columns,
                     tableonly=args.tableonly)


if __name__ == '__main__':
    run()
