import logging

logger = logging.getLogger(__name__)

class FrequenciesExtras(object):
    """Methods for adding frequencies"""
    
    def _add_thousand_g(self, variant_obj, gemini_variant):
        """Add the thousand genomes frequency
        
        Args:
            variant_obj (puzzle.models.Variant)
            gemini_variant (GeminiQueryRow)
        """
        
        thousand_g = gemini_variant['aaf_1kg_all']
        if thousand_g:
            logger.debug("Updating thousand_g to: {0}".format(
                thousand_g))
            variant_obj.thousand_g = float(thousand_g)
            variant_obj.add_frequency('1000GAF', variant_obj.get('thousand_g'))
    
    def _add_gmaf(self, variant_obj, gemini_variant):
        """Add the gmaf frequency
        
        Args:
            variant_obj (puzzle.models.Variant)
            gemini_variant (GeminiQueryRow)
        
        """
        max_af = gemini_variant['max_aaf_all']
        if max_af:
            max_af = float(max_af)
            if max_af != -1.0:
                variant_obj.set_max_freq(max_af)

    def _add_exac(self, variant_obj, gemini_variant):
        """Add the gmaf frequency
        
        Args:
            variant_obj (puzzle.models.Variant)
            gemini_variant (GeminiQueryRow)        
        """
        exac = gemini_variant['aaf_exac_all']
        if exac:
            exac = float(exac)
            variant_obj.add_frequency('ExAC', exac)
            logger.debug("Updating ExAC to: {0}".format(
                exac))
    