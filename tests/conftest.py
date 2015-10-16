# -*- coding: utf-8 -*-
import pytest

from puzzle.factory import create_app
from puzzle.models import Variant
from puzzle.plugins import VcfPlugin
from puzzle.settings import TestConfig


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
    data = dict(CHROM='1', POS=100, ID='rs01', REF='A', ALT='T', QUAL='100',
                FILTER='PASS')
    variant = Variant(**data)
    return variant
