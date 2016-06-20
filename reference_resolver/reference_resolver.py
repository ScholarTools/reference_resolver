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
import csv
import inspect
import json
import string
import sys

import os
import random

# Third party imports
import requests

# Local imports
from pypub.paper_info import PaperInfo
import pypub.publishers.pub_resolve as pub_resolve


if sys.version_info.major == 2:
    from urllib import quote as urllib_quote
else:
    from urllib.parse import quote as urllib_quote
# -----------------------------------------------------


def resolve_citation(citation):
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
    doi = response[0]['doi']
    print(doi)

    # If crossref returns a http://dx.doi.org/ link, retrieve the doi from it
    # and save the URL to pass to doi_to_info
    url = None
    if doi[0:18] == 'http://dx.doi.org/':
        url = doi
        doi = doi[18:]
    doi_prefix = doi[0:7]

    # Check if this DOI has been searched and saved before.
    # If it has, return saved information
    saved_info = get_saved_info(doi)
    if saved_info is not None:
        saved_paper_info = PaperInfo()
        for k, v in saved_info.items():
            setattr(saved_paper_info, k, v)
        saved_paper_info.make_interface_object()
        return saved_paper_info

    paper_info = doi_to_info(doi, doi_prefix, url)

    idnum = assign_id()
    paper_info.idnum = idnum

    log_info(paper_info)

    return paper_info


def resolve_doi(doi):
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

    # Same steps as in resolve_citation
    saved_info = get_saved_info(doi)
    if saved_info is not None:
        saved_paper_info = PaperInfo()
        for k, v in saved_info.items():
            setattr(saved_paper_info, k, v)
        saved_paper_info.make_interface_object()
        return saved_paper_info



    paper_info = doi_to_info(doi)
    idnum = assign_id()
    paper_info.idnum = idnum

    log_info(paper_info)

    return paper_info


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

    base_url = link[:link.find('.com')+4]

    return pub_resolve.get_publisher_site_info(base_url=base_url)


def link_to_doi(link):
    return_values = resolve_link(link)
    return return_values


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


def assign_id():
    """
    Generates an ID string specific to this program and file system
    to save article information. This is because not all papers will
    always have a DOI/PubMed ID/etc. so there needs to be a way to
    save the articles for later local retrieval.

    Returns
    -------
    idnum : str
        Randomly generated alphanumeric string of length 8

    """

    idnum = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(8))
    return idnum


def get_saved_info(doi):
    """
    Checks if paper information has previously been saved, and if so,
    retrieves that information from local files.

    Parameters
    ----------
    doi : str
        Unique ID assigned to a journal article.

    Returns
    -------
    json.loads(wholestring) : JSON-formatted dict
        See Also: resolve_citation. This return value is the same as
        paper_info, but as a dict, not str.

    """
    current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    root_dir = os.path.dirname(current_dir)
    doi_list_file = os.path.join(root_dir, 'paper_data/doi_list.csv')
    paper_data_dir = os.path.join(root_dir, 'paper_data/')

    with open(doi_list_file, 'r') as dlist:
        reader = csv.reader(dlist)
        saved_id = None
        for row in reader:
            if doi == row[0]:
                saved_id = row[1]

    if saved_id is not None:
        file_name = str(doi[0:7]) + '/' + saved_id + '.txt'
        new_file = os.path.join(paper_data_dir, file_name)
        with open(new_file, 'r') as file:
            wholestring = file.read()
        return json.loads(wholestring)
    else:
        return None


def log_info(paper_info):
    """
    Saves article information to local files for retrieval.

    Papers from a specific publisher are organized by their DOI prefix.
    A directory with that prefix name is made if it does not already
    exist, and a file named using idnum is created, which holds
    paper_info. In a separate doi_list.csv file, the DOI and its
    assigned idnum are saved as a tuple so that the information can
    be found later.

    Parameters
    ----------
    paper_info : PaperInfo
        See resolve_citation for description.

    """

    current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    doi_list_file = os.path.join(current_dir, 'paper_data/doi_list.csv')
    paper_data_dir = os.path.join(current_dir, 'paper_data/')

    # First make a folder for DOI prefix if one does not already exist
    os.makedirs(os.path.join(paper_data_dir, str(paper_info.doi_prefix)), exist_ok=True)

    # Log the DOI and corresponding identifying ID number on master CSV file
    with open(doi_list_file, 'a') as dlist:
        writer = csv.writer(dlist)
        writer.writerow([paper_info.doi, paper_info.idnum])

    file_name = str(paper_info.doi_prefix) + '/' + str(paper_info.idnum) + '.txt'

    # Create dict of relevant information from paper_info
    pi_dict = dict()
    pi_dict['entry'] = paper_info.entry
    pi_dict['references'] = paper_info.references
    pi_dict['doi'] = paper_info.doi
    pi_dict['scraper_obj'] = paper_info.scraper_obj

    with open(os.path.join(paper_data_dir, file_name), 'w') as paper:
        paper.write(json.dumps(pi_dict))


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