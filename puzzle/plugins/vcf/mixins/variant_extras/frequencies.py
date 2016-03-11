import logging

logger = logging.getLogger(__name__)

class FrequenciesExtras(object):
    """Methods for adding frequencies"""
    
    def _add_thousand_g(self, variant_obj, info_dict):
        """Add the thousand genomes frequency
        
        Args:
            variant_obj (puzzle.models.Variant)
            info_dict (dict): A info dictionary
        
        """
        thousand_g = info_dict.get('1000GAF')
        if thousand_g:
            logger.debug("Updating thousand_g to: {0}".format(
                thousand_g))
            variant_obj.thousand_g = float(thousand_g)
            variant_obj.add_frequency('1000GAF', variant_obj.get('thousand_g'))
    
    def _add_gmaf(self, variant_obj, info_dict):
        """Add the gmaf frequency
        
        Args:
            variant_obj (puzzle.models.Variant)
            info_dict (dict): A info dictionary
        
        """
        ##TODO search for max freq in info dict
        for transcript in variant_obj.transcripts:
            gmaf_raw = transcript.GMAF
            if gmaf_raw:
                gmaf = float(gmaf_raw.split(':')[-1])
                variant_obj.add_frequency('GMAF', gmaf)
                
                if not variant_obj.thousand_g:
                    variant_obj.thousand_g = gmaf
    
    def _add_exac(self, variant_obj, info_dict):
        """Add the gmaf frequency
        
        Args:
            variant_obj (puzzle.models.Variant)
            info_dict (dict): A info dictionary
        
        """
        exac = None
        exac_keys = ['ExAC', 'EXAC', 'ExACAF', 'EXACAF']
        for key in exac_keys:
            if info_dict.get(key):
                exac = float(info_dict[key])
        #If not found in vcf search transcripts
        if not exac:
            for transcript in variant_obj.transcripts:
                exac_raw = transcript.ExAC_MAF
                if exac_raw:
                    exac = float(exac_raw.split(':')[-1])
        
        if exac:
            variant_obj.add_frequency('ExAC', exac)
    