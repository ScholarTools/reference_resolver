# Third party imports
import sqlalchemy as sql
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class RefMapping(Base):
    """
    This table keeps track of paper references.
    Both 'original_paper' and 'ref_paper' are unique identifying integers. See
    the References table for mapping to information.
    The 'ordering' column keeps track of reference order within a paper.
    """
    __tablename__ = 'ref_mapping'

    id = sql.Column(sql.INTEGER, primary_key=True)
    main_paper_id = sql.Column(sql.INTEGER, sql.ForeignKey('main_paper_info.id'))
    ref_paper_id = sql.Column(sql.INTEGER, sql.ForeignKey('references.id'))
    ordering = sql.Column(sql.INTEGER)

    def __repr__(self):
        return "<RefMapping(original_paper='%d', ref_paper='%d')>" % (self.main_paper_id, self.ref_paper_id)


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
    url = sql.Column(sql.VARCHAR)
    pdf_link = sql.Column(sql.VARCHAR)
    scraper_obj = sql.Column(sql.VARCHAR)

    def __repr__(self):
        return u'' + \
        '      title: %s\n' % self.title + \
        '   keywords: %s\n' % self.keywords + \
        'publication: %s\n' % self.publication + \
        '       date: %s\n' % self.date + \
        '        year %s\n' % self.year + \
        '     volume: %s\n' % self.volume + \
        '      issue: %s\n' % self.issue + \
        '      pages: %s\n' % self.pages + \
        '        doi: %s\n' % self.doi + \
        '         url %s\n' % self.url + \
        '    pdf_link %s\n' % self.pdf_link


class Authors(Base):
    __tablename__ = 'authors'

    id = sql.Column(sql.INTEGER, primary_key=True)
    main_paper_id = sql.Column(sql.INTEGER, sql.ForeignKey('main_paper_info.id'))
    name = sql.Column(sql.VARCHAR)
    affiliations = sql.Column(sql.VARCHAR)
    email = sql.Column(sql.VARCHAR)


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

    def __repr__(self):
        return u'' + \
        '     ref_id: %s\n' % self.ref_id + \
        '      title: %s\n' % self.title + \
        '    authors: %s\n' % self.authors + \
        'publication: %s\n' % self.publication + \
        '     volume: %s\n' % self.volume + \
        '      issue: %s\n' % self.issue + \
        '     series: %s\n' % self.series + \
        '       date: %s\n' % self.date + \
        '      pages: %s\n' % self.pages + \
        '        doi: %s\n' % self.doi + \
        '        pii: %s\n' % self.pii


class LinkedNotes(Base):
    __tablename__ = "linked_notes"

    id = sql.Column(sql.INTEGER, primary_key=True)
    main_paper_id = sql.Column(sql.INTEGER, sql.ForeignKey('main_paper_info.id'))
    ref_paper_id = sql.Column(sql.INTEGER, sql.ForeignKey('references.id'))
    notes = sql.Column(sql.VARCHAR)

