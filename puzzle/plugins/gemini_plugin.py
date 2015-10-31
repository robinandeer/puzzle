# -*- coding: utf-8 -*-
import logging
from sqlite3 import OperationalError

from gemini import GeminiQuery
from puzzle.plugins import Plugin
from puzzle.models import (Variant, Genotype, Gene, Transcript, Case)
from puzzle.utils import (get_omim_number, get_ensembl_id, get_hgnc_symbols,
                          get_most_severe_consequence)
from puzzle.exceptions import DatabaseError

logger = logging.getLogger(__name__)

class GeminiPlugin(Plugin):
    """This is the base class for puzzle plugins"""

    def __init__(self):
        super(GeminiPlugin, self).__init__()

    def init_app(self, app):
        """Initialize plugin via Flask."""
        logger.debug("Updating root path to {0}".format(
            app.config['PUZZLE_ROOT']
        ))
        self.root_path = app.config['PUZZLE_ROOT']
        logger.debug("Updating pattern to {0}".format(
            app.config['PUZZLE_PATTERN']
        ))
        self.pattern = app.config['PUZZLE_PATTERN']
    
    def cases(self, pattern=None):
        """Return all cases."""
        db = pattern or self.root_path
        logger.debug("Looking for cases in {0}".format(
            db
        ))
        cases = set()
        
        gq = GeminiQuery(db)
        query = "SELECT * from samples"
        gq.run(query)
    
        for individual in gq:
            logger.debug("Found individual  {0}".format(individual['name']))
            cases.add(individual['family_id'])
        
        logger.debug("Found cases {0}".format(', '.join(cases)))
        case_objs = (Case(case_id=db.replace('/', '|'),
                          name = case) for case in cases)
        
        return case_objs

    def _get_individuals(self, gemini_variant, sample2idx):
        """Add the genotypes for all individuals
        
            Args:
                gemini_variant (GeminiQueryRow): The gemini variant
                sample2idx (dict): A dictionary with sample_ids: index
            
            Returns:
                individuals (list) A list of Genotypes
        """
        individuals = []
        for sample_id in sample2idx:
            index = sample2idx[sample_id]
            individuals.append(Genotype(
                sample_id=sample_id, 
                genotype=gemini_variant['gts'][index], 
                ref_depth=gemini_variant['gt_ref_depths'][index], 
                alt_depth=gemini_variant['gt_alt_depths'][index],
                depth=gemini_variant['gt_depths'][index],
                genotype_quality=gemini_variant['gt_quals'][index]
            ))
        
        return individuals
    
    def _get_genes(self, variant):
        """Add the genes for a variant
        
            Get the hgnc symbols from all transcripts and add them 
            to the variant
            
            Args:
                variant (dict): A variant dictionary
            
            Returns:
                genes (list): A list of Genes
        """
        genes = []
        hgnc_symbols = get_hgnc_symbols(
            transcripts = variant['transcripts']
        )
        for hgnc_id in hgnc_symbols:
            genes.append(Gene(
                symbol=hgnc_id,
                omim_number=get_omim_number(hgnc_id),
                ensembl_id=get_ensembl_id(hgnc_id)
                )
            )
        return genes
    
    def _get_transcripts(self, gemini_variant, gemini_db):
        """Return a Transcript object
            
            Gemini stores the information for the most severe transcript
            so only one transcript is connected to one variant.
            
            Args:
                gemini_variant (GeminiQueryRow): The gemini variant
                gemini_db (str): Path to gemini db
            
            Returns:
                transcripts list: List of affected transcripts
        
        """
        query = "SELECT * from variant_impacts WHERE variant_id = {0}".format(
            gemini_variant['variant_id']
        )
        gq = GeminiQuery(gemini_db)
        gq.run(query)
        
        transcripts = []
        for transcript in gq:
            transcripts.append(Transcript(
                SYMBOL=transcript['gene'], 
                Feature=transcript['transcript'], 
                Consequence=transcript['impact_so'],
                BIOTYPE=transcript['biotype'],
                PolyPhen=transcript['polyphen_pred'],
                SIFT=transcript['sift_pred'],
                HGVSc = transcript['codon_change'],
                HGVSp = transcript['aa_change']
                
                )
            )
        return transcripts

    def _variants(self, gemini_db, gemini_query=None):
        """Return variants found in the gemini database"""
        try:
            gq = GeminiQuery(gemini_db)
        except OperationalError as e:
            message = "{0} is not a valid gemini db".format(gemini_db)
            logger.error(message)
            raise DatabaseError(message)
        
        sample2idx = gq.sample_to_idx
        logger.info("Found samples: {0}".format(', '.join(sample2idx.keys())))
        
        if not gemini_query:
            gemini_query = "select * from variants"
        
        gq.run(gemini_query)
        
        for index, gemini_variant in enumerate(gq):
            index += 1
            logger.debug("Updating index to: {0}".format(index))

            # print("max_aaf_all {0}".format(gemini_variant['max_aaf_all']))

            variant_dict = {
                'CHROM':gemini_variant['chrom'].lstrip('chr'),
                'POS':str(gemini_variant['start']),
                'ID':gemini_variant['rs_ids'],
                'REF':gemini_variant['ref'],
                'ALT':gemini_variant['alt'],
                'QUAL':gemini_variant['qual'],
                'FILTER':gemini_variant['filter']
            }
            
            variant = Variant(**variant_dict)
            variant['index'] = index
            # Use the gemini id for fast search
            variant.update_variant_id(gemini_variant['variant_id'])
            # Update the individuals
            for individual in self._get_individuals(
                gemini_variant=gemini_variant, sample2idx=sample2idx):
                # Add the genotype calls to the variant
                variant.add_individual(individual)
            
            for transcript in self._get_transcripts(gemini_variant, gemini_db):
                variant.add_transcript(transcript)
            
            variant['most_severe_consequence'] = get_most_severe_consequence(
                variant['transcripts']
            )
            
            for gene in self._get_genes(variant):
                variant.add_gene(gene)
            
            #### Check the impact annotations ####
            if gemini_variant['cadd_scaled']:
                variant['cadd_score'] = gemini_variant['cadd_scaled']
            
            # We use the prediction in text
            polyphen = gemini_variant['polyphen_pred']
            if polyphen:
                variant.add_severity('Polyphen', polyphen)

            # We use the prediction in text
            sift = gemini_variant['sift_pred']
            if sift:
                variant.add_severity('SIFT', sift)
            
            #### Check the frequencies ####
            thousand_g = gemini_variant['aaf_1kg_all']
            if thousand_g:
                variant['thousand_g'] = float(thousand_g)
                variant.add_frequency(name='1000GAF', value=float(thousand_g))
            
            exac = gemini_variant['aaf_exac_all']
            if exac:
                variant.add_frequency(name='EXaC', value=float(exac))

            esp = gemini_variant['aaf_esp_all']
            if esp:
                variant.add_frequency(name='ESP', value=float(esp))
            
            yield variant
            
        
    
    def variants(self, case_id, skip=0, count=30, gene_list=None, 
                 frequency=None, cadd=None):
        """Return count variants for a case.
            
            case_id : A gemini db
            skip (int): Skip first variants
            count (int): The number of variants to return
            gene_list (list): A list of genes
            thousand_g (float): filter variants based on frequency
            
        """
        case_id = case_id.replace('|', '/')
        logger.debug("Looking for variants in {0}".format(case_id))
        
        limit = count + skip
        
        gemini_query = "SELECT * from variants"
        
        any_filter = False
        #This would be the fastest solution but it seems like we loose all variants
        #that are missing a frequency...
        if frequency:
            gemini_query += " WHERE (max_aaf_all < {0} or max_aaf_all is"\
                            " Null)".format(frequency)
            any_filter = True

        if cadd:
            if any_filter:
                gemini_query += " AND (cadd_scaled > {0})".format(cadd)
            else:
                gemini_query += " WHERE (cadd_scaled > {0})".format(cadd)
            any_filter = True
        
        filtered_variants = self._variants(
            gemini_db=case_id, 
            gemini_query=gemini_query)
        
        if gene_list:
            gene_list = set(gene_list)
            filtered_variants = (variant for variant in filtered_variants
                                 if set(variant['hgnc_symbols'].intersection(gene_list)))

        for index, variant_obj in enumerate(filtered_variants):
            if index >= skip:
                if index <= limit:
                    yield variant_obj
                else:
                    break
        
        
    def variant(self, case_id, variant_id):
        """Return a specific variant.
        
            We solve this by building a gemini query and send it to _variants
            
            Args:
                case_id (str): Path to a gemini database
                variant_id (int): A gemini variant id
            
            Returns:
                variant_obj (dict): A puzzle variant
                
        """
        case_id = case_id.replace('|', '/')
        variant_id = int(variant_id)
        gemini_query = "SELECT * from variants WHERE variant_id = {0}".format(
            variant_id
        )
        for variant in self._variants(
            gemini_db = case_id, 
            gemini_query=gemini_query):
            
            return variant
        
        return None
        
if __name__ == '__main__':
    import sys
    from pprint import pprint as pp
    from puzzle.log import configure_stream
    configure_stream(level="DEBUG")
    gemini_db = sys.argv[1]
    plugin = GeminiPlugin()
    for case in plugin.cases(gemini_db):
        print("Case found: {0}".format(case))
    # try:
    #     for variant in plugin.variants(gemini_db, thousand_g=0.01):
    #         # print(variant['thousand_g'])
    #         pp(variant)
    # except DatabaseError as e:
    #     logger.info("Exiting...")
    #     sys.exit()
    # try:
    #     for variant in plugin.variant(gemini_db, variant_id=3):
    #         print(variant)
    # except DatabaseError as e:
    #     logger.info("Exiting...")
    #     sys.exit()

