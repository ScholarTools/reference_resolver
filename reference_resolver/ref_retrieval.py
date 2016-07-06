# Local imports
import database.db_logging as db

import reference_resolver as rr
from scopy import Scopus

api = Scopus()

def retrieve_references(doi):
    try:
        api.bibliography_retrieval.get_from_doi(doi=doi)
    except Exception:
        pass


def retrieve_all_info(input, input_type):
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
        saved_info = db.get_saved_info(input)
        if saved_info is not None:
            saved_info.make_interface_object()
            return saved_info

        paper_info = api.get_all_data.get_from_doi(doi=input)

        if paper_info.references == [] or paper_info.entry == None:
            paper_info = rr.paper_info_from_doi(doi=input)
    elif input_type == 'pubmed_id':
        paper_info = api.get_all_data.get_from_pubmed(pubmed_id=input)

    return paper_info
