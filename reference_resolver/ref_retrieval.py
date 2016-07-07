# Local imports
import database.db_logging as db

import reference_resolver as rr
from scopy import Scopus

api = Scopus()


def retrieve_references(doi):
    """
    This retrieves references from online sources.
    This is to be used when a paper is in a user's library
    but the references have not been retrieved and connected
    to the paper in the database.

    """
    tried_rr = False
    try:
        refs = api.bibliography_retrieval.get_from_doi(doi=doi)
    except LookupError or ConnectionRefusedError or ConnectionError:
        tried_rr = True
        paper_info = rr.doi_to_info(doi=doi)
        refs = paper_info.references

    if len(refs) == 0 and not tried_rr:
        paper_info = rr.doi_to_info(doi=doi)
        refs = paper_info.references

    return refs


def retrieve_all_info(input, input_type, skip_saved=False):
    """
    Checks Scopus first, and then web-scrapes.

    Potential input types:
    'doi', 'pubmed_id', 'eid', 'url'

    Returns
    -------
    paper_info : PaperInfo object

    """
    paper_info = None

    if input_type == 'doi':
        # Check for the DOI and corresponding paper in user's database.
        # If it has already been saved, return saved values.
        if not skip_saved:
            saved_info = db.get_saved_info(input)
            if saved_info is not None:
                saved_info.make_interface_object()
                return saved_info

        try:
            paper_info = api.get_all_data.get_from_doi(doi=input)
        except LookupError or ConnectionRefusedError or ConnectionError:
            paper_info = rr.paper_info_from_doi(doi=input)

        if len(paper_info.references) == 0 or paper_info.entry is None:
            paper_info = rr.paper_info_from_doi(doi=input)
    elif input_type == 'pubmed_id':
        paper_info = api.get_all_data.get_from_pubmed(pubmed_id=input)

    return paper_info
