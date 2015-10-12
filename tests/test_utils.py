# -*- coding: utf-8 -*-
from puzzle.utils import (get_most_severe_consequence, get_hgnc_symbols,
                          get_omim_number)


def test_get_omim_number():
    assert get_omim_number('MCCRP2') == 605031
    assert get_omim_number('IFT172') == 607386
