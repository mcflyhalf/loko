import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from loko.conf import get_configs
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
config = get_configs()

def get_tables_metadata():
	sorted_tables = Base.metadata.sorted_tables
	return sorted_tables

production_engine = create_engine('sqlite:///{dbpath}'.format(\
	dbpath = config['sqlite production db']))

development_engine = create_engine('sqlite:///{dbpath}'.format(\
	dbpath = config['sqlite development db']))

test_engine = create_engine('sqlite:///{dbpath}'.format(\
	dbpath = config['sqlite test db']))

ProductionSession = sessionmaker(bind=production_engine)
production_session = ProductionSession()
DevelopmentSession = sessionmaker(bind=development_engine)
development_session = DevelopmentSession()
TestSession = sessionmaker(bind=test_engine)
test_session = TestSession()

sessions = {}
sessions['test'] = test_session
sessions['development'] = development_session
sessions['production'] = production_session

def get_db_session(env='development'):
	'''
    :param env: session's environment. Can be development, test or production
    :raise ValueError: If env not in ['development', 'test', 'production'] .
    :return: A session instance to the appropriate db
    '''
	#default session
	session = sessions.get(env.lower())

	if session is None:
		raise ValueError("env parameter must be 'development', 'test' or 'production'")

	return session