from puzzle.utils import (get_file_type, get_variant_type)

def test_get_file_type_vcf(vcf_file):
    file_type = get_file_type(vcf_file)
    assert file_type == 'vcf'

def test_get_file_type_compressed_vcf(compressed_vcf_file):
    file_type = get_file_type(compressed_vcf_file)
    assert file_type == 'vcf'

def test_get_file_type_gemini(gemini_path):
    file_type = get_file_type(gemini_path)
    assert file_type == 'gemini'

def test_get_file_type_unknown():
    path = 'hello'
    file_type = get_file_type(path)
    assert file_type == 'unknown'

def test_get_variant_type_snv_vcf(vcf_file):
    variant_type = get_variant_type(variant_source=vcf_file)
    assert variant_type == 'snv'

def test_get_variant_type_sv_vcf(vcf_file_sv):
    variant_type = get_variant_type(variant_source=vcf_file_sv)
    assert variant_type == 'sv'

def test_get_variant_type_snv_gemini(gemini_path):
    variant_type = get_variant_type(variant_source=gemini_path)
    assert variant_type == 'snv'
