import logging

from puzzle.utils.constants import (SO_TERMS, IMPACT_SEVERITIES, SEVERITY_DICT)

logger = logging.getLogger(__name__)

class ConsequenceExtras(object):
    """Methods to handle consequences"""
    
    def _add_consequences(self, variant_obj, raw_variant_line):
        """Add the consequences found for a variant

            Args:
                variant_obj (puzzle.models.Variant)
                raw_variant_line (str): A raw vcf variant line
        """
        consequences = []
        for consequence in SO_TERMS:
            if consequence in raw_variant_line:
                consequences.append(consequence)
        
        variant_obj.consequences = consequences
    
    def _add_most_severe_consequence(self, variant_obj):
        """Add the most severe consequence
        
        Args:
            variant_obj (puzzle.models.Variant)
            
        """
        most_severe_consequence = None
        most_severe_score = None

        for consequence in variant_obj.consequences:
            logger.debug("Checking severity score for consequence: {0}".format(
                consequence))
            
            severity_score = SEVERITY_DICT.get(consequence)
            
            if severity_score != None:
                if most_severe_score:
                    if severity_score < most_severe_score:
                        most_severe_consequence = consequence
                        most_severe_score = severity_score
                else:
                    most_severe_consequence = consequence
                    most_severe_score = severity_score

        variant_obj.most_severe_consequence = most_severe_consequence

    def _add_impact_severity(self, variant_obj):
        """Add the impact severity for the most severe consequence
        
            Args:
                variant_obj (puzzle.models.Variant)
        
        """
        if variant_obj.most_severe_consequence:
            variant_obj.impact_severity = IMPACT_SEVERITIES.get(
                variant_obj.most_severe_consequence
            )
