from puzzle.utils import get_most_severe_consequence

def test_get_most_severe():
    """docstring for test_get_most_severe"""
    transcripts = [
        {'Consequence': 'transcript_ablation'}
    ]
    
    assert get_most_severe_consequence(transcripts) == 'transcript_ablation'

def test_get_most_severe_no_transcripts():
    """docstring for test_get_most_severe"""
    transcripts = []
    
    assert get_most_severe_consequence(transcripts) == None

def test_get_most_severe_unknown_consequence():
    """docstring for test_get_most_severe"""
    transcripts = [
        {'Consequence': 'unknown'}
    ]
    
    assert get_most_severe_consequence(transcripts) == None

def test_get_most_severe_multiple_transcripts():
    """docstring for test_get_most_severe"""
    transcripts = [
        {'Consequence': 'inframe_deletion'},
        {'Consequence': 'start_lost'},
        {'Consequence': 'synonymous_variant'}
    ]
    
    assert get_most_severe_consequence(transcripts) == 'start_lost'
