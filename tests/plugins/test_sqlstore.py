# -*- coding: utf-8 -*-


def test_set_up(sql_store):
    assert sql_store.dialect == 'sqlite'


def test_add_case(sql_store, case_obj):
    sql_store.add_case(case_obj)
    case = sql_store.case(case_obj['case_id'])
    assert case and case.case_id == case_obj['case_id']
