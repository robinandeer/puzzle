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

def test_add_cadd_score(variant):
    plugin = VcfPlugin()
    info_dict = {'CADD': '24'}
    plugin._add_cadd_score(variant, info_dict)
    
    assert float(variant.cadd_score) == 24.0

def test_add_cadd_score_no_score(variant):
    plugin = VcfPlugin()
    info_dict = {}
    plugin._add_cadd_score(variant, info_dict)
    
    assert variant.cadd_score == None

def test_add_genetic_models(variant):
    plugin = VcfPlugin()
    info_dict = {'GeneticModels': '643594:AD_dn|AR_comp_dn'}
    plugin._add_genetic_models(variant, info_dict)
    
    assert set(variant.genetic_models) == set(['AD_dn', 'AR_comp_dn'])

def test_add_genetic_models_no_models(variant):
    plugin = VcfPlugin()
    info_dict = {}
    plugin._add_genetic_models(variant, info_dict)
    
    assert variant.genetic_models == []

def test_add_rank_score(variant):
    plugin = VcfPlugin()
    info_dict = {'RankScore': '643594:24'}
    plugin._add_rank_score(variant, info_dict)
    
    assert int(variant.rank_score) == 24

def test_add_rank_score_no_score(variant):
    plugin = VcfPlugin()
    info_dict = {}
    plugin._add_rank_score(variant, info_dict)
    
    assert variant.rank_score == None
