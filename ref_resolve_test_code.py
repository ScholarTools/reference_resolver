# Third party
import sqlalchemy as sql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import types

# Local
from reference_resolver import reference_resolver as rr
import database.db_tables as tables

citation = 'Senís, Elena, et al. "CRISPR/Cas9‐mediated genome engineering: An adeno‐associated viral (AAV) vector ' + \
           'toolbox. Biotechnology journal 9.11 (2014): 1402-1412.'

link = 'http://onlinelibrary.wiley.com/doi/10.1002/biot.201400046/references'

doi = '10.1002/biot.201400046'

#paper_info = rr.resolve_citation(citation)
#print(paper_info['entry'])
#print(paper_info['references'][0])
#print(paper_info.keys())

#paper_info = rr.resolve_doi(doi)

#doi = '10.1038/nrg3686'

paper_info = rr.resolve_doi(doi)
refs = paper_info.references
print(refs)
print(len(refs))

engine = sql.create_engine('sqlite:///papers.db', echo=True)

# Note on Sessions: http://docs.sqlalchemy.org/en/latest/orm/session_basics.html#session-faq-whentocreate
Session = sessionmaker(bind=engine)
session = Session()

tables.Base.metadata.create_all(engine)

mainentry = session.query(tables.MainPaperInfo).all()
refs = session.query(tables.References).all()
mapping = session.query(tables.RefMapping).all()


import pdb
pdb.set_trace()
