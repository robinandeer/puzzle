from . import SEVERITY_DICT


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
