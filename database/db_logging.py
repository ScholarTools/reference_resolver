# Standard
import datetime

# Third party imports
import sqlalchemy as sql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import types

# Local imports
from reference_resolver.rr_errors import *
import database.db_tables as tables

# TODO: put this somewhere/organize this better
engine = sql.create_engine('sqlite:///papers.db', echo=True)

# Note on Sessions: http://docs.sqlalchemy.org/en/latest/orm/session_basics.html#session-faq-whentocreate
Session = sessionmaker(bind=engine)
session = Session()

# Create the tables
# So far this includes (ClassName (table_name))
#   RefMapping (ref_mapping)
#   References (references)
#   MainPaperInfo (main_paper_info)
tables.Base.metadata.create_all(engine)


# TODO: Update this whole function
# Fetch the information from each table and return an object
def get_saved_info(doi):
    # Start a new Session
    session = Session()

    # Get papers with the requested DOI
    # This should only be 1
    results = session.query(tables.MainPaperInfo).filter_by(doi=doi).all()
    if len(results) > 1:
        raise DatabaseError('Multiple papers with the same DOI found')

    # Close Session
    session.close()

    # TODO: update this
    # Make sure there is only one returned
    if len(results) == 1:
        return results[0]
    else:
        return None


def log_info(paper_info):
    # Start a new Session
    session = Session()

    doi = paper_info.doi

    # Check if the DOI is already in the main paper database
    existing_doi = session.query(tables.MainPaperInfo).filter_by(doi=doi).all()
    if len(existing_doi) > 0:
        raise DatabaseError('Paper already exists in database')

    # Create entry for main paper table
    main_entry = _create_entry_table_obj(paper_info)

    # Check if this paper has already been referenced and is in the references table
    ref_table_id = _fetch_id(tables.References, doi=doi, title=main_entry.title)

    main_entry.ref_table_id = ref_table_id

    # Add main entry to the table
    session.add(main_entry)

    # Add each reference to the references table
    refs = paper_info.references
    ref_list = []
    for ref in refs:
        db_ref_entry = _create_ref_table_obj(ref)
        main_table_id = _fetch_id(tables.MainPaperInfo, doi=db_ref_entry.doi, title=db_ref_entry.title)
        db_ref_entry.main_table_id = main_table_id
        ref_list.append(db_ref_entry)
        session.add(db_ref_entry)

    session.refresh(main_entry)

    main_paper_id = main_entry.id

    # Refresh the session so that the primary keys can be retrieved
    # Then extract the IDs
    ref_id_list = []
    for ref in ref_list:
        session.refresh(ref)
        ref_id_list.append(ref.id)

    order = 1
    for ref_id in ref_id_list:
        db_map_obj = _create_mapping_table_obj(main_paper_id, ref_id, order)
        session.add(db_map_obj)
        order += 1

    # Flush and close the session
    session.flush()
    session.close()


def _create_entry_table_obj(paper_info):
    entry = paper_info.entry

    # Format some of the entry data
    keywords = entry.get('keywords')
    if entry.get('keywords') is not None:
        keywords = ', '.join(entry.get('keywords'))

    author_list = entry.get('authors')
    author_names = []
    affiliations = []
    contact_info = None
    for author in author_list:
        if author.get('email') is not None:
            contact_info = author.get('email')
        author_names.append(author.get('name'))
        affs = author.get('affiliations')
        if affs is not None:
            for a in affs:
                if a not in affiliations:
                    affiliations.append(a)

    db_entry = tables.MainPaperInfo(
        # Get attributes of the paper_info.entry field
        title = entry.get('title'),
        authors = ', '.join(author_names),
        affiliations = '; '.join(affiliations),
        contact_info = contact_info,
        keywords = keywords,
        publication = entry.get('publication'),
        date = entry.get('date'),
        volume = entry.get('volume'),
        pages = entry.get('pages'),
        doi = entry.get('doi'),
        abstract = entry.get('abstract'),

        # Get attributes of the general paper_info object
        doi_prefix = paper_info.doi_prefix,
        url = paper_info.url,
        pdf_link = paper_info.pdf_link,
        scraper_obj = paper_info.scraper_obj,

        # Save the ID of the corresponding paper entry in references table
        ref_table_id = None
    )
    return db_entry


def _create_ref_table_obj(ref):
    db_ref_entry = tables.References(
            # Get standard ref information
            ref_id = ref.get('ref_id'),
            title = ref.get('title'),
            authors = ref.get('authors'),
            publication = ref.get('publication'),
            volume = ref.get('volume'),
            issue = ref.get('issue'),
            series = ref.get('series'),
            date = ref.get('date'),
            pages = ref.get('pages'),
            doi = ref.get('doi'),
            pii = ref.get('pii'),
            citation = ref.get('citation'),

            # Get all possible external links
            crossref = ref.get('crossref'),
            pubmed = ref.get('pubmed'),
            pubmed_central = ref.get('pubmed_central'),
            cas = ref.get('cas'),
            isi = ref.get('isi'),
            ads = ref.get('ads'),
            scopus_link = ref.get('scopus_link'),
            pdf_link = ref.get('pdf_link'),
            scopus_cite_count = ref.get('scopus_cite_count'),
            aps_full_text = ref.get('aps_full_text'),

            # Make a timestamp
            timestamp = datetime.datetime.utcnow()
    )

    # Fix author list
    if isinstance(db_ref_entry.authors, list):
        db_ref_entry.authors = ', '.join(db_ref_entry.authors)

    return db_ref_entry


def _create_mapping_table_obj(main_paper_id, ref_paper_id, ordering):
    db_map_entry = tables.RefMapping(
        main_paper_id = main_paper_id,
        ref_paper_id = ref_paper_id,
        ordering = ordering
    )
    return db_map_entry


def _fetch_id(table_name, doi, title):
    """
    For a given paper, it looks to see if it already exists in a table
    'table_name' and if so, returns the primary key of its entry in that table.

    Parameters
    ----------
    table_name : Base object (from db_tables.py)
        The table in the database that will be queried.
    doi : str
        Paper DOI
    title : str
        Paper title

    Returns
    -------
    primary_id : int
        Primary key of the entry corresponding to 'doi' and/or 'title' within
         'table_name'
    """
    doi_check = session.query(table_name).filter_by(doi=doi).all()
    if len(doi_check) == 0:
        title_check = session.query(table_name).filter_by(title=title).all()
        if len(title_check) == 0:
            primary_id = None
        else:
            primary_id = title_check[0].id
    else:
        primary_id = doi_check[0].id

    return primary_id
