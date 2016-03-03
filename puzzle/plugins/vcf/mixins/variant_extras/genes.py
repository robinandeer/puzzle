from puzzle.utils import (get_gene_info, get_gene_symbols)


class GeneExtras(object):
    """Methods for genes"""
    
    def _add_genes(self, variant_obj):
        """Add the gene symbols for a variant"""
        genes = []
        ensembl_ids = []
        hgnc_symbols = []
        
        # if variant_obj.transcripts:
        #     for transcript in variant_obj.transcripts:
        #         if transcript.ensembl_id:
        #             ensembl_ids.append(transcript.ensembl_id)
        #         if transcript.hgnc_symbol:
        #             hgnc_symbols.append(transcript.hgnc_symbol)
        #
        # else:
        chrom = variant_obj.CHROM
        start = variant_obj.start
        stop = variant_obj.stop
        
        hgnc_symbols = get_gene_symbols(chrom, start, stop)
        
        genes = get_gene_info(
                        ensembl_ids=ensembl_ids, 
                        hgnc_symbols=hgnc_symbols
                        )
            
        for gene in genes:
            variant_obj.add_gene(gene)
        