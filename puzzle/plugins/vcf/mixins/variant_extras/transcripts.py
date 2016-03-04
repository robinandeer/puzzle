from vcftoolbox import (get_vep_info, get_snpeff_info)

from puzzle.models import (Transcript)


class TranscriptExtras(object):
    """Collect the methods that deals with transcripts"""
    
    def _add_transcripts(self, variant_obj, info_dict):
        """Return all transcripts sound in the vcf file"""
        vep_string = info_dict.get('CSQ')

        #Check if snpeff annotation:
        snpeff_string = info_dict.get('ANN')
        
        # We check one of these.
        # VEP has presedence over snpeff
        if vep_string:
            #Get the vep annotations
            vep_info = get_vep_info(
                vep_string = vep_string,
                vep_header = self.vep_header
                )
            for transcript_info in vep_info:
                transcript = self._get_vep_transcript(transcript_info)
                variant_obj.add_transcript(transcript)

        elif snpeff_string:
            #Get the vep annotations
            snpeff_info = get_snpeff_info(
                snpeff_string = snpeff_string,
                snpeff_header = self.snpeff_header
                )
            for transcript_info in snpeff_info:
                transcript = self._get_snpeff_transcript(transcript_info)
                variant_obj.add_transcript(transcript)

    
    def _get_vep_transcript(self, transcript_info):
        """Create a Transcript based on the vep annotation

            Args:
                transcript_info (dict): A dict with vep info

            Returns:
                transcript (puzzle.models.Transcript): A Transcripts
        """
        transcript = Transcript(
                hgnc_symbol = transcript_info.get('SYMBOL'),
                transcript_id = transcript_info.get('Feature'),
                ensembl_id = transcript_info.get('Gene'),
                biotype = transcript_info.get('BIOTYPE'),
                consequence = transcript_info.get('Consequence'),
                strand = transcript_info.get('STRAND'),
                sift = transcript_info.get('SIFT'),
                polyphen = transcript_info.get('PolyPhen'),
                exon = transcript_info.get('EXON'),
                HGVSc = transcript_info.get('HGVSc'),
                HGVSp = transcript_info.get('HGVSp'),
                GMAF = transcript_info.get('GMAF'),
                ExAC_MAF = transcript_info.get('ExAC_MAF')
            )
        return transcript

    def _get_snpeff_transcript(self, transcript_info):
        """Create a transcript based on the snpeff annotation

            Args:
                transcript_info (dict): A dict with snpeff info

            Returns:
                transcript (puzzle.models.Transcript): A Transcripts
        """
        transcript = Transcript(
                hgnc_symbol = transcript_info.get('Gene_Name'),
                transcript_id = transcript_info.get('Feature'),
                ensembl_id = transcript_info.get('Gene_ID'),
                biotype = transcript_info.get('Transcript_BioType'),
                consequence = transcript_info.get('Annotation'),
                exon = transcript_info.get('Rank'),
                HGVSc = transcript_info.get('HGVS.c'),
                HGVSp = transcript_info.get('HGVS.p')
            )
        return transcript
    