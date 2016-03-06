import logging

logger = logging.getLogger(__name__)

def get_csq(description):
    """Get the csq columns
    
        Args:
            description (str): The vcf header description string
        
        Returns:
            csq_cols (list): The CSQ colums
    """
    csq_description = description.split(':')[1][1:-1]
    csq_cols = csq_description.split('|')
    return csq_cols
