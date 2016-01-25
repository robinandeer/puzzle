# -*- coding: utf-8 -*-


def test_set_up(test_session):
    assert test_session.dialect == 'sqlite'
