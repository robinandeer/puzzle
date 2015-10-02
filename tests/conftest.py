# -*- coding: utf-8 -*-
import pytest

from puzzle.factory import create_app
from puzzle.plugins import VcfPlugin
from puzzle.settings import TestConfig


@pytest.fixture
def app(request):
    app = create_app(config_obj=TestConfig)
    return app


@pytest.fixture
def vcf():
    db = VcfPlugin(TestConfig.PUZZLE_VCF_FILE)
    return db
