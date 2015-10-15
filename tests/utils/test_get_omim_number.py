# -*- coding: utf-8 -*-
from puzzle.utils import (get_omim_number)


def test_get_omim_number():
    assert get_omim_number('IFT172') == 607386

def test_get_non_existing_omim():
    assert get_omim_number('HEJ') == None

def test_get_phenotype():
    assert get_omim_number('MCCRP2') != get_omim_number('PLK4')
    assert get_omim_number('MCCRP2') == None
    assert get_omim_number('PLK4') == 605031

# def test_get_specific():
#     """docstring for test_get_specific"""
#     assert get_omim_number('DDX11L1') == 605031
    