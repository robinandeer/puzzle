# -*- coding: utf-8 -*-


def test_add_phenotype(test_db, phenomizer_auth):
    # setup phenomizer auth
    test_db.phenomizer_auth = phenomizer_auth

    ind_id = 'ADM1059A2'
    ind_obj = test_db.individual(ind_id)

    hpo_id = 'HP:0002497'
    added_terms = test_db.add_phenotype(ind_obj, hpo_id)

    assert len(added_terms) == 1
    assert len(ind_obj.phenotypes) == 1

    term_obj = ind_obj.phenotypes[0]
    assert term_obj.phenotype_id == hpo_id
    assert term_obj.description == 'Spastic ataxia'
    assert term_obj.individual.ind_id == ind_id

    # test with a missing HPO id
    hpo_id = 'HP:0000118'
    assert test_db.add_phenotype(ind_obj, hpo_id) is None

    # test with a repeated HPO id
    hpo_id = 'HP:0002497'
    assert test_db.add_phenotype(ind_obj, hpo_id) == []

    # test adding with OMIM id
    omim_id = 'OMIM:615862'
    hpo_ids = ['HP:0000092', 'HP:0006580', 'HP:0000090', 'HP:0000238',
               'HP:0001249', 'HP:0001970', 'HP:0004722', 'HP:0000486',
               'HP:0003774', 'HP:0001396']
    added_terms = test_db.add_phenotype(ind_obj, omim_id)
    added_ids = [term.phenotype_id for term in added_terms]
    assert set(added_ids) == set(hpo_ids)
    assert len(ind_obj.phenotypes) == len(hpo_ids) + 1


def test_remove_phenotype(test_db, phenomizer_auth):
    # setup phenomizer auth
    test_db.phenomizer_auth = phenomizer_auth

    ind_id = 'ADM1059A2'
    ind_obj = test_db.individual(ind_id)

    hpo_id = 'HP:0002497'
    removed_hpo_id = 'HP:0006580'
    test_db.add_phenotype(ind_obj, hpo_id)
    test_db.add_phenotype(ind_obj, removed_hpo_id)

    assert len(ind_obj.phenotypes) == 2
    test_db.remove_phenotype(ind_obj, removed_hpo_id)
    assert len(ind_obj.phenotypes) == 1
    assert ind_obj.phenotypes[0].phenotype_id == hpo_id

    # test resetting the phenotypes for an individual
    test_db.remove_phenotype(ind_obj)
    assert len(ind_obj.phenotypes) == 0
