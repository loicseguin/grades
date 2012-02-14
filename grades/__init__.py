#-*- coding: utf-8 -*-
"""
Grades
======

For managing student grades, most teachers use spreadsheet tools. With these
tools, it is hard to maintain grades in plain text files that are easily
readable by humans. The goal of **grades** is to let teachers manage their
students' grade in plain text file while providing tools to parse the file and
calculate students and group means.

The table format that **grades** use is the one Emacs `org-mode
<http://orgmode.org/index.html>`_ uses. Using org-mode, grades tables can be
easily set up and then **grades** will happily compute all the required values.

"""


from __future__ import print_function  # For Python 2 compatibility.


__author__ = "Loïc Séguin-C. <loicseguin@gmail.com>"
__license__ = "BSD"
__version__ = "0.1"


from . import classes
from . import runner
