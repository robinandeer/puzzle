# -*- coding: utf-8 -*-
from puzzle.models.case import Case


def test_Case():
    # with explicit name
    case_obj = Case('sample1', name='Oscar Wilde')
    assert case_obj.case_id == 'sample1'
    assert case_obj.name == 'Oscar Wilde'

    # without name
    case_obj = Case('sample2')
    assert case_obj.case_id == case_obj.name == 'sample2'
