# Third party imports
import sqlalchemy as sql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import types

# Local imports
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
tables.Base.metadata.create_all(engine)

mainentry = session.query(tables.MainPaperInfo).all()
refs = session.query(tables.References).all()
mapping = session.query(tables.RefMapping).all()

import pdb
pdb.set_trace()
