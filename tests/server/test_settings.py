# -*- coding: utf-8 -*-
from puzzle.server.settings import BaseConfig


def test_BaseConfig():
    assert not BaseConfig.DEBUG
