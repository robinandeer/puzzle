import logging

from gemini import GeminiQuery

from puzzle.models import (Compound, Variant, Gene, Genotype, Transcript,)

from puzzle.utils import (get_most_severe_consequence, get_hgnc_symbols,
                          get_omim_number, get_ensembl_id, get_cytoband_coord,
                          get_gene_info)


logger = logging.getLogger(__name__)

class VariantMixin(object):
    """Class to store variant specific functions for gemini plugin"""
    
    def variants(self, case_id, skip=0, count=30, filters={}):
        """Return count variants for a case.

            Args:
                case_id (str): A gemini db
                skip (int): Skip first variants
                count (int): The number of variants to return
                filters (dict): A dictionary with filters. Currently this will
                look like: {
                    gene_list: [] (list of hgnc ids),
                    frequency: None (float),
                    cadd: None (float),
                    consequence: [] (list of consequences),
                    is_lof: None (Bool),
                    genetic_models [] (list of genetic models)
                }

        """
        logger.debug("Looking for variants in {0}".format(case_id))

        limit = count + skip

        gemini_query = "SELECT * from variants"

        any_filter = False

        if filters.get('frequency'):
            frequency = filters['frequency']
            gemini_query += " WHERE (max_aaf_all < {0} or max_aaf_all is"\
                            " Null)".format(frequency)
            any_filter = True

        if filters.get('cadd'):
            cadd_score = filters['cadd']
            if any_filter:
                gemini_query += " AND (cadd_scaled > {0})".format(cadd_score)
            else:
                gemini_query += " WHERE (cadd_scaled > {0})".format(cadd_score)
            any_filter = True

        if filters.get('gene_list'):
            gene_list = [gene_id.strip() for gene_id in filters['gene_list']]
            gene_string = "("
            for index, gene_id in enumerate(gene_list):
                if index == 0:
                    gene_string += "'{0}'".format(gene_id)
                else:
                    gene_string += ", '{0}'".format(gene_id)
            gene_string += ")"

            if any_filter:
                gemini_query += " AND gene in " + gene_string
            else:
                gemini_query += " WHERE gene in " + gene_string

            any_filter = True

        filtered_variants = self._variants(
            case_id=case_id,
            gemini_query=gemini_query
        )

        if filters.get('consequence'):
            consequences = set(filters['consequence'])
            cons_variants = []
            for variant in filtered_variants:
                for transcript in variant.get('transcripts', []):
                    if transcript['Consequence'] in consequences:
                        cons_variants.append(variant)
                        break

            filtered_variants = cons_variants

        for index, variant_obj in enumerate(filtered_variants):
            if index >= skip:
                if index < limit:
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
        variant_id = int(variant_id)
        gemini_query = "SELECT * from variants WHERE variant_id = {0}".format(
            variant_id
        )

        individuals = []
        # Get the individuals for the case
        for case in self.cases():
            if case['name'] == case_id:
                for individual in case['individuals']:
                    individuals.append(individual)

        gq = GeminiQuery(self.db)

        gq.run(gemini_query)

        for gemini_variant in gq:
            variant = self._format_variant(
                gemini_variant=gemini_variant,
                individual_objs=individuals,
                index=gemini_variant['variant_id']
            )

            return variant

        return None
    
    def _get_genotypes(self, gemini_variant, individual_objs):
        """Add the genotypes for a variant for all individuals

            Args:
                gemini_variant (GeminiQueryRow): The gemini variant
                individual_objs (list(dict)): A list of Individuals

            Returns:
                individuals (list) A list of Genotypes
        """
        individuals = []
        for ind in individual_objs:
            index = ind['index']
            individuals.append(Genotype(
                sample_id=ind['ind_id'],
                genotype=gemini_variant['gts'][index],
                case_id=ind.get('case_id'),
                phenotype=ind.get('phenotype'),
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
        genes = get_gene_info(variant['transcripts'])
        return genes

    def _get_transcripts(self, gemini_variant):
        """Return a Transcript object

            Gemini stores the information for the most severe transcript
            so only one transcript is connected to one variant.

            Args:
                gemini_variant (GeminiQueryRow): The gemini variant

            Returns:
                transcripts list: List of affected transcripts

        """
        query = "SELECT * from variant_impacts WHERE variant_id = {0}".format(
            gemini_variant['variant_id']
        )
        gq = GeminiQuery(self.db)
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
    
    def _variants(self, case_id, gemini_query):
        """Return variants found in the gemini database

            Args:
                case_id (str): The case for which we want to see information
                gemini_query (str): What variants should be chosen

            Yields:
                variant_obj (dict): A Variant formatted doctionary
        """

        gq = GeminiQuery(self.db)

        gq.run(gemini_query)

        individuals = []
        # Get the individuals for the case
        for case in self.cases():
            if case['name'] == case_id:
                for individual in case['individuals']:
                    individuals.append(individual)

        indexes = [individual['index'] for individual in individuals]

        index = 0
        for gemini_variant in gq:
            # Check if variant is non ref in the individuals
            if self._is_variant(gemini_variant, indexes):
                index += 1
                logger.debug("Updating index to: {0}".format(index))

                variant = self._format_variant(
                    gemini_variant=gemini_variant,
                    individual_objs=individuals,
                    index=index
                )
                yield variant
    
    def _format_variant(self, gemini_variant, individual_objs, index=0):
        """Make a puzzle variant from a gemini variant

            Args:
                gemini_variant (GeminiQueryRow): The gemini variant
                individual_objs (list(dict)): A list of Individuals
                index(int): The index of the variant

            Returns:
                variant (dict): A Variant object
        """
        variant_dict = {
            'CHROM':gemini_variant['chrom'].lstrip('chr'),
            'POS':str(gemini_variant['start']),
            'ID':gemini_variant['rs_ids'],
            'REF':gemini_variant['ref'],
            'ALT':gemini_variant['alt'],
            'QUAL':gemini_variant['qual'],
            'FILTER':gemini_variant['filter']
        }
        
        print(variant_dict)
        variant = Variant(**variant_dict)
        variant['index'] = index

        # Use the gemini id for fast search
        variant.update_variant_id(gemini_variant['variant_id'])
        # Update the individuals
        individual_genotypes = self._get_genotypes(
            gemini_variant=gemini_variant,
            individual_objs=individual_objs
            )

        for individual in individual_genotypes:
            # Add the genotype calls to the variant
            variant.add_individual(individual)

        for transcript in self._get_transcripts(gemini_variant):
            variant.add_transcript(transcript)

        variant['most_severe_consequence'] = get_most_severe_consequence(
            variant['transcripts']
        )
        for gene in self._get_genes(variant):
            variant.add_gene(gene)
        
        variant['start'] = int(variant_dict['POS'])
        
        if self.mode == 'sv':
            other_chrom = variant['CHROM']
            # If we have a translocation:
            if ':' in variant_dict['ALT']:
                other_coordinates = variant_dict['ALT'].strip('ACGTN[]').split(':')
                other_chrom = other_coordinates[0].lstrip('chrCHR')
                other_position = other_coordinates[1]
                variant['stop'] = other_position
       
                #Set 'infinity' to length if translocation
                variant['sv_len'] = float('inf')
                variant['sv_type'] = 'BND'
            else:
                variant['stop'] = int(gemini_variant['end'])
                variant['sv_len'] = variant['stop'] - variant['start']
                variant['sv_type'] = gemini_variant['sub_type']
       
            variant['stop_chrom'] = other_chrom
            
        else:
            variant['stop'] = int(variant_dict['POS']) + \
                (len(variant_dict['REF']) - len(variant_dict['ALT']))
        
        variant['cytoband_start'] = get_cytoband_coord(
                                        chrom=variant['CHROM'], 
                                        pos=variant['start'])

        if variant.get('stop_chrom'):
            variant['cytoband_stop'] = get_cytoband_coord(
                                        chrom=variant['stop_chrom'], 
                                        pos=variant['stop'])
        
        
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

        max_freq = gemini_variant['max_aaf_all']
        if max_freq:
            variant.set_max_freq(max_freq)

        return variant
    
    
    def _is_variant(self, gemini_variant, indexes):
        """Check if the variants is a variation in any of the individuals

            Args:
                gemini_variant (GeminiQueryRow): The gemini variant
                indexes (list(int)): A list of indexes for the individuals

            Returns:
                bool : If any of the individuals has the variant
        """

        for index in indexes:
            if gemini_variant['gts'][index] != 0:
                return True

        return False
    