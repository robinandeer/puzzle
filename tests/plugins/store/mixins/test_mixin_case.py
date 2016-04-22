# -*- coding: utf-8 -*-


def test_add_case(sql_store, case_obj):
    sql_store.add_case(case_obj)
    case = sql_store.case(case_obj['case_id'])
    assert case and case.case_id == case_obj['case_id']


def test_delete_case(test_db):
    case_obj = test_db.case('636808')
    test_db.delete_case(case_obj)

    empty_case = test_db.case('636808')
    assert empty_case is None


def test_delete_individual(test_db):
    # GIVEN: a single case in the database
    case_obj = test_db.cases().all()[0]

    # WHEN: the case is delete
    test_db.delete_case(case_obj)

    # THEN: no cases are left in the database
    assert test_db.cases().count() == 0


def test_case(test_db):
    # GIVEN: a case "636808" in the database
    case_obj = test_db.case('636808')

    # WHEN: -

    # THEN: the returned case has case_id: "636808"
    assert case_obj.case_id == '636808'


def test_individual(test_db):
    # GIVEN: an individual "ADM1059A1" in the database
    ind_obj = test_db.individual('ADM1059A1')

    # WHEN: -

    # THEN: the returned case has ind_id: "ADM1059A1"
    assert ind_obj.ind_id == 'ADM1059A1'
    assert ind_obj.cases[0].case_id == '636808'


def test_cases(test_db):
    # GIVEN: a single case in the database
    cases_query = test_db.cases()

    # THEN: fetching all cases should return one object as a list
    assert cases_query.count() == 1


def test_get_individuals(test_db):
    # GIVEN: a case with three individuals in the database
    individuals = test_db.individuals()

    # THEN: fetching individuals returns three records
    assert individuals.count() == 3

    # WHEN: passing in two ind ids
    ind_ids = [ind.ind_id for ind in individuals]
    sub_inds = test_db.individuals(ind_ids=ind_ids[:2])

    # THEN: ... it returns two records matching the ids
    assert sub_inds.count() == 2
    assert [ind.ind_id for ind in sub_inds] == ind_ids[:2]
