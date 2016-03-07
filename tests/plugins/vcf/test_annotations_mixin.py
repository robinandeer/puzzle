# -*- coding: utf-8 -*-
from puzzle.plugins import VcfPlugin

def test_add_compounds(variant):
    plugin = VcfPlugin()
    info_dict = {
        'Compounds': "643594:11_120999413_G_A>24|11_120988038_T_G>23|11_120991571_G_A>10|11_121028581_C_G>36"
    }
    plugin._add_compounds(variant, info_dict)
    compounds = variant.compounds
    highest_scored_compound = compounds[0]
    assert int(highest_scored_compound.combined_score) == 36

def test_add_compounds_no_compounds(variant):
    plugin = VcfPlugin()
    info_dict = {}
    plugin._add_compounds(variant, info_dict)
    assert variant.compounds == []
    