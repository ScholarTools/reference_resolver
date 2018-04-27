# -*- coding: utf-8 -*-
"""
"""

import datetime

from sqlalchemy import create_engine
import sqlalchemy as sql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session


from reference_resolver.utils import get_truncated_display_string as td
from reference_resolver import utils
#from .utils import get_list_class_display as cld

Base = declarative_base()
    
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
    
    unknown_text = sql.Column(sql.VARCHAR)
    #If we don't know the reference, put the text here
    

    def __repr__(self):
        pv = ['id: ', self.id,
              'main_paper_id: ', self.main_paper_id,
              'ref_paper_id: ', self.ref_paper_id,
              'ordering',self.ordering,
              'unknown_text',td(self.unknown_text)]
        return utils.property_values_to_string(pv)
    
    
    #    return "<RefMapping(original_paper='%d', ref_paper='%d')>" % (self.main_paper_id, self.ref_paper_id)

class Paper(Base):
    __tablename__ = 'papers'

    id = sql.Column(sql.INTEGER, primary_key=True)

    doi = sql.Column(sql.VARCHAR)
    pmid = sql.Column(sql.BigInteger)
    created = sql.Column(sql.DateTime, default=datetime.datetime.utcnow)
    updated = sql.Column(sql.DateTime, onupdate=datetime.datetime.utcnow)
    
    new_pointer = sql.Column(sql.BigInteger, default=0)
    #If we ever need to merge duplicates all duplicates will point to a new id
        
    
    #doi_prefix = sql.Column(sql.VARCHAR)
    #title = sql.Column(sql.VARCHAR)
    #publication = sql.Column(sql.VARCHAR)
    #date = sql.Column(sql.VARCHAR)
    #syear = sql.Column(sql.VARCHAR)
    
    
    #----------
    #date_created
    #date_updated
    #new_pointer - 0 - 
    #is_unknown_type - raw text that can't be identified

if __name__ == "__main__":
      
    
    engine = create_engine('sqlite:///C:/Users/RNEL/Desktop/temp/wtf.db')
    # Bind the engine to the metadata of the Base class so that the
    # declaratives can be accessed through a DBSession instance
    Base.metadata.create_all(engine)
    #Base.metadata.bind = engine
     
    #tables.Base.metadata.create_all(engine)
    #Session = sessionmaker(bind=engine)    
     
    session = Session(engine)
     
     
    #DBSession = sessionmaker(bind=engine)
    # A DBSession() instance establishes all conversations with the database
    # and represents a "staging zone" for all the objects loaded into the
    # database session object. Any change made against the objects in the
    # session won't be persisted into the database until you call
    # session.commit(). If you're not happy about the changes, you can
    # revert all of them back to the last commit by calling
    # session.rollback()
    #session = DBSession()
     
    # Insert a Person in the person table
    for i in range(100):
        new_paper = Paper(pmid=i+1)
        session.add(new_paper)
        
    for i in range(10):
        ref = Reference(main_paper_id=10,ref_paper_id=i)  
        session.add(ref)
    
    session.commit()
    
    import pdb
    pdb.set_trace()
    
    wtf = session.query(Paper).filter_by(pmid=10)
    wtf = session.query(Reference).filter_by(main_paper_id=10)
    
    session.close()
    #wtf.count()
    #wtf2 = wtf.first()
    
    
    #
    
    # Insert an Address in the address table
    #new_address = Address(post_code='00000', person=new_person)
    #session.add(new_address)
    #session.commit()
