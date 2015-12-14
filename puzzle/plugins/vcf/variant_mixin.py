import logging

from vcftoolbox import (get_variant_dict, HeaderParser, get_info_dict,
                        get_vep_info)

from puzzle.models import (Compound, Variant, Gene, Genotype, Transcript,)

from puzzle.utils import (get_most_severe_consequence, get_hgnc_symbols,
                          get_omim_number, get_ensembl_id, get_cytoband_coord,
                          get_gene_info)


logger = logging.getLogger(__name__)

class VariantMixin(object):
    """Class to store variant specific functions for vcf plugin"""

    def variant(self, case_id, variant_id):
        """Return a specific variant.

            Args:
                case_id (str): Path to vcf file
                variant_id (str): A variant id

            Returns:
                variant (Variant): The variant object for the given id
        """
        for variant_obj in self.variants(case_id, count=float('inf')):
            if variant_obj['variant_id'] == variant_id:
                return variant_obj
        return None

    def variants(self, case_id, skip=0, count=30, filters={}):
        """Return all variants in the VCF.

            Args:
                case_id (str): Path to a vcf file (for this adapter)
                skip (int): Skip first variants
                count (int): The number of variants to return
                filters (dict): A dictionary with filters. Currently this will
                look like: {
                    gene_list: [] (list of hgnc ids),
                    frequency: None (float),
                    cadd: None (float),
                    sv_len: None (float),
                    consequence: [] (list of consequences),
                    is_lof: None (Bool),
                    genetic_models [] (list of genetic models)
                    sv_type: List (list of sv types),
                }
        """

        vcf_path = case_id.replace('|', '/')
        limit = count + skip

        filtered_variants = self._variants(vcf_path)

        if filters.get('gene_list'):
            gene_list = set([gene_id.strip() for gene_id in filters['gene_list']])
            
            filtered_variants = (variant for variant in filtered_variants
                                 if (set(gene['symbol'] for gene in variant['genes'])
                                     .intersection(gene_list)))

        if filters.get('frequency'):
            frequency = float(filters['frequency'])
            filtered_variants = (variant for variant in filtered_variants
                                 if variant['max_freq'] <= frequency)

        if filters.get('cadd'):
            cadd_score = float(filters['cadd'])
            filtered_variants = (variant for variant in filtered_variants
                                 if variant['max_freq'] <= cadd_score)
        
        if filters.get('consequence'):
            consequences = set(filters['consequence'])
            cons_variants = []
            for variant in filtered_variants:
                for transcript in variant.get('transcripts', []):
                    if transcript['Consequence'] in consequences:
                        cons_variants.append(variant)
                        break
            
            filtered_variants = cons_variants
        
        if filters.get('genetic_models'):
            genetic_models = set(filters['genetic_models'])
            filtered_variants = (variant for variant in filtered_variants
            if set(variant.get('genetic_models',[])).intersection(genetic_models))
        
        if filters.get('sv_types'):
            sv_types = set(filters['sv_types'])
            filtered_variants = (variant for variant in filtered_variants
                                    if variant.get('sv_type') in sv_types)

        if filters.get('sv_len'):
            sv_len = float(filters['sv_len'])
            filtered_variants = (variant for variant in filtered_variants
                                    if variant.get('sv_len') >= sv_len)

        for index, variant_obj in enumerate(filtered_variants):
            if index >= skip:
                if index <= limit:
                    yield variant_obj
                else:
                    break

    
    
    def _add_compounds(self, variant, info_dict):
        """Check if there are any compounds and add them to the variant

        """
        compound_entry = info_dict.get('Compounds')
        if compound_entry:
            for family_annotation in compound_entry.split(','):
                compounds = family_annotation.split(':')[-1].split('|')
                for compound in compounds:
                    splitted_compound = compound.split('>')

                    compound_score = None
                    if len(splitted_compound) > 1:
                        compound_id = splitted_compound[0]
                        compound_score = splitted_compound[-1]

                    variant.add_compound(Compound(
                        variant_id=compound_id,
                        combined_score=compound_score
                    ))

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

    def _get_transcripts(self, variant, vep_info):
        """Get all transcripts for a variant

            Args:
                vep_info (list): A list of vep dicts

            Returns:
                transcripts (list): A list of transcripts
        """
        transcripts = []
        for transcript_info in vep_info:
            transcripts.append(Transcript(
                SYMBOL = transcript_info.get('SYMBOL'),
                Feature = transcript_info.get('Feature'),
                Gene = transcript_info.get('Gene'),
                BIOTYPE = transcript_info.get('BIOTYPE'),
                Consequence = transcript_info.get('Consequence'),
                STRAND = transcript_info.get('STRAND'),
                SIFT = transcript_info.get('SIFT'),
                PolyPhen = transcript_info.get('PolyPhen'),
                EXON = transcript_info.get('EXON'),
                HGVSc = transcript_info.get('HGVSc'),
                HGVSp = transcript_info.get('HGVSp')
            ))
        return transcripts

    def _variants(self, vcf_file_path):
        head = HeaderParser()
        # Parse the header
        with open(vcf_file_path, 'r') as variant_file:
            for line in variant_file:
                line = line.rstrip()
                if line.startswith('#'):
                    if line.startswith('##'):
                        head.parse_meta_data(line)
                    else:
                        head.parse_header_line(line)
                else:
                    break

        header_line = head.header
        
        if self.individuals:
            individuals = self.individuals
        else:
            individuals = self._get_individuals(vcf_file_path)

        variant_columns = ['CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER']

        vep_header = head.vep_columns

        with open(vcf_file_path, 'r') as vcf_file:
            index = 0
            for variant_line in vcf_file:
                if not variant_line.startswith('#'):
                    index += 1
                    #Create a variant dict:
                    variant_dict =  get_variant_dict(
                        variant_line = variant_line,
                        header_line = header_line
                    )
                    #Crreate a info dict:
                    info_dict = get_info_dict(
                        info_line = variant_dict['INFO']
                    )
                    #Check if vep annotation:
                    vep_string = info_dict.get('CSQ')

                    if vep_string:
                        #Get the vep annotations
                        vep_info = get_vep_info(
                            vep_string = vep_string,
                            vep_header = vep_header
                        )

                    variant = Variant(
                        **{column: variant_dict.get(column, '.')
                            for column in variant_columns}
                        )

                    logger.debug("Creating a variant object of variant {0}".format(
                        variant.get('variant_id')))

                    variant['index'] = index
                    logger.debug("Updating index to: {0}".format(
                        index))

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
                        else:
                            variant['stop'] = int(info_dict.get('END', variant_dict['POS']))
                            variant['sv_len'] = variant['stop'] - variant['start']
                        
                        variant['stop_chrom'] = other_chrom
                        
                    else:
                        variant['stop'] = int(variant_dict['POS']) + \
                            (len(variant_dict['REF']) - len(variant_dict['ALT']))
                    
                    variant['sv_type'] = info_dict.get('SVTYPE')
                    variant['cytoband_start'] = get_cytoband_coord(
                                                    chrom=variant['CHROM'], 
                                                    pos=variant['start'])
                    if variant.get('stop_chrom'):
                        variant['cytoband_stop'] = get_cytoband_coord(
                                                    chrom=variant['stop_chrom'], 
                                                    pos=variant['stop'])
                    
                    # It would be easy to update these keys...
                    thousand_g = info_dict.get('1000GAF')
                    if thousand_g:
                        logger.debug("Updating thousand_g to: {0}".format(
                            thousand_g))
                        variant['thousand_g'] = float(thousand_g)
                        variant.add_frequency('1000GAF', variant.get('thousand_g'))
                    
                    #SV specific tag for number of occurances
                    occurances = info_dict.get('OCC')
                    if occurances:
                        logger.debug("Updating occurances to: {0}".format(
                            occurances))
                        variant['occurances'] = float(occurances)
                        variant.add_frequency('OCC', occurances)

                    cadd_score = info_dict.get('CADD')
                    if cadd_score:
                        logger.debug("Updating cadd_score to: {0}".format(
                            cadd_score))
                        variant['cadd_score'] = float(cadd_score)

                    rank_score_entry = info_dict.get('RankScore')
                    if rank_score_entry:
                        for family_annotation in rank_score_entry.split(','):
                            rank_score = family_annotation.split(':')[-1]
                        logger.debug("Updating rank_score to: {0}".format(
                            rank_score))
                        variant['rank_score'] = float(rank_score)

                    genetic_models_entry = info_dict.get('GeneticModels')
                    if genetic_models_entry:
                        genetic_models = []
                        for family_annotation in genetic_models_entry.split(','):
                            for genetic_model in family_annotation.split(':')[-1].split('|'):
                                genetic_models.append(genetic_model)
                        logger.debug("Updating rank_score to: {0}".format(
                            rank_score))
                        variant['genetic_models'] = genetic_models

                    #Add genotype calls:
                    if individuals:
                        for individual in individuals:
                            sample_id = individual['ind_id']
                            
                            raw_call = dict(zip(
                                variant_dict['FORMAT'].split(':'),
                                variant_dict[sample_id].split(':'))
                            )
                            variant.add_individual(Genotype(
                                sample_id = sample_id,
                                genotype = raw_call.get('GT', './.'),
                                case_id = individual.get('case_id'),
                                phenotype = individual.get('phenotype'),
                                ref_depth = raw_call.get('AD', ',').split(',')[0],
                                alt_depth = raw_call.get('AD', ',').split(',')[1],
                                genotype_quality = raw_call.get('GQ', '.'),
                                depth = raw_call.get('DP', '.'),
                                supporting_evidence = raw_call.get('SU', '0'),
                                pe_support = raw_call.get('PE', '0'),
                                sr_support = raw_call.get('SR', '0'),
                            ))

                    # Add transcript information:
                    if vep_string:
                        for transcript in self._get_transcripts(variant, vep_info):
                            variant.add_transcript(transcript)

                    variant['most_severe_consequence'] = get_most_severe_consequence(
                        variant['transcripts']
                    )
                    for gene in self._get_genes(variant):
                        variant.add_gene(gene)

                    self._add_compounds(variant=variant, info_dict=info_dict)

                    yield variant

