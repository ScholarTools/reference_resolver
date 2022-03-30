# -*- coding: utf-8 -*-
"""
Contains all custom errors called within the reference_resolver package.
"""

class OptionalLibraryError(Exception):
    pass

class DatabaseError(Exception):
    pass

class UnsupportedTypeError(Exception):
    pass
