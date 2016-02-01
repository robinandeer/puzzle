from puzzle.utils import get_most_severe_consequence

def test_get_most_severe():
    """docstring for test_get_most_severe"""
    transcripts = [
        {'consequence': 'transcript_ablation'}
    ]
    
    assert get_most_severe_consequence(transcripts) == 'transcript_ablation'

def test_get_most_severe_no_transcripts():
    """docstring for test_get_most_severe"""
    transcripts = []
    
    assert get_most_severe_consequence(transcripts) == None

def test_get_most_severe_unknown_consequence():
    """docstring for test_get_most_severe"""
    transcripts = [
        {'consequence': 'unknown'}
    ]
    
    assert get_most_severe_consequence(transcripts) == None

def test_get_most_severe_multiple_transcripts():
    """docstring for test_get_most_severe"""
    transcripts = [
        {'consequence': 'inframe_deletion'},
        {'consequence': 'start_lost'},
        {'consequence': 'synonymous_variant'}
    ]
    
    assert get_most_severe_consequence(transcripts) == 'start_lost'

def test_get_most_severe_multiple_annotations():
    """docstring for test_get_most_severe"""
    transcripts = [
        {'consequence': 'start_lost&synonymous_variant'},
    ]
    
    assert get_most_severe_consequence(transcripts) == 'start_lost'
