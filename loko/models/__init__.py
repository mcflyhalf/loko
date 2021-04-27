from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from loko import get_configs
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
config = get_configs()

def get_tables_metadata():
	sorted_tables = Base.metadata.sorted_tables
	return sorted_tables

production_engine = create_engine('sqlite:///{dbpath}'.format(\
	dbpath = config['sqlite file']))
