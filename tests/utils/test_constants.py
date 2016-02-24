from puzzle.utils.constants import HGNC_TO_OMIM, SEVERITY_DICT

def test_HGNC_TO_OMIM():
    assert HGNC_TO_OMIM['CACNA1F'].get('mim_nr') == 300110
    assert HGNC_TO_OMIM['ADK'].get('mim_nr') == 102750

def test_SEVERITY_DICT():
    assert SEVERITY_DICT['transcript_ablation'] == 0
    assert SEVERITY_DICT['start_lost'] == 6
