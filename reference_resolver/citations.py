#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"""

#Standard Library
#------------------------
import sys

if sys.version_info.major == 2:
    from urllib import quote as urllib_quote
else:
    from urllib.parse import quote as urllib_quote
    
#Third party
#------------------------    
import requests


#Local
#------------------------
from . import utils
from .utils import get_truncated_display_string as td
#from .utils import get_list_class_display as cld

def citation_to_doi(citation):
    """

    Uses a search to CrossRef.org to retrive paper DOI.

    Parameters
    ----------
    citation : str
        Full journal article citation.
        Example: Senís, Elena, et al. "CRISPR/Cas9‐mediated genome
                engineering: An adeno‐associated viral (AAV) vector
                toolbox. Biotechnology journal 9.11 (2014): 1402-1412.
                
    Returns
    -------
    _CitationDOISearchResponse
    
    Usage Notes
    -----------
    This is relatively slow. I'm not sure how much of the slowness is due to 
    parsing into parts versus using those parts to find a DOI (of course those
    could be done together). 
    """
    
    citation = urllib_quote(citation)

    # Search for citation on CrossRef.org to try to get a DOI link
    
    #TODO: Where is this documented????
    #Examples: https://search.crossref.org/help/search
    #
    #Inserting /dois as an endpoint converts results from html to JSON
    api_search_url = 'http://search.crossref.org/dois?q=' + citation
    json_data = requests.get(api_search_url).json()
    
    #Multiple responses are possible. Note we might not have anything:
    best_match_data = json_data[0]
    
    return _CitationDOISearchResponse(best_match_data)

class _CitationDOISearchResponse(object):
    
    """
    Attributes
    ----------
    doi
    score : float
        0 to ?
        Observed 99 and 122.7
        This may be useful in indicating how well our query matches an object.
        Higher appears to be better.
    normalized_score : float
        This may always be 100 since we are grabbing the best response
    raw : dict
        The original JSON response
        
    See Also
    --------
    citation_to_doi
    """

    def __init__(self, json):
        """
        Example:
         "doi": "http://dx.doi.org/10.1002/biot.201400046",
        "score": 99.11717,
        "normalizedScore": 100,
        "title": "CRISPR/Cas9-mediated genome engineering: An adeno-associated viral (AAV) vector toolbox",
        "fullCitation":
        """
        
        doi = json.get('doi')
    
        if doi is None:
            raise LookupError('No DOI could be found for the given citation')
    
        # If crossref returns a http://dx.doi.org/ link, retrieve the doi from it
        # and save the URL to pass to doi_to_info
        #
        #For now results all seem to be http, no https ...
        if doi[0:18] == 'http://dx.doi.org/':
            doi = doi[18:]
        
        self.doi = doi
        self.score = json.get('score')
        self.normalized_score = json.get('normalized_score')
        self.raw = json
        
    def __repr__(self):
        pv = ['doi', self.doi,
              'score', self.score,
              'normalized_score', self.normalized_score,
              'raw',td(str(self.raw))]
        return utils.property_values_to_string(pv)        