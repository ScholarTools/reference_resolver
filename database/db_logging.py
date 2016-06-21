# Standard
import random

# Third party imports
import sqlalchemy as sql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import types

# Local imports
from reference_resolver.rr_errors import *
import database.db_tables as tables

# TODO: put this somewhere/organize this better
engine = sql.create_engine('sqlite:///:memory:', echo=True)

# Note on Sessions: http://docs.sqlalchemy.org/en/latest/orm/session_basics.html#session-faq-whentocreate
Session = sessionmaker(bind=engine)
session = Session()

# Create the tables
# So far this includes (ClassName (table_name))
#   RefMapping (ref_mapping)
#   References (references)
tables.Base.metadata.create_all(engine)


def get_saved_info(doi):
    # Start a new Session
    session = Session()

    # Get papers with the requested DOI
    # This should only be 1
    results = session.query(tables.References).filter_by(doi=doi).all()

    # Make sure there is only one returned
    if len(results) > 1:
        raise DatabaseError('Multiple papers with the same DOI found')

    paper = results[0]


# TODOs:
#   Check if the main paper from paper_intro (i.e. paper_info.entry) already exists in the database.
#       If it doesn't, then add it.
#   Decide what the best way would be to maintain the two tables and their relationships.
#       Currently, I'm assigning a random integer between 1-1000000 to use as an ID. Jim suggested using the
#       auto-incrementing ID assigned by the References table to use as the ID, which would work. (Thought: what
#       happens when an entry is removed from the database? If entry 1 is removed, do the rest shift up so there
#       is a new entry #1, or do they retain their old primary key numbers and there just is never again an entry
#       #1? Look into this; that behavior would kill the usability of the primary key in the other table.) In any
#       case, figure out how to either hang on to the random assigned IDs as the entries are being added, or
#       quickly flush to the database, query it for the primary keys, and use those in the other table. The goal is
#       to be able to set up the second table that holds on to which references map to which original paper.
def log_info(paper_info):
    # Start a new Session
    session = Session()

    refs = paper_info.references
    for ref in refs:
        db_entry = _create_table_entry(ref)
        session.add(db_entry)


def _create_table_entry(ref):
    paper_id = assign_id()

    db_entry = tables.References(
            paper_id=paper_id,
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
            timestamp = types.TIMESTAMP
        )

    return db_entry


# TODO: figure out a better system for this
def assign_id():
    paper_id = random.randint(1, 1000000)
    return paper_id
