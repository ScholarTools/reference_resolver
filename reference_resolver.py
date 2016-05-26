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

import sys
import requests
import json
import csv
import importlib
import string
import random
import os
import inspect
from pypub.utils import convert_to_dict
from pypub.publishers.pub_resolve import resolve_link

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
    paper_info : dict
        Dict containing relevant paper meta-information and
        references list.
        Paper info is in 'entry' value, and is in the form of another dict
        (with str and dict values). References list is in 'references'
        value and is a list of dicts (each with str and dict values).
        This is formatted to be JSON-serializable.

    """
    # Encode raw citation
    citation = urllib_quote(citation)

    # Search for citation on CrossRef.org to try to get a DOI link
    api_search_url = 'http://search.labs.crossref.org/dois?q=' + citation
    response = requests.get(api_search_url).json()
    doi = response[0]['doi']
    print(doi)

    # If crossref returns a http://dx.doi.org/ link, retrieve the doi from it
    if doi[0:18] == 'http://dx.doi.org/':
        doi = doi[18:]
    doi_prefix = doi[0:7]

    # Check if this DOI has been searched and saved before.
    # If it has, return saved information
    saved_info = get_saved_info(doi)
    if saved_info is not None:
        return saved_info

    [entry_dict, refs_dicts, url] = doi_to_info(doi, doi_prefix)

    idnum = assign_id()

    print(doi)

    paper_info = {'entry': entry_dict, 'references': refs_dicts, 'doi': doi, 'url': url}
    log_info(doi, doi_prefix, idnum, paper_info)

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
    paper_info : dict
        See resolve_citation for description.

    """
    doi_prefix = doi[0:7]

    # Same steps as in resolve_citation
    saved_info = get_saved_info(doi)
    if saved_info is not None:
        return saved_info

    [entry_dict, refs_dicts, pdf_link, url] = doi_to_info(doi, doi_prefix)
    idnum = assign_id()

    paper_info = {'entry': entry_dict, 'references': refs_dicts, 'pdf_link': pdf_link, 'doi': doi, 'url': url}
    log_info(doi, doi_prefix, idnum, paper_info)

    return paper_info


def doi_to_info(doi, doi_prefix):
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
    doi_prefix : str
        The first 7 characters of the DOI above. I.e. 10.XXXX.
        This prefix is used to identify publisher information.

    Returns
    -------
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
    current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    doi_prefix_file = os.path.join(current_dir, 'doi_prefix_dict.txt')
    root = os.path.dirname(current_dir)

    # Import current prefix dict
    with open(doi_prefix_file, 'r') as f:
        str_dict = f.read()
    prefix_dict = json.loads(str_dict)

    # With the DOI prefix we got from the CrossRef search,
    # look in the prefix_dict to get the corresponding base URL.
    # The url should be in index 1
    if len(prefix_dict[doi_prefix]) > 1:
        pub_url = prefix_dict[doi_prefix][1]
    else:
        raise IndexError('The DOI prefix is not yet set assigned to a publisher')

    #print(pub_url)

    site_features_file = os.path.join(root, 'pypub/pypub/publishers/site_features.csv')
    # Now search the site_features.csv file to get information relevant to that provider
    with open(site_features_file) as f:
        reader = csv.reader(f)
        headings = next(reader)  # Save the first line as the headings
        values = None
        for row in enumerate(reader):
            if pub_url in row[1]:
                values = row[1]  # Once the correct row is found, save it as values
                break

    # Turn the headings and values into a callable dict
    pub_dict = dict(zip(headings, values))
    #print(pub_dict)

    # Get the name of the scraper .py file from the dictionary
    # Import the correct scraper file
    scrapername = 'pypub.scrapers.' + pub_dict['scraper']
    scraper = importlib.import_module(scrapername)

    # Construct the correct direct URL from the dictionary
    full_url = pub_dict['provider_root_url'] + pub_dict['url_prefix'] + str(doi) + pub_dict['article_page_suffix']

    # If ScienceDirect, need to get real URL featuring PII
    # The URLs don't use the DOI
    if pub_dict['provider_root_url'] == 'http://sciencedirect.com':
        resp = requests.get('http://dx.doi.org/' + doi)
        full_url = resp.url

    print(full_url)

    # Call the scraper to get entry info and reference information
    entry_info = scraper.get_entry_info(full_url)
    references = scraper.get_references(full_url)
    pdf_link = scraper.get_pdf_link(full_url)

    # Make entry into a dict
    entry_dict = convert_to_dict(entry_info)

    # Make a list of refs as dict objects
    refs_dicts = []
    for ref in references:
        refs_dicts.append(convert_to_dict(ref))

    return entry_dict, refs_dicts, pdf_link, full_url


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
    doi_list_file = os.path.join(current_dir, 'paper_data/doi_list.csv')
    paper_data_dir = os.path.join(current_dir, 'paper_data/')

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


def log_info(doi, prefix, idnum, paper_info):
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
    doi : str
        Unique ID assigned to a journal article.

    prefix : str
        First 7 characters of DOI in format 10.XXXX.
        Gives publisher information

    idnum : str
        Random alphanumeric string assigned to article info for
        local identification and retrieval.
        See Also: assign_id.

    paper_info : dict
        See resolve_citation for description.

    """

    current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    doi_list_file = os.path.join(current_dir, 'paper_data/doi_list.csv')
    paper_data_dir = os.path.join(current_dir, 'paper_data/')

    # First make a folder for DOI prefix if one does not already exist
    os.makedirs(os.path.join(paper_data_dir, str(prefix)), exist_ok=True)

    # Log the DOI and corresponding identifying ID number on master CSV file
    with open(doi_list_file, 'a') as dlist:
        writer = csv.writer(dlist)
        writer.writerow([doi, idnum])

    file_name = str(prefix) + '/' + str(idnum) + '.txt'
    with open(os.path.join(paper_data_dir, file_name), 'w') as paper:
        paper.write(json.dumps(paper_info))


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