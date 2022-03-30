# -*- coding: utf-8 -*-
"""
"""

#Standard
#------------------------
import datetime
import os


# Third party imports
#--------------------------------------
import sqlalchemy as sql
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Local imports
#-------------------------------------
from . import tables

package_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


# SQLite is used to maintain a local database
db_path = os.path.join(package_path,'refs.db')
dialect = 'sqlite:///'

# Combine the dialect and path names to use as params for the engine
engine_params = dialect + db_path

engine = sql.create_engine(engine_params, echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


#============================================================



#from .utils import get_truncated_display_string as td
from . import utils
#from .utils import get_list_class_display as cld

    
class UnknownReference(Base):
    __tablename__ = 'unknown_references'
    
    id = sql.Column(sql.INTEGER, primary_key=True)
    ref_id = sql.Column(sql.INTEGER, sql.ForeignKey('unknown_references.id'))
    
    unknown_text = sql.Column(sql.VARCHAR)
    #If we don't know the reference, put the text here

class Reference(Base):
    """
    This table keeps track of paper references.
    Both 'original_paper' and 'ref_paper' are unique identifying integers. See
    the References table for mapping to information.
    The 'ordering' column keeps track of reference order within a paper.
    """
    __tablename__ = 'references'

    id = sql.Column(sql.INTEGER, primary_key=True)
    main_paper_id = sql.Column(sql.INTEGER, sql.ForeignKey('papers.id'))

    ref_paper_id = sql.Column(sql.INTEGER, sql.ForeignKey('papers.id'),default=-1)
    #Can we have this be -1 if we don't know what it is????
    
    ordering = sql.Column(sql.INTEGER)
    
    def __repr__(self):
        pv = ['id: ', self.id,
              'main_paper_id: ', self.main_paper_id,
              'ref_paper_id: ', self.ref_paper_id,
              'ordering',self.ordering]
        return utils.property_values_to_string(pv)
    
class Paper(Base):
    __tablename__ = 'papers'

    id = sql.Column(sql.INTEGER, primary_key=True)

    doi = sql.Column(sql.VARCHAR)
    pmid = sql.Column(sql.BigInteger)
    isbn = sql.Column(sql.VARCHAR)
    chapter = sql.Column(sql.INTEGER)
    first_page = sql.Column(sql.VARCHAR)
    created = sql.Column(sql.DateTime, default=datetime.datetime.utcnow)
    updated = sql.Column(sql.DateTime, onupdate=datetime.datetime.utcnow)
    #TODO: Need something to indicate that we have added the references
    #- but we might want to know how as well for later verification
    #- as well as when the references were added
    
    new_pointer = sql.Column(sql.BigInteger, default=0)
    #If we ever need to merge duplicates all duplicates will point to a new id

    def __repr__(self):
        pv = ['id: ', self.id,
              'doi: ', self.doi,
              'pmid: ', self.pmid,
              'created',self.created,
              'updated',self.updated,
              'new_pointer',self.new_pointer]
        return utils.property_values_to_string(pv)
    
    @staticmethod
    def create_from_doi(input_doi):
        #populate other properties here as well
        
        #How would we know what other properties to add?
        #e.g. if we add book, we don't need Pubmed
        import pdb
        pdb.set_trace()
        pass
    
    @staticmethod
    def get_from_doi(input_doi):
        #TODO: Option for creating if no exist
        session = Session()
        result = session.query(Paper).filter_by(doi=input_doi)
        obj = result.first()
        return obj
        

