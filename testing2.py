#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JAH: Current status - working on adding 
"""

#Step 1
#------------------------------
from reference_resolver import tables

session = tables.Session()

doi='10.1002/biot.201400046'

#TODO:
#p1 = tables.Paper.create_from_pmid(pmid)
#p2 = tables.Paper.create_from_doi(doi)

p1 = tables.Paper(pmid=4200)
p2 = tables.Paper(doi=doi)
session.add(p1)
session.add(p2)

session.commit()
session.close()


wtf = tables.Paper.from_doi(doi)

    #if __name__ == "__main__":
    #engine = create_engine('sqlite:///C:/Users/RNEL/Desktop/temp/wtf.db')
    # Bind the engine to the metadata of the Base class so that the
    # declaratives can be accessed through a DBSession instance
    #Base.metadata.create_all(engine)
    #Base.metadata.bind = engine
     
    #tables.Base.metadata.create_all(engine)
    #Session = sessionmaker(bind=engine)    
     
    #session = Session(engine)
     
     
    #DBSession = sessionmaker(bind=engine)
    # A DBSession() instance establishes all conversations with the database
    # and represents a "staging zone" for all the objects loaded into the
    # database session object. Any change made against the objects in the
    # session won't be persisted into the database until you call
    # session.commit(). If you're not happy about the changes, you can
    # revert all of them back to the last commit by calling
    # session.rollback()
    #session = DBSession()
     
    """
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
    """


