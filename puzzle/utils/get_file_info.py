import logging

from cyvcf2 import VCF
try:
    from gemini import GeminiQuery
except ImportError:
    pass

logger = logging.getLogger(__name__)

def get_file_type(variant_source):
    """Check what kind of file variant source is
    
        Args:
            variant_source (str): Path to variant source
        
        Returns:
            file_type (str): 'vcf', 'gemini' or 'unknown'
    """
    file_type = 'unknown'
    valid_vcf_suffixes = ('.vcf', '.vcf.gz')
    if variant_source:
        logger.debug("Check file type with file: {0}".format(variant_source))
        if variant_source.endswith('.db'):
            file_type = 'gemini'
            logger.debug("File {0} is a gemini database".format(variant_source))
        elif variant_source.endswith(valid_vcf_suffixes):
            file_type = 'vcf'
            logger.debug("File {0} is a vcf".format(variant_source))
        else:
            logger.debug("File is in a unknown format")
    
    return file_type

def get_variant_type(variant_source):
    """Try to find out what type of variants that exists in a variant source
    
        Args:
            variant_source (str): Path to variant source
            source_mode (str): 'vcf' or 'gemini'
        
        Returns:
            variant_type (str): 'sv' or 'snv'
    """
    file_type = get_file_type(variant_source)
    variant_type = 'sv'
    if file_type == 'vcf':
        variants = VCF(variant_source)
    elif file_type == 'gemini':
        variants = GeminiQuery(variant_source)
        gemini_query = "SELECT * from variants"
        variants.run(gemini_query)
    # Check 1000 first variants, if anyone is a snv we set the variant_type
    # to 'snv'
    for i,variant in enumerate(variants):
        if file_type == 'vcf':
            if variant.is_snp:
                variant_type = 'snv'
        elif file_type == 'gemini':
            if variant['type'] == 'snp':
                variant_type = 'snv'
            
        if i > 1000:
            break
    
    return variant_type
                    
            
    
