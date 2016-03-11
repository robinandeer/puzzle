# -*- coding: utf-8 -*-
from puzzle.plugins import VcfPlugin


def test_set_up(sql_store):
    assert sql_store.dialect == 'sqlite'


def test_select_plugin(test_db, case_obj):
    plugin, case_id = test_db.select_plugin(case_obj)
    assert isinstance(plugin, VcfPlugin)
    assert case_id == case_obj.case_id
