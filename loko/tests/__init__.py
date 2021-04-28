import pytest
from loko.models import get_db_session
from loko import LokoConfig, get_logger

logger = get_logger('loko_test')

@pytest.fixture(scope='session')
def test_session():
	session = get_db_session(env='test')
	engine = session.get_bind()
	lokoconfig = LokoConfig(engine, logger)
	lokoconfig.newconfig(engine, drop_tables=True)

	return session