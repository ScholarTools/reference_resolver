# Third party
import sqlalchemy as sql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import types

# Local
from reference_resolver import main as rr
import database.db_tables as tables
from database import Session

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
references = paper_info.references
#print(refs)
#print(len(refs))

session = Session()

mainentry = session.query(tables.MainPaperInfo).all()
refs = session.query(tables.References).all()
mapping = session.query(tables.RefMapping).all()

import pdb
pdb.set_trace()
