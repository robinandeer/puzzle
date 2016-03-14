from puzzle.models import (Transcript)
from gemini import GeminiQuery


class TranscriptExtras(object):
    """Collect the methods that deals with transcripts"""

    def _add_transcripts(self, variant_obj, gemini_variant):
        """
        Add all transcripts for a variant

        Go through all transcripts found for the variant

            Args:
                gemini_variant (GeminiQueryRow): The gemini variant

            Yields:
                transcript (puzzle.models.Transcript)

        """
        query = "SELECT * from variant_impacts WHERE variant_id = {0}".format(
            gemini_variant['variant_id']
        )

        gq = GeminiQuery(self.db)
        gq.run(query)
        
        for gemini_transcript in gq:
            transcript = Transcript(
                hgnc_symbol=gemini_transcript['gene'],
                transcript_id=gemini_transcript['transcript'],
                consequence=gemini_transcript['impact_so'],
                biotype=gemini_transcript['biotype'],
                polyphen=gemini_transcript['polyphen_pred'],
                sift=gemini_transcript['sift_pred'],
                HGVSc=gemini_transcript['codon_change'],
                HGVSp=', '.join([gemini_transcript['aa_change'] or '', gemini_transcript['aa_length'] or ''])
                )
            variant_obj.add_transcript(transcript)

