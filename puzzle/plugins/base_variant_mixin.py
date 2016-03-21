from puzzle.utils import (get_gene_info, get_cytoband_coord)


class BaseVariantMixin(object):
    """Base class for variant mixins"""
    
    def variants(self, case_id, skip=0, count=30, filters=None):
        """Return a results tuple with variants and nr_of_variants.

        """
        raise NotImplementedError

    def variant(self, variant_id):
        """Return a specific variant."""
        raise NotImplementedError
    
    def _get_genes(self, variant):
        """Add the genes for a variant

        Get the hgnc symbols from all transcripts and add them
        to the variant

        Args:
            variant (dict): A variant dictionary

        Returns:
            genes (list): A list of Genes
        """
        ensembl_ids = []
        hgnc_symbols = []
        
        for transcript in variant.transcripts:
            if transcript.ensembl_id:
                ensembl_ids.append(transcript.ensembl_id)
            if transcript.hgnc_symbol:
                hgnc_symbols.append(transcript.hgnc_symbol)
        
        genes = get_gene_info(
                        ensembl_ids=ensembl_ids, 
                        hgnc_symbols=hgnc_symbols
                        )
        return genes
    
    def _add_sv_coordinates(self, variant):
        """Add the neccesary sv coordinates for a variant
        
        Args:
            variant (puzzle.models.variant)
        """
        variant.stop_chrom = variant.CHROM
        variant.start = int(variant.POS)
        
        # If we have a translocation:
        if ':' in variant.ALT:
            other_coordinates = variant.ALT.strip('ACGTN[]').split(':')
            variant.stop_chrom = other_coordinates[0].lstrip('chrCHR')
            other_position = other_coordinates[1]
            # variant.stop = other_position

            #Set 'infinity' to length if translocation
            variant.sv_len = float('inf')
            variant.sv_type = 'BND'
        else:
            variant.sv_len = variant.stop - variant.start

        variant['cytoband_start'] = get_cytoband_coord(
                                        chrom=variant.CHROM,
                                        pos=variant.start
                                        )

        variant['cytoband_stop'] = get_cytoband_coord(
                                    chrom=variant.stop_chrom,
                                    pos=variant.stop
                                    )
