# Third party imports
import sqlalchemy as sql
from sqlalchemy.orm import sessionmaker

# Local imports
import database.db_tables as tables

engine = sql.create_engine('sqlite:///papers.db', echo=False)
tables.Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

from database.db_logging import update_reference_field
