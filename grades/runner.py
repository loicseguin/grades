#-*- coding: utf-8 -*-
"""runner

"""


__author__ = "Loïc Séguin-C. <loicseguin@gmail.com>"
__license__ = "BSD"
__version__ = "0.1"


import argparse
from .classes import GradesFile

def run():
    clparser = argparse.ArgumentParser(
        description='A grade management tool with plain text tables storage.')
    clparser.add_argument('-v', '--version', action='version',
            version='%(prog)s 0.1')
    clparser.add_argument('-m', '--mean', action='store_true',
            help='print the mean for each evaluation')
    clparser.add_argument('-c', '--cumul', action='store_true',
            help='print the cumulative grade for each student')
    clparser.add_argument('-g', '--grouped',
            help='print the mean for each GROUPED for each evaluation; '
                 + 'GROUPED must be the name of one of the columns in the '
                 + 'table')
    clparser.add_argument('-d', '--div', nargs='*',
            help='draw a horizontal division between students in different '
                 + 'DIV; DIV must be the name of one of the columns in '
                 + 'the table')
    clparser.add_argument('filehandle', type=argparse.FileType('r'),
            help='grades file to read and parse')
    args = clparser.parse_args()

    gfile = GradesFile(args.filehandle)
    if args.cumul:
        gfile.table.compute_cumul()
    if args.mean:
        gfile.table.compute_mean()
    if args.grouped:
        gfile.table.compute_grouped_mean(group_by=args.grouped)
    gfile.print_file(div_on=args.div)


if __name__ == '__main__':
    run()


