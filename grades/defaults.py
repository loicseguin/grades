#-*- coding: utf-8 -*-
"""
defaults
========

Default values for constants used throughout the program.

"""


__author__ = "Loïc Séguin-C. <loicseguin@gmail.com>"
__license__ = "BSD"


input_filename = 'Grades.txt'
output_filename = 'Grades.txt'
ignore_char = '*'
calc_char = '*'
precision = 2
padding_left = 1
padding_right = 1
min_cell_width = 5
columns = [
        {'title': 'Name', 'is_num': False, 'evalu': None, 'width': 0},
        {'title': 'Group', 'is_num': False, 'evalu': None, 'width': 0},
        {'title': 'Test 1', 'is_num': True, 'width': 0,
            'evalu': {'max_grade': 20., 'weight': 5., 'width': 0}},
        {'title': 'Test 2', 'is_num': True, 'width': 0,
            'evalu': {'max_grade': 20., 'weight': 5., 'width': 0}},
        {'title': 'Test 3', 'is_num': True, 'width': 0,
            'evalu': {'max_grade': 20., 'weight': 5., 'width': 0}},
        {'title': 'Midterm', 'is_num': True, 'width': 0,
            'evalu': {'max_grade': 100., 'weight': 30., 'width': 0}},
        {'title': 'Test 4', 'is_num': True, 'width': 0,
            'evalu': {'max_grade': 20., 'weight': 5., 'width': 0}},
        {'title': 'Test 5', 'is_num': True, 'width': 0,
            'evalu': {'max_grade': 20., 'weight': 5., 'width': 0}},
        {'title': 'Test 6', 'is_num': True, 'width': 0,
            'evalu': {'max_grade': 20., 'weight': 5., 'width': 0}},
        {'title': 'Final', 'is_num': True, 'width': 0,
            'evalu': {'max_grade': 100., 'weight': 40., 'width': 0}}]
