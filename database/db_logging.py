# Standard
import datetime

# Third party imports
import sqlalchemy as sql

# Local imports
from reference_resolver.rr_errors import *
import database.db_tables as tables
from database import Session
from pypub.paper_info import PaperInfo
from pypub.scrapers.base_objects import *

def get_saved_info(doi):
    # Start a new Session
    session = Session()

    # Get papers with the requested DOI
    # This should only be 1
    main_results = session.query(tables.MainPaperInfo).filter_by(doi=doi).all()
    if len(main_results) > 1:
        raise DatabaseError('Multiple papers with the same DOI found')
    elif len(main_results) == 0:
        return None

    main_paper = main_results[0]
    main_id = main_paper.id

    # Get author information
    authors = session.query(tables.Authors).filter_by(main_paper_id=main_id).all()

    # Get references for the main paper
    refs = session.query(tables.References).join(tables.RefMapping).\
        filter(tables.RefMapping.main_paper_id == main_id).all()

    # Make into a PaperInfo object
    saved_paper_info = _create_paper_info_from_saved(main_paper=main_paper, authors=authors, refs=refs)

    # Close Session
    session.close()

    return saved_paper_info


def log_info(paper_info):
    # Start a new Session
    session = Session()

    doi = paper_info.doi.lower()

    # Check if the DOI is already in the main paper database
    existing_doi = session.query(tables.MainPaperInfo).filter_by(doi=doi).all()
    if len(existing_doi) > 0:
        return
        #raise DatabaseError('Paper already exists in database')

    # Create entry for main paper table
    main_entry = _create_entry_table_obj(paper_info)

    # Check if this paper has already been referenced and is in the references table
    ref_table_id = _fetch_id(session=session, table_name=tables.References, doi=doi, title=main_entry.title)

    main_entry.ref_table_id = ref_table_id

    # Add main entry to the table
    session.add(main_entry)

    # Get primary key for main entry
    session.flush()
    session.refresh(main_entry)
    main_paper_id = main_entry.id

    # Add author information to author database
    entry = paper_info.entry
    if entry is not None:
        for a in entry.get('authors'):
            db_author_entry = _create_author_table_obj(main_paper_id=main_paper_id, author=a)
            session.add(db_author_entry)

    # Add each reference to the references table
    refs = paper_info.references
    ref_list = []
    for ref in refs:
        db_ref_entry = _create_ref_table_obj(ref)
        main_table_id = _fetch_id(session=session, table_name=tables.MainPaperInfo, doi=db_ref_entry.doi,
                                  title=db_ref_entry.title)
        db_ref_entry.main_table_id = main_table_id
        ref_list.append(db_ref_entry)
        session.add(db_ref_entry)

    session.flush()

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

    _end(session)


def delete_info(doi):
    """
    Note that this will rarely be used and is mainly for debugging
        and manual database management reasons. Even if a user opts to
        delete a document from his/her Mendeley library, the information
        will not be deleted from the database in case it is to be
        retrieved again later.
    """
    session = Session()

    matching_entries = session.query(tables.MainPaperInfo).filter_by(doi = doi).all()
    ids = []
    for entry in matching_entries:
        ids.append(entry.id)
        session.delete(entry)

    for id in ids:
        refs = session.query(tables.References).join(tables.RefMapping).\
            filter(tables.RefMapping.main_paper_id == id).all()
        for ref in refs:
            session.delete(ref)
        entry_map = session.query(tables.RefMapping).filter_by(main_paper_id = id).all()
        for map in entry_map:
            session.delete(map)


    import pdb
    pdb.set_trace()

    _end(session)


def update_reference_field(identifying_value, updating_field, updating_value, filter_by_title=False, filter_by_doi=False):
    session = Session()
    if filter_by_title:
        entries = session.query(tables.References).filter_by(title = identifying_value).all()
    elif filter_by_doi:
        entries = session.query(tables.References).filter_by(doi = identifying_value).all()
    else:
        _end(session)
        return

    for entry in entries:
        setattr(entry, updating_field, updating_value)

    _end(session)


def _create_entry_table_obj(paper_info):
    entry = paper_info.entry

    # Format some of the entry data
    keywords = entry.get('keywords')
    if entry.get('keywords') is not None:
        keywords = ', '.join(entry.get('keywords'))

    db_entry = tables.MainPaperInfo(
        # Get attributes of the paper_info.entry field
        title = entry.get('title'),
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


def _create_author_table_obj(main_paper_id, author):
    affs = author.get('affiliations')
    affiliations = None
    if affs is not None:
        if isinstance(affs, list):
            affiliations = '; '.join(affs)
        else:
            affiliations = affs

    db_author_entry = tables.Authors(
        main_paper_id = main_paper_id,
        name = author.get('name'),
        affiliations = affiliations,
        email = author.get('email')
    )
    return db_author_entry


def _fetch_id(session, table_name, doi, title):
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


def _create_paper_info_from_saved(main_paper, authors, refs):
    """
    Parameters
    ----------
    main_paper : list of tables.Paper objects
    authors : list of tables.Authors objects
    refs : list of tables.References objects

    Returns
    -------

    """
    saved_info = PaperInfo()

    # Create entry information and PaperInfo attributes
    entry_obj = BaseEntry()
    md = main_paper.__dict__
    for k, v in md.items():
        if k == '_sa_instance_state':
            pass
        elif k == 'doi':
            setattr(saved_info, k, v)
            setattr(entry_obj, k, v)
        elif k in ('doi_prefix', 'url', 'pdf_link', 'scraper_obj'):
            setattr(saved_info, k, v)
        else:
            setattr(entry_obj, k, v)

    # Get authors
    author_list = []
    for author in authors:
        a = BaseAuthor()
        a.name = author.name
        a.affiliations = author.affiliations
        a.email = author.email
        author_list.append(a)

    # Add author_list to entry_obj, then add entry to saved_info
    entry_obj.authors = author_list
    saved_info.entry = entry_obj

    # Create references list
    references = []
    for ref in refs:
        rd = ref.__dict__
        rd['authors'] = rd['authors'].split(', ')
        ref_obj = BaseRef()
        for k, v in rd.items():
            if k not in ('timestamp', '_sa_instance_state'):
                setattr(ref_obj, k, v)
        references.append(ref_obj)
    saved_info.references = references

    return saved_info


def _end(session):
    # Commit and close the session
    try:
        session.commit()
    except:
        session.rollback()
        raise DatabaseError('Error encountered while committing to database. '
                            'Most recent information may not have been saved.')
    finally:
        session.close()
