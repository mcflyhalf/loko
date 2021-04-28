import os
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

development_engine = create_engine('sqlite:///{dbpath}'.format(\
	dbpath = config['sqlite file']))

test_engine = create_engine('sqlite:///{dbpath}'.format(\
	dbpath = config['sqlite file']))

ProductionSession = sessionmaker(bind=production_engine)
production_session = ProductionSession()
DevelopmentSession = sessionmaker(bind=development_engine)
development_session = DevelopmentSession()
TestSession = sessionmaker(bind=test_engine)
test_session = TestSession()

env = os.environ['FLASK_ENV'].lower()

#default session
session = development_session

if env == 'test':
	session=test_session
elif env == 'production':
	session == production_session