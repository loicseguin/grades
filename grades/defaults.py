#-*- coding: utf-8 -*-
"""
defaults
========

Default values for constants used throughout the program.

"""


__author__ = "Loïc Séguin-C. <loicseguin@gmail.com>"
__license__ = "BSD"


INPUT_FILENAME = 'Grades.txt'
OUTPUT_FILENAME = 'Grades.txt'
IGNORE_CHAR = '*'
CALC_CHAR = '*'
PRECISION = 2
PADDING_LEFT = 1
PADDING_RIGHT = 1
MIN_CELL_WIDTH = 5
TABLE_FORMAT = 'org'
COLUMNS = [
        {'title': 'Name', 'is_num': False, 'evalu': None, 'width': 0},
        {'title': 'Group', 'is_num': False, 'evalu': None, 'width': 0},
        {'title': 'Test 1', 'is_num': True, 'width': 0,
            'evalu': {'max_grade': 20., 'weight': 5.}},
        {'title': 'Test 2', 'is_num': True, 'width': 0,
            'evalu': {'max_grade': 20., 'weight': 5.}},
        {'title': 'Test 3', 'is_num': True, 'width': 0,
            'evalu': {'max_grade': 20., 'weight': 5.}},
        {'title': 'Midterm', 'is_num': True, 'width': 0,
            'evalu': {'max_grade': 100., 'weight': 30.}},
        {'title': 'Test 4', 'is_num': True, 'width': 0,
            'evalu': {'max_grade': 20., 'weight': 5.}},
        {'title': 'Test 5', 'is_num': True, 'width': 0,
            'evalu': {'max_grade': 20., 'weight': 5.}},
        {'title': 'Test 6', 'is_num': True, 'width': 0,
            'evalu': {'max_grade': 20., 'weight': 5.}},
        {'title': 'Final', 'is_num': True, 'width': 0,
            'evalu': {'max_grade': 100., 'weight': 40.}}]
