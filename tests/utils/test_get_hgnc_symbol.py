from puzzle.utils import get_hgnc_symbols

def test_get_hgnc_symbols():
    """docstring for test_get_hgnc_symbols"""
    transcripts = [
        {'SYMBOL': 'ADK'}
    ] 
    assert get_hgnc_symbols(transcripts) == set(['ADK'])

def test_get_empty():
    """docstring for test_get_hgnc_symbols"""
    transcripts = []
     
    assert get_hgnc_symbols(transcripts) == set()

def test_get_multiple_hgnc_symbols():
    """docstring for test_get_hgnc_symbols"""
    transcripts = [
        {'SYMBOL': 'ADK'},
        {'SYMBOL': 'TTN'},
        {'SYMBOL': 'ADK'}
    ] 
    assert get_hgnc_symbols(transcripts) == set(['ADK', 'TTN'])
