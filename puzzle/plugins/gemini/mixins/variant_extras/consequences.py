import logging

logger = logging.getLogger(__name__)

class ConsequenceExtras(object):
    """Methods to handle consequences"""
    
    def _add_consequences(self, variant_obj):
        """Add the consequences found in all transcripts

        Args:
            variant_obj (puzzle.models.Variant)
        """

        consequences = set()
        for transcript in variant_obj.transcripts:
            for consequence in transcript.consequence.split('&'):
                consequences.add(consequence)

        variant_obj.consequences = list(consequences)
    
    def _add_most_severe_consequence(self, variant_obj, gemini_variant):
        """Add the most severe consequence
        
        Args:
            variant_obj (puzzle.models.Variant)
            gemini_variant (GeminiQueryRow)
        """
        variant_obj.most_severe_consequence = gemini_variant['impact_so']

    def _add_impact_severity(self, variant_obj, gemini_variant):
        """Add the impact severity for the most severe consequence
        
            Args:
                variant_obj (puzzle.models.Variant)
                gemini_variant (GeminiQueryRow)
        """
        gemini_impact = gemini_variant['impact_severity']
        if gemini_impact == 'MED':
            gemini_impact = 'MEDIUM'
        variant_obj.impact_severity = gemini_impact
