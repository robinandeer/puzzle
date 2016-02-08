"""Test al functionalities of the Utils module"""

from puzzle.utils import get_most_severe_consequence, get_cytoband_coord

class TestGetInfo():
    """Test get_info submodule"""

    def test_get_most_severe_consequence(self):
        """Test get_most_sever_consequence(transcripts) method"""

        print "Test get_most_sever_consequence with a 'regular' transcripts list"
        transcripts = [
            {'consequence': 'transcript_ablation'}
        ]
        assert get_most_severe_consequence(transcripts) == 'transcript_ablation'

        print "Test get_most_sever_consequence with empty transcripts list"
        transcripts = []
        assert get_most_severe_consequence(transcripts) == None

        print "Test get_most_sever_consequence with 'unknown' consequence"
        transcripts = [
            {'consequence': 'unknown'}
        ]
        assert get_most_severe_consequence(transcripts) == None

        print "Test most_severe_consequence with multiple transcripts"
        transcripts = [
            {'consequence': 'inframe_deletion'},
            {'consequence': 'start_lost'},
            {'consequence': 'synonymous_variant'}
        ]
        assert get_most_severe_consequence(transcripts) == 'start_lost'

        print "Test most_severe_consequence with multiple transcripts (annotations)"
        transcripts = [
            {'consequence': 'start_lost&synonymous_variant'},
        ]
        assert get_most_severe_consequence(transcripts) == 'start_lost'


    def test_get_cytoband_coord(self):
        """test get_cytoband_coord(chrom, pos) method"""

        print "Test get_cytoband_coord with different input formats"
        assert get_cytoband_coord('1', 3) == '1p36.33'
        assert get_cytoband_coord('chr1', 3)  == '1p36.33'
        assert get_cytoband_coord('chr1', '3') == '1p36.33'

        print "Test get_cytoband_coord with non existing chromosome"
        assert get_cytoband_coord('chrMT', '3') == None

        print "Test get_cytoband_coord with non existing position"
        assert get_cytoband_coord('chrX', '155270600') == None
