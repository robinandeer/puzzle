from .constants import SEVERITY_DICT, HGNC_TO_OMIM


def get_most_severe_consequence(transcripts):
    """Get the most severe consequence

        Go through all transcripts and get the most severe consequence

        Args:
            transcripts (list): A list of transcripts to evaluate

        Returns:
            most_severe_consequence (str): The most severe consequence
    """
    most_severe_consequence = None
    most_severe_score = None

    for transcript in transcripts:
        for consequence in transcript['Consequence'].split('&'):
            severity_score = SEVERITY_DICT.get(
                consequence
            )
            if most_severe_score:
                if severity_score < most_severe_score:
                    most_severe_consequence = consequence
                    most_severe_score = severity_score
            else:
                most_severe_consequence = consequence
                most_severe_score = severity_score

    return most_severe_consequence


def get_hgnc_symbols(transcripts):
    """Get the hgnc symbols

        Go through all transcripts and get hgnc symbols

        Args:
            transcripts (list): A list of transcripts to evaluate

        Returns:
            hgnc_symbols (list): The hgnc symbols
    """

    hgnc_symbols = set()
    for transcript in transcripts:
        hgnc_symbol = transcript['SYMBOL']

        if hgnc_symbol:
            hgnc_symbols.add(hgnc_symbol)

    return hgnc_symbols


def get_omim_number(hgnc_symbol):
    """Get the omim number for a hgnc symbol

        Args:
            hgnc_symbol (str): A hgnc symbol

        Returns:
            omim_number (int): The omim number
    """
    
    hgnc=HGNC_TO_OMIM.get(hgnc_symbol)
    
    if hgnc is not None:
        omim_number = hgnc.get('mim_nr')
    else:
        omim_number = None

    return omim_number

def get_ensembl_id(hgnc_symbol):
    """Get the ensembl id for a hgnc symbol

        Args:
            hgnc_symbol (str): A hgnc symbol

        Returns:
            ensembl_id (int): The ensembl id
    """
    hgnc = HGNC_TO_OMIM.get(hgnc_symbol)

    if hgnc is not None:
        ensembl_id = hgnc.get('ensembl_id')
    else:
        ensembl_id = None

    return ensembl_id
