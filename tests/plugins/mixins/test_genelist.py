# -*- coding: utf-8 -*-


def test_gene_list(test_db):
    list_obj = test_db.gene_list('test-list')
    assert list_obj.gene_ids == ['ADK', 'KRAS', 'DIABLO']
    assert list_obj.cases[0].case_id == '636808'


def test_gene_lists(test_db):
    list_objs = test_db.gene_lists()
    assert list_objs.count() == 1


def test_add_genelist(test_db):
    list_id = 'Bruce Lee List'
    gene_ids = ['EGFR', 'PID']
    assert test_db.gene_lists().count() == 1
    new_list = test_db.add_genelist(list_id, gene_ids)
    assert isinstance(new_list.id, int)
    assert new_list.list_id == list_id
    assert test_db.gene_lists().count() == 2


def test_remove_genelist(test_db):
    list_id = 'test-list'
    assert test_db.gene_lists().count() == 1
    test_db.remove_genelist(list_id)
    assert test_db.gene_lists().count() == 0


def test_case_genelist(test_db):
    case_obj = test_db.case('636808')
    list_obj = test_db.case_genelist(case_obj)
    assert list_obj.list_id == "{}-HPO".format(case_obj.case_id)
