# -*- coding: utf-8 -*-
import pytest
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from puzzle.factory import create_app
from puzzle.models import Variant
from puzzle.models.sql import BASE
from puzzle.plugins import VcfPlugin
from puzzle.settings import TestConfig

from puzzle.log import configure_stream

root_logger = configure_stream()
logger = logging.getLogger(__name__)

@pytest.fixture
def app(request):
    app = create_app(config_obj=TestConfig)
    return app


@pytest.fixture
def vcf():
    db = VcfPlugin()
    return db


@pytest.fixture
def variant():
    """Return a variant dictionary"""
    data = dict(CHROM='1', POS='100', ID='rs01', REF='A', ALT='T', QUAL='100',
                FILTER='PASS')
    variant = Variant(**data)
    return variant

@pytest.fixture(scope='session')
def session(request):
    """Create and return a session to a sqlite database"""
    engine = create_engine("sqlite:///:memory:")
    connection = engine.connect()
    
    session = sessionmaker()
    session.configure(bind=engine)
    BASE.metadata.create_all(engine)
    
    s = session()
    
    def teardown():
        print('\n')
        logger.info("Teardown sqlite database")
        s.close()
        connection.close()
    request.addfinalizer(teardown)
    
    return s