# Third party imports
import sqlalchemy as sql
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# TODO: figure out the best way to assign unique IDs to papers without collisions
class RefMapping(Base):
    """
    This table keeps track of paper references.
    Both 'original_paper' and 'ref_paper' are unique identifying integers. See
    the References table for mapping to information.
    The 'ordering' column keeps track of reference order within a paper.
    """
    __tablename__ = 'ref_mapping'

    id = sql.Column(sql.INTEGER, primary_key=True)
    main_paper_id = sql.Column(sql.INTEGER)
    ref_paper_id = sql.Column(sql.INTEGER)
    ordering = sql.Column(sql.INTEGER)

    def __repr__(self):
        return "<RefMapping(\noriginal_paper='%d', \nref_paper='%d'\n)>" % (self.original_paper, self.ref_paper)


class MainPaperInfo(Base):
    __tablename__ = 'main_paper_info'

    id = sql.Column(sql.INTEGER, primary_key=True)
    ref_table_id = sql.Column(sql.INTEGER)

    doi = sql.Column(sql.VARCHAR)
    doi_prefix = sql.Column(sql.VARCHAR)
    title = sql.Column(sql.VARCHAR)
    publication = sql.Column(sql.VARCHAR)
    date = sql.Column(sql.VARCHAR)
    year = sql.Column(sql.VARCHAR)
    volume = sql.Column(sql.VARCHAR)
    issue = sql.Column(sql.VARCHAR)
    pages = sql.Column(sql.VARCHAR)
    keywords = sql.Column(sql.VARCHAR)
    abstract = sql.Column(sql.VARCHAR)
    affiliations = sql.Column(sql.VARCHAR)
    url = sql.Column(sql.VARCHAR)
    pdf_link = sql.Column(sql.VARCHAR)
    scraper_obj = sql.Column(sql.VARCHAR)
    contact_info = sql.Column(sql.VARCHAR)
    authors = sql.Column(sql.VARCHAR)


class References(Base):
    __tablename__ = 'references'

    id = sql.Column(sql.INTEGER, primary_key=True)
    main_table_id = sql.Column(sql.INTEGER)

    # Initialize standard reference information
    ref_id = sql.Column(sql.INTEGER)
    title = sql.Column(sql.VARCHAR)
    authors = sql.Column(sql.VARCHAR)
    publication = sql.Column(sql.VARCHAR)
    volume = sql.Column(sql.VARCHAR)
    issue = sql.Column(sql.VARCHAR)
    series = sql.Column(sql.VARCHAR)
    date = sql.Column(sql.VARCHAR)
    pages = sql.Column(sql.VARCHAR)
    doi = sql.Column(sql.VARCHAR)
    pii = sql.Column(sql.VARCHAR)
    citation = sql.Column(sql.VARCHAR)

    # Initialize all possible external links
    crossref = sql.Column(sql.VARCHAR)
    pubmed = sql.Column(sql.VARCHAR)
    pubmed_central = sql.Column(sql.VARCHAR)
    cas = sql.Column(sql.VARCHAR)
    isi = sql.Column(sql.VARCHAR)
    ads = sql.Column(sql.VARCHAR)
    scopus_link = sql.Column(sql.VARCHAR)
    pdf_link = sql.Column(sql.VARCHAR)
    scopus_cite_count = sql.Column(sql.VARCHAR)
    aps_full_text = sql.Column(sql.VARCHAR)

    # Make a timestamp
    timestamp = sql.Column(sql.TIMESTAMP)
