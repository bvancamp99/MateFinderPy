# Author: Bryce Van Camp
# Project: MateFinder
# File: peekable.py
# Description: Iterator wrapper object with peek and has_next functionality


import itertools


_marker = object()


class Peekable:
    def __init__(self, iterable):
        self._it = iter(iterable)

    def __iter__(self):
        return self

    def __next__(self):
        return next(self._it)

    def peek(self, default=_marker):
        '''
        Implements peeking with next-like default parameter functionality
        '''
        try:
            peeked_var = next(self)
        except StopIteration:
            if default is _marker:
                raise
            return default

        # Add back to iterator beginning if before StopIteration
        self._it = itertools.chain([peeked_var], self._it)

        return peeked_var

    def has_next(self):
        sentinel = object()
        return self.peek(default=sentinel) is not sentinel
