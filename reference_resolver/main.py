"""




Have                Want            How
----                -----------     -----------------
citation            doi             citation_to_doi
citation            paper_info      citation_to_paper_info

retrieve_all_info - check Scopus, then web scrape
retrieve_only_references - check Scopus then web scrape


Reference Resolver
------------------

NOTE: All of these approaches use web-scraping directly from publisher sites.


Goal:
    Take something like this:
        Senís, Elena, et al. "CRISPR/Cas9‐mediated genome engineering:
        An adeno‐associated viral (AAV) vector toolbox."
        Biotechnology journal 9.11 (2014): 1402-1412.

    and retrieve the entry data and/or that paper's references from the
    corresponding site where it is hosted.

    Do the same for a DOI or link.

------------------

Basically follow the method outlined here:
    http://labs.crossref.org/resolving-citations-we-dont-need-no-stinkin-parser/

Another super helpful link about DOIs and publishers:
    https://webhome.weizmann.ac.il/home/comartin/doi.html

Steps:
    1) Search for the original reference on CrossRef
    2) Extract DOI from CrossRef
    3) Match DOI with provider
    4) Call appropriate scraper with DOI and get info
    5) Return info

"""
# Standard imports
#---------------------------------
import json
import json.decoder
import sys

if sys.version_info.major == 2:
    from urllib import quote as urllib_quote
else:
    from urllib.parse import quote as urllib_quote

# Third party imports
#---------------------------------
import requests
#https://github.com/ScholarTools/crossrefapi
from crossref.restful import Works

# Other Scholar Tools Imports
#--------------------------------------------
"""
try:
    from pypub.paper_info import PaperInfo
except ImportError:
    raise Exception("The pypub package is required for this code")


from pypub.publishers import pub_resolve

from pypub.utils import find_nth


import pypub.errors as pypub_errors

#from . import ref_retrieval
from . import errors

#TODO: Make an optional module ...
#TODO: Provide consistent optional summary ...
#from scopy import Scopus

Scopus = []
"""


#from database import db_logging as db

#DB Methods
#1) db.log_info(paper_info)
#2) db.get_saved_info(doi)
#3)   db.add_references(refs=saved_info.references, main_paper_doi=saved_info.doi.lower(),
#                                         main_paper_title=getattr(saved_info.entry, 'title', None))
#4) references, main_paper_exists = db.get_references_from_db(input)
#5) db.add_references(refs=references, main_paper_doi=input)

# -----------------------------------------------------

class PaperInfo():
    
    """
    doi
    url
    pdf_link
    references
    """
    def __init__(self, **kwargs):
        self.doi = kwargs.get('doi')
        
        """
        self.entry = kwargs.get('entry_dict')
        self.references = kwargs.get('references')
        
        self.doi_prefix = ''
        if self.doi is not None:
            self.doi_prefix = self.doi[:7]
        self.url = kwargs.get('url')
        self.pdf_link = kwargs.get('pdf_link')
        self.scraper_obj = kwargs.get('scraper_obj')
        self.publisher_interface = kwargs.get('publisher_interface')
        """

def citation_to_paper_info(citation):
    """
    Gets the paper and references information from
    a plaintext citation.
    
    Strategies
    ----------
    1) 

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
    paper_info : PaperInfo
        Class containing relevant paper meta-information and
        references list.
        Information about the paper itself is in 'entry' value, and is a dict
        (with str and dict values). References list is in 'references'
        value and is a list of dicts (each with str and dict values).
        Must call .__dict__ to be JSON-serializable
        
        
    Example
    --------
    import reference_resolver as rr
    citation = ('Senís, Elena, et al. "CRISPR/Cas9‐mediated genome ' +
                'engineering: An adeno‐associated viral (AAV) vector ' +
                'toolbox. Biotechnology journal 9.11 (2014): 1402-1412.')
    result = rr.citation_to_paper_info(citation)
    
    Improvements
    ------------
    1. Can we use CSL to generate the citation based on the journal style

    """
    # Encode raw citation
    escaped_quotation = urllib_quote(citation)
    
    #Citation decoding strategy
    #---------------------------------------------------
    #For right now we only have crossref.
    #
    #There are numerous other strategies out there ... (NYI)

    #TODO: Support etiquette
    w1 = Works().query(bibliographic=citation).select('DOI,score,title').rows(5)
    result = w1.get()
    
    n_values = result['message']['total-results']
    if n_values == 0:
        raise Exception('queried citation not found')
        
    entries = result['message']['items']
    
    #TODO: Support scoring support
    doi = entries[0]['DOI']
    
    #TODO: Check out these as well:
    #from https://github.com/CrossRef/rest-api-doc/issues/456
    #http://search.crossref.org/references
    #https://doi.crossref.org/simpleTextQuery

    
    """
    # Check if this DOI has been searched and saved before.
    # If it has, return saved information
    saved_info = db.get_saved_info(doi)
    if saved_info is not None:
        saved_info.make_interface_object()
        return saved_info

    paper_info = doi_to_webscraped_info(doi=doi, url=url)
    db.log_info(paper_info)

    return paper_info
    """

# This is commented out because retrieve_all_info subsumes it.
'''
def paper_info_from_doi(doi, skip_saved=False):
    """
    Gets the paper and references information from an article DOI.

    Parameters
    ----------
    doi : str
        DOI = digital object identifier.
        Unique ID assigned to a journal article.
        Example: 10.1002/biot.201400046

    Returns
    -------
    paper_info : PaperInfo
        See resolve_citation for description.

    """
    if not skip_saved:
        # Check for the DOI and corresponding paper in user's database.
        # If it has already been saved, return saved values.
        saved_info = db.get_saved_info(doi)
        if saved_info is not None:
            saved_info.make_interface_object()
            return saved_info


    paper_info = doi_to_webscraped_info(doi=doi)
    db.log_info(paper_info)

    return paper_info
'''


def get_references_from_doi():
    pass

#------------------------------------------------
#--- Old Code ----------------
#-----------------------------------

# def paper_info_from_link(link):
#     pub_dict = resolve_link(link)


# def resolve_link(link):
#     """
#     Gets the paper and references information from a link (URL)
#     to a specific journal article page.

#     Parameters
#     ----------
#     link : str
#         URL to journal article page on publisher's website.
#         Example: http://onlinelibrary.wiley.com/doi/10.1002/biot.201400046/references

#     Returns
#     -------
#     pub_dict : dict
#         See resolve_citation for description.

#     """

#     # First format the link correctly and determine the publisher
#     # ---------------------
#     # Make sure 'http://' and not 'www.' is at the beginning
#     link = link.replace('www.', '')
#     if link[0:4] != 'http':
#         link = 'http://' + link

#     # Find the third '/', which should be after the base URL
#     # i.e. giving something like http://onlinelibrary.wiley.com/
#     end_of_base_url = find_nth(link, '/', 3)
#     base_url = link[:end_of_base_url+1]

#     return pub_resolve.get_publisher_site_info(base_url=base_url)


# def link_to_doi(link):
#     return_values = resolve_link(link)
#     return return_values


# def citation_to_doi(citation):
#     """
#     Gets the DOI from
#     a plaintext citation.

#     Uses a search to CrossRef.org to retrive paper DOI.

#     Parameters
#     ----------
#     citation : str
#         Full journal article citation.
#         Example: Senís, Elena, et al. "CRISPR/Cas9‐mediated genome
#                 engineering: An adeno‐associated viral (AAV) vector
#                 toolbox. Biotechnology journal 9.11 (2014): 1402-1412.

#     Returns
#     -------
#     doi : None or str
#     """
#     # Encode raw citation
#     citation = urllib_quote(citation)

#     # Search for citation on CrossRef.org to try to get a DOI link
#     api_search_url = 'http://search.labs.crossref.org/dois?q=' + citation
#     try:
#         response = requests.get(api_search_url).json()
#     except json.decoder.JSONDecodeError:
#         return None

#     resp = response[0]
#     doi = resp.get('doi')
#     title = resp.get('title')

#     if doi is None:
#         return None

#     # If crossref returns a http://dx.doi.org/ link, retrieve the doi from it
#     # and save the URL to pass to doi_to_info
#     if 'http://dx.doi.org/' in doi:
#         doi = doi.replace('http://dx.doi.org/', '')
#         doi = doi.strip()

#     return doi, title


# def doi_to_webscraped_info(doi=None, url=None, refs_only=False):
#     """
#     Gets entry and references information for an article DOI.

#     Uses saved dicts matching DOI prefixes to publishers and web scrapers
#     to retrieve information. Will fail if DOI prefix hasn't been saved
#     with a publisher link or if a scraper for a specific publisher
#     site hasn't been built.

#     Parameters
#     ----------
#     doi : str
#         Unique ID assigned to a journal article.
#     url : str
#         The CrossRef URL to the article page.
#         I.e. http://dx.doi.org/10.######

#     Returns
#     -------
#     paper_info : PaperInfo
#         Class containing parameters including the following:

#         entry_dict : dict
#             Contains information about the paper referenced by the DOI.
#             Includes title, authors, affiliations, publish date, journal
#             title, volume, and pages, and keywords. Some values are other
#             dicts (for example, the author info with affiliation values).
#             Formatted to be JSON serializable.

#         refs_dicts : list of dicts
#             Each list item is a dict corresponding to an individual reference
#             from the article's reference list. Includes title, authors,
#             publishing date, journal title, volume, and pages (if listed),
#             and any external URL links available (i.e. to where it is hosted
#             on other sites, or pdf links).

#         full_url : str
#             URL to the journal article page on publisher's website.

#     """
#     # Resolve DOI or URL through PyPub pub_resolve methods
#     publisher = pub_resolve.publisher_from_doi_or_url(doi=doi, url=url)

#     # Create a PaperInfo object to hold all information and call appropriate scraper
#     paper_info = PaperInfo(doi=doi, url=url)
#     paper_info.publisher_interface = publisher
#     if refs_only:
#         paper_info.get_references()
#     else:
#         paper_info.populate_info()

#     return paper_info


# def retrieve_all_info(id_value, input_type, skip_saved=False):
#     """
#     Checks Scopus first, and then web-scrapes.

#     input_type:
#         'doi'
#         'pmid'
#         'eid'
#         'url'
        
#     Returns
#     -------
#     paper_info : PaperInfo object

#     """
#     paper_info = None

#     scopus_api = Scopus()

#     if input_type == 'doi':
#         # Check for the DOI and corresponding paper in user's database.
#         # If it has already been saved, return saved values.
#         if not skip_saved:
#             saved_info = db.get_saved_info(input)
#             if saved_info:
#                 if getattr(saved_info, 'references', None) is not None:
#                     saved_info.make_interface_object()
#                     return saved_info
#                 else:
#                     saved_info.references = ref_retrieval.retrieve_references(saved_info.doi)
#                     # These lines probably don't belong in this function. This is for the case in which
#                     # a paper's information has already been saved in the database, but has no corresponding
#                     # references. This saves the references after having retrieved them.
#                     if saved_info.references is not None and len(saved_info.references) > 0:
#                         db.add_references(refs=saved_info.references, main_paper_doi=saved_info.doi.lower(),
#                                          main_paper_title=getattr(saved_info.entry, 'title', None))
#                     else:
#                         return saved_info

#         try:
#             # This next line fetches information from Scopus
#             paper_info = scopus_api.get_all_data.get_from_doi(doi=input)
#         except LookupError or ConnectionRefusedError or ConnectionError:
#             # If Scopus could not connect or info wasn't found there,
#             # this line attempts to web-scrape from a publisher site.
#             paper_info = doi_to_webscraped_info(doi=input)
#             db.log_info(paper_info)

#         if paper_info.pdf_link is None:
#             if paper_info.publisher_interface is None:
#                 try:
#                     paper_info.make_interface_object()
#                 except pypub_errors.UnsupportedPublisherError:
#                     paper_info.publisher_interface = None
#             if paper_info.publisher_interface is not None:
#                 try:
#                     paper_info.pdf_link = paper_info.publisher_interface.get_pdf_link(input)
#                 except Exception:
#                     pass

#     elif input_type == 'pubmed_id':
#         paper_info = scopus_api.get_all_data.get_from_pubmed(pubmed_id=input)

#     return paper_info


# def retrieve_only_references(input, input_type, skip_saved=False):
#     """
#     Checks Scopus first, and then web-scrapes.

#     Potential input types:
#     'doi', 'pubmed_id', 'eid', 'url'

#     Returns
#     -------
#     references

#     """
#     scopus_api = Scopus()

#     if input_type == 'doi':
#         # Check for the DOI and corresponding paper in user's database.
#         # If it has already been saved, return saved values.
#         if not skip_saved:
#             references, main_paper_exists = db.get_references_from_db(input)
#             if references:
#                 return references
#             else:
#                 references = ref_retrieval.retrieve_references(input)
#                 # These lines probably don't belong in this function. This is for the case in which
#                 # a paper's information has already been saved in the database, but has no corresponding
#                 # references. This saves the references after having retrieved them.
#                 if references and main_paper_exists:
#                     db.add_references(refs=references, main_paper_doi=input)
#                 else:
#                     return references

#         else:
#             references = ref_retrieval.retrieve_references(input)
#             return references

#     elif input_type == 'pubmed_id':
#         paper_info = scopus_api.get_all_data.get_from_pubmed(pubmed_id=input)
#         return paper_info
#     else:
#         raise errors.UnsupportedTypeError('Only DOI and PMID lookups are supported at this time.')



# '''
# DOI_SEARCH = 'http://doi.crossref.org/search/doi'

# crossref_email = 'jim.hokanson@gmail.com'

# def getMeta(doi, format='unixsd'):

#     """

#     Given a doi, return article meta data

#     #Output formats:
#     #-------------------------
#     #1) xsd_xml - default - 'unixsd' - recommended for future use
#     #http://help.crossref.org/#unixsd
#     #DOC: query_output3.0
#     #http://www.crossref.org/schema/documentation/crossref_query_output3.0/query_output3.0.html
#     #2) 'unixref'
#     #http://help.crossref.org/#unixref-query-result-format

#     #TODO: Document why unixref might be preferable
#     #TODO: Finish parsing of xsd


#     """

#     #pid    - email
#     #format - unixsd
#     #doi    - doi
#     payload = {'pid':crossref_email, 'format':format, 'doi':doi}
#     r = requests.get(DOI_SEARCH, params=payload)

#     #XSD code generation
#     #http://www.rexx.com/~dkuhlman/generateDS.html
#     #generateds_gui.py

# '''