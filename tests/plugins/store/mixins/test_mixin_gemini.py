# -*- coding: utf-8 -*-


def test_gemini_query(test_db):
    name = 'Chuck Norris Query'
    query_obj = test_db.gemini_query(name)
    assert query_obj.name == name


def test_gemini_queries(test_db):
    query_objs = test_db.gemini_queries()
    assert query_objs.count() == 1


def test_add_gemini_query(test_db):
    name = 'Bruce Lee Query'
    query = "SELECT * FROM variants WHERE 'lee' > 'chuck'"
    new_query = test_db.add_gemini_query(name, query)
    assert isinstance(new_query.id, int)


def test_delete_query(test_db):
    name = 'Chuck Norris Query'
    assert test_db.gemini_query(name)
    test_db.delete_gemini_query(name)
    assert test_db.gemini_query(name) is None
