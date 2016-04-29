from puzzle.utils.gemini_extras import (add_to_query, build_gemini_query)

def test_add_to_query():
    query = "SELECT * from variants"
    extra_info = "max_aaf_all < 0.01"
    new_query = add_to_query(query, extra_info)
    assert new_query == "SELECT * from variants WHERE max_aaf_all < 0.01"

    extra_info = "cadd_score > 10"
    new_query = add_to_query(new_query, extra_info)
    assert new_query == "SELECT * from variants WHERE max_aaf_all < 0.01 AND cadd_score > 10"

def test_build_gemini_query():
    filters = {
        'frequency' : 0.01
    }
    query = build_gemini_query(filters)
    
    assert query == "SELECT * from variants WHERE (max_aaf_all < 0.01 or max_aaf_all is Null)"

def test_build_gemini_query_models():
    filters = {
        'frequency' : 0.01
    }
    query = build_gemini_query(filters, add_where = False)
    
    assert query == "(max_aaf_all < 0.01 or max_aaf_all is Null)"

def test_build_gemini_query_models_two():
    filters = {
        'frequency' : 0.01,
        'cadd' : 15.0
    }
    query = build_gemini_query(filters, add_where = False)
    
    assert query == "(max_aaf_all < 0.01 or max_aaf_all is Null) AND (cadd_scaled > 15.0)"