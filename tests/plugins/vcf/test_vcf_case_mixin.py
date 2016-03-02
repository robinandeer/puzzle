from puzzle.plugins import VcfPlugin

def test_ped_info(vcf_file, ped_lines):
    adapter=VcfPlugin(root_path=vcf_file, case_lines=ped_lines, case_type='ped')
    assert len(adapter.individuals) == 3
    case_obj = adapter.case_objs[0]
    assert case_obj.name == "636808"

def test_vcf_case(vcf_file):
    adapter=VcfPlugin(root_path=vcf_file)
    assert len(adapter.individuals) == 3
    case_obj = adapter.case_objs[0]
    assert case_obj['name'] == 'hapmap.vcf'

def test_vcf_case_dir(root_path):
    adapter=VcfPlugin(root_path=root_path)
    assert len(adapter.case_objs) == 3
