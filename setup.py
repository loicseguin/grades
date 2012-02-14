# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
    name = 'grades',
    packages = ['grades'],
    scripts = ['bin/grades'],
    version = '0.1',
    description = 'Minimalist grades management for teachers.',
    author = 'Loïc Séguin-C.',
    author_email = 'loicseguin@gmail.com',
    url = 'https://github.com/loicseguin/grades',
    download_url = 'https://github.com/loicseguin/grades/tarball/master',
    keywords = ['grades', 'student', 'teacher', 'class management'],
    classifiers = [
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Education',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: Database',
        'Topic :: Education',
        'Topic :: Text Processing',
        'Topic :: Utilities'
        ],
    long_description = """For managing student grades, most teachers use
    spreadsheet tools. With these tools, it is hard to maintain grades in plain
    text files that are easily readable by humans. The goal of grades is to let
    teachers manage their students' grade in plain text file while providing
    tools to parse the file and calculate students and group means."""
)
