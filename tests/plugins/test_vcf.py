# -*- coding: utf-8 -*-


# def test_variants(vcf):
#     variant = next(vcf.variants())
#     assert variant['CHROM'] == 'X'
#     assert variant['index'] == 1
#
#
# def test_variant(vcf):
#     variant = vcf.variant('X_84563218_C_G')
#     assert variant['CHROM'] == 'X'
#     assert variant['POS'] == '84563218'
#
#     # get 10th variant
#     variant = vcf.variant('3_124998098_C_A')
#     assert variant['index'] == 10
