##TODO mock a gemini db
import pytest
from puzzle.plugins import VcfPlugin

def test_setup_no_file():
    """Test to initialize a gemini database without any file"""

    adapter = VcfPlugin()
    
    assert adapter.variant_type == 'snv'
    
    assert adapter.filters.can_filter_gene == True
    assert adapter.filters.can_filter_inheritance == True

def test_setup_variant_type():
    """docstring for test_setup_variant_type"""
    adapter = VcfPlugin('sv')
    
    assert adapter.variant_type == 'sv'
