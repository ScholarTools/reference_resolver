"""

Reference Resolver
------------------

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
import json
import json.decoder
import sys

if sys.version_info.major == 2:
    from urllib import quote as urllib_quote
else:
    from urllib.parse import quote as urllib_quote

# Third party imports
import requests

# Local imports
from pypub.paper_info import PaperInfo
import pypub.publishers.pub_resolve as pub_resolve
from pypub.utils import find_nth

from database import db_logging as db


# -----------------------------------------------------


def paper_info_from_citation(citation):
    """
    Gets the paper and references information from
    a plaintext citation.

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

    """
    # Encode raw citation
    citation = urllib_quote(citation)

    # Search for citation on CrossRef.org to try to get a DOI link
    api_search_url = 'http://search.labs.crossref.org/dois?q=' + citation
    response = requests.get(api_search_url).json()
    resp = response[0]
    doi = resp.get('doi')
    print(doi)

    if doi is None:
        raise LookupError('No DOI could be found for the given citation')

    # If crossref returns a http://dx.doi.org/ link, retrieve the doi from it
    # and save the URL to pass to doi_to_info
    url = None
    if doi[0:18] == 'http://dx.doi.org/':
        url = doi
        doi = doi[18:]

    # Check if this DOI has been searched and saved before.
    # If it has, return saved information
    saved_info = db.get_saved_info(doi)
    if saved_info is not None:
        saved_info.make_interface_object()
        return saved_info

    paper_info = doi_to_info(doi=doi, url=url)
    db.log_info(paper_info)

    return paper_info


def paper_info_from_doi(doi):
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
    doi_prefix = doi[0:7]


    # Check for the DOI and corresponding paper in user's database.
    # If it has already been saved, return saved values.
    saved_info = db.get_saved_info(doi)
    if saved_info is not None:
        saved_info.make_interface_object()
        return saved_info


    paper_info = doi_to_info(doi=doi)
    db.log_info(paper_info)

    return paper_info


def paper_info_from_link(link):
    pub_dict = resolve_link(link)


def resolve_link(link):
    """
    Gets the paper and references information from a link (URL)
    to a specific journal article page.

    Parameters
    ----------
    link : str
        URL to journal article page on publisher's website.
        Example: http://onlinelibrary.wiley.com/doi/10.1002/biot.201400046/references

    Returns
    -------
    pub_dict : dict
        See resolve_citation for description.

    """

    # First format the link correctly and determine the publisher
    # ---------------------
    # Make sure 'http://' and not 'www.' is at the beginning
    link = link.replace('www.', '')
    if link[0:4] != 'http':
        link = 'http://' + link

    # Find the third '/', which should be after the base URL
    # i.e. giving something like http://onlinelibrary.wiley.com/
    end_of_base_url = find_nth(link, '/', 3)
    base_url = link[:end_of_base_url+1]

    return pub_resolve.get_publisher_site_info(base_url=base_url)


def link_to_doi(link):
    return_values = resolve_link(link)
    return return_values


def doi_from_citation(citation):
    """
    Gets the DOI from
    a plaintext citation.

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
    doi : str
    """
    # Encode raw citation
    citation = urllib_quote(citation)

    # Search for citation on CrossRef.org to try to get a DOI link
    api_search_url = 'http://search.labs.crossref.org/dois?q=' + citation
    try:
        response = requests.get(api_search_url).json()
    except json.decoder.JSONDecodeError:
        return None

    resp = response[0]
    doi = resp.get('doi')
    print(doi)

    if doi is None:
        return doi

    # If crossref returns a http://dx.doi.org/ link, retrieve the doi from it
    # and save the URL to pass to doi_to_info
    if 'http://dx.doi.org/' in doi:
        doi = doi.replace('http://dx.doi.org/', '')
        doi = doi.strip()

    return doi


def doi_to_info(doi=None, url=None):
    """
    Gets entry and references information for an article DOI.

    Uses saved dicts matching DOI prefixes to publishers and web scrapers
    to retrieve information. Will fail if DOI prefix hasn't been saved
    with a publisher link or if a scraper for a specific publisher
    site hasn't been built.

    Parameters
    ----------
    doi : str
        Unique ID assigned to a journal article.
    url : str
        The CrossRef URL to the article page.
        I.e. http://dx.doi.org/10.######

    Returns
    -------
    paper_info : PaperInfo
        Class containing parameters including the following:

        entry_dict : dict
            Contains information about the paper referenced by the DOI.
            Includes title, authors, affiliations, publish date, journal
            title, volume, and pages, and keywords. Some values are other
            dicts (for example, the author info with affiliation values).
            Formatted to be JSON serializable.

        refs_dicts : list of dicts
            Each list item is a dict corresponding to an individual reference
            from the article's reference list. Includes title, authors,
            publishing date, journal title, volume, and pages (if listed),
            and any external URL links available (i.e. to where it is hosted
            on other sites, or pdf links).

        full_url : str
            URL to the journal article page on publisher's website.

    """
    # Resolve DOI or URL through PyPub pub_resolve methods
    publisher_base_url, full_url = pub_resolve.get_publisher_urls(doi=doi, url=url)
    pub_dict = pub_resolve.get_publisher_site_info(publisher_base_url)

    # Create a PaperInfo object to hold all information and call appropriate scraper
    paper_info = PaperInfo(doi=doi, scraper_obj=pub_dict['object'], url=full_url)
    paper_info.populate_info()

    return paper_info

'''
DOI_SEARCH = 'http://doi.crossref.org/search/doi'

crossref_email = 'jim.hokanson@gmail.com'

def getMeta(doi, format='unixsd'):

    """

    Given a doi, return article meta data

    #Output formats:
    #-------------------------
    #1) xsd_xml - default - 'unixsd' - recommended for future use
    #http://help.crossref.org/#unixsd
    #DOC: query_output3.0
    #http://www.crossref.org/schema/documentation/crossref_query_output3.0/query_output3.0.html
    #2) 'unixref'
    #http://help.crossref.org/#unixref-query-result-format

    #TODO: Document why unixref might be preferable
    #TODO: Finish parsing of xsd


    """

    #pid    - email
    #format - unixsd
    #doi    - doi
    payload = {'pid':crossref_email, 'format':format, 'doi':doi}
    r = requests.get(DOI_SEARCH, params=payload)

    #XSD code generation
    #http://www.rexx.com/~dkuhlman/generateDS.html
    #generateds_gui.py

'''