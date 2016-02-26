# -*- coding: utf-8 -*-


def test_variants(test_db):
    # WHEN: there are some variants in the database for a case (vcf)

    # THEN: fetching variants for that case returnes a list of variant objs
    variant_objs = list(test_db.variants('636808'))
    assert len(variant_objs) > 0
    assert variant_objs[0].start == 879537

    # WHEN: skipping the first 10 variants
    variant_objs = list(test_db.variants('636808', skip=10))

    # THEN: the first variant is the 11 overall
    assert variant_objs[0].start == 76154073

    # WHEN: limiting the variants to 10 overall
    variant_objs = list(test_db.variants('636808', count=10))

    # THEN: the the length of variants list is 10
    assert len(variant_objs) == 10


def test_variant(test_db):
    # WHEN: fetching variant
    case_id = '636808'
    variant_id = '1_880086_T_C'
    variant_obj = test_db.variant(case_id, variant_id)

    # THEN: variant with position '880086' is returned
    assert variant_obj.start == 880086
