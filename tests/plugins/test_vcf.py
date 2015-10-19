# -*- coding: utf-8 -*-

from puzzle.plugins import VcfPlugin

##TODO define a vcf in the test
vcf = "tests/fixtures/15031.vcf"

def test_variants():
    vcf_plugin = VcfPlugin()
    variant = next(vcf_plugin.variants(vcf))
    assert variant['CHROM'] == 'X'
    assert variant['index'] == 1


def test_variant():
    vcf_plugin = VcfPlugin()
    variant = vcf_plugin.variant(vcf, 'X_132888207_TA_T')
    assert variant['CHROM'] == 'X'
    assert variant['POS'] == '132888207'

    # get 10th variant
    variant = vcf_plugin.variant(vcf, '9_139366460_C_T')
    assert variant['index'] == 10
