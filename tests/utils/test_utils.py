"""Test al functionalities of the Utils module"""
from puzzle.utils import get_most_severe_consequence

class TestGetInfo():
    """Test get_info submodule"""

    def test_get_most_severe():
        """Get most sever consequence"""
        transcripts = [
            {'consequence': 'transcript_ablation'}
        ]

        assert get_most_severe_consequence(transcripts) == 'transcript_ablation'

    def test_get_most_severe_no_transcripts():
        """Get most sever consequence (empty transcrpts list)"""
        transcripts = []

        assert get_most_severe_consequence(transcripts) == None

    def test_get_most_severe_unknown_consequence():
        """Get most severe consequence ('unknown' consequence)"""
        transcripts = [
            {'consequence': 'unknown'}
        ]

        assert get_most_severe_consequence(transcripts) == None

    def test_get_most_severe_multiple_transcripts():
        """Get most severe consequence of multiple transcripts"""
        transcripts = [
            {'consequence': 'inframe_deletion'},
            {'consequence': 'start_lost'},
            {'consequence': 'synonymous_variant'}
        ]

        assert get_most_severe_consequence(transcripts) == 'start_lost'

    def test_get_most_severe_multiple_annotations():
        """Get most sever consequence of multiple transcripts (annotations)"""
        transcripts = [
            {'consequence': 'start_lost&synonymous_variant'},
        ]

        assert get_most_severe_consequence(transcripts) == 'start_lost'
