# -*- coding: utf-8 -*-
from puzzle.plugins import VcfPlugin

# TODO: define a vcf in the test
vcf = "tests/fixtures/hapmap.vcf"


def test_variants():
    vcf_plugin = VcfPlugin()
    variant = next(vcf_plugin.variants(vcf))
    assert variant['CHROM'] == 'X'
    assert variant['index'] == 1


def test_variant():
    vcf_plugin = VcfPlugin()
    variant = vcf_plugin.variant(vcf, 'X_155239821_G_A')
    assert variant['CHROM'] == 'X'
    assert variant['POS'] == '155239821'

    # get 10th variant
    variant = vcf_plugin.variant(vcf, '3_124998098_C_A')
    assert variant['index'] == 10
