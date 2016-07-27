# Local imports
import database.db_logging as db

import reference_resolver as rr
from scopy import Scopus

scopus_api = Scopus()


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
                if len(saved_info.references) > 0:
                    saved_info.make_interface_object()
                    return saved_info
                else:
                    saved_info.references = retrieve_references(saved_info.doi)
                    # These lines probably don't belong in this function. This is for the case in which
                    # a paper's information has already been saved in the database, but has no corresponding
                    # references. This saves the references after having retrieved them.
                    if saved_info.references is not None and len(saved_info.references) > 0:
                        for ref in paper_info.references:
                            db.add_reference(ref=ref, main_paper_doi=paper_info.doi.lower(),
                                             main_paper_title=getattr(paper_info.entry, 'title', None))
                    else:
                        return saved_info

        try:
            # This next line fetches information from Scopus
            paper_info = scopus_api.get_all_data.get_from_doi(doi=input)
        except LookupError or ConnectionRefusedError or ConnectionError:
            # If Scopus could not connect or info wasn't found there,
            # this line attempts to web-scrape from a publisher site.
            paper_info = rr.paper_info_from_doi(doi=input, skip_saved=True)

    elif input_type == 'pubmed_id':
        paper_info = scopus_api.get_all_data.get_from_pubmed(pubmed_id=input)

    return paper_info
