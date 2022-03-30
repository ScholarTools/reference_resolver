#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"""

from .errors import OptionalLibraryError

class MissingModule(object):
    """
    This class throws an error upon trying to get an attribute.
    
    The idea is that if you import a missing module, and then try and get a
    class or function from this missing module (i.e. actually use the import
    calls) then an error is thrown.
    """
    def __init__(self,msg):
        self.msg = msg
        
    def __getattr__(self, name):
        #do we really want getattribute instead?
        #=> I think getattribute is more comprehensive
        raise OptionalLibraryError(self.msg)



pubmed_available = True
try:
    import pubmed
except ImportError:
    pubmed_available = False
    pubmed = MissingModule('The method called requires the library "reference_resolver" from the Scholar Tools Github repo')
    # TODO: Provide link to repo
    # Eventually pip the repo and specify pip is possible

