##TODO mock a gemini db
import pytest
from puzzle.plugins import VcfPlugin

def test_setup_no_file():
    """Test to initialize a gemini database without any file"""

    adapter = VcfPlugin()
    assert adapter.root_path == None
    
    assert adapter.variant_type == 'snv'
    
    assert adapter.filters.can_filter_gene == True
    assert adapter.filters.can_filter_inheritance == True

def test_setup_with_file(vcf_file):
    """Test to initialize a gemini database without any file"""

    adapter = VcfPlugin(root_path=vcf_file)
    assert adapter.root_path == vcf_file

def test_setup_with_dir():
    dir_path = 'tests/fixtures'
    adapter = VcfPlugin(root_path=dir_path)
    assert adapter.root_path == dir_path
