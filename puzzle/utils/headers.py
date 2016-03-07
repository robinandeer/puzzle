import logging

from vcftoolbox import (HeaderParser, get_vcf_handle)

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

def get_header(vcf_file_path):
    """Parse the header and return a header object

        Args:
            vcf_file_path(str): Path to vcf

        Returns:
            head: A HeaderParser object
    """
    logger.info("Parsing header of file {0}".format(vcf_file_path))
    head = HeaderParser()
    handle = get_vcf_handle(infile=vcf_file_path)
    # Parse the header
    for line in handle:
        line = line.rstrip()
        if line.startswith('#'):
            if line.startswith('##'):
                head.parse_meta_data(line)
            else:
                head.parse_header_line(line)
        else:
            break

    handle.close()

    return head
