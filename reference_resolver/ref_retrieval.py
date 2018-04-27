# Local imports
#import database.db_logging as db

#JAH: Why are we reaching back to the root?
import reference_resolver as rr

#What is this for????? - can we make this optional?????
from scopy import Scopus

scopus_api = Scopus()

#Why just this one function in this module??????

def retrieve_references(doi):
    """
    This retrieves references from online sources.
    This is to be used when a paper is in a user's library
    but the references have not been retrieved and connected
    to the paper in the database.

    """

    if doi is None:
        return None

    try:
        refs = scopus_api.bibliography_retrieval.get_from_doi(doi=doi)
    except LookupError or ConnectionRefusedError or ConnectionError:
        refs = None
        pass

    if refs is None or len(refs) == 0:
        paper_info = rr.doi_to_webscraped_info(doi=doi, refs_only=True)
        refs = paper_info.references

    return refs
