import logging

from vcftoolbox import (get_variant_dict, HeaderParser, get_info_dict,
                        get_vep_info, get_snpeff_info, get_vcf_handle,
                        get_variant_id, Genotype)

from puzzle.plugins import BaseVariantMixin

from puzzle.models import (Compound, Variant, Gene)
from puzzle.models import Genotype as puzzle_genotype
from puzzle.utils import (get_most_severe_consequence, get_omim_number,
                          IMPACT_SEVERITIES)

from .variant_extras import VariantExtras

logger = logging.getLogger(__name__)

class VariantMixin(BaseVariantMixin, VariantExtras):
    """Class to store variant specific functions for vcf plugin"""

    def variant(self, case_id, variant_id):
        """Return a specific variant.

            Args:
                case_id (str): Path to vcf file
                variant_id (str): A variant id

            Returns:
                variant (Variant): The variant object for the given id
        """
        case_obj = self.case(case_id=case_id)
        vcf_file_path = case_obj.variant_source
        # self.head = self._get_header(vcf_file_path)

        handle = get_vcf_handle(infile=vcf_file_path)
        relevant_lines = (line for line in handle if not line.startswith('#'))
        
        for index, variant_line in enumerate(relevant_lines):
            index += 1
            line_id = get_variant_id(variant_line=variant_line).lstrip('chrCHR')
            if line_id == variant_id:
                return self._format_variants(
                    variant_line=variant_line,
                    index=index,
                    case_obj=case_obj,
                    add_all_info=True
                    )

        return None

    def variants(self, case_id, skip=0, count=30, filters=None):
        """Return all variants in the VCF.
        
        This function will apply the given filter and return the 'count' first 
        variants. If skip the first 'skip' variants will not be regarded.

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
        filters = filters or {}
        case_obj = self.case(case_id=case_id)
        limit = count + skip

        genes = None
        if filters.get('genes'):
            genes = set(filters['genes'])

        frequency = None
        if filters.get('frequency'):
            frequency = float(filters['frequency'])

        cadd = None
        if filters.get('cadd'):
            cadd = float(filters['cadd'])

        genetic_models = None
        if filters.get('genetic_models'):
            genetic_models = set(filters['genetic_models'])

        sv_len = None
        if filters.get('sv_len'):
            sv_len = float(filters['sv_len'])

        impact_severities = None
        if filters.get('impact_severities'):
            impact_severities = set(filters['impact_severities'])

        vcf_file_path = case_obj.variant_source

        self.head = self._get_header(vcf_file_path)
        
        self.vep_header = self.head.vep_columns
        self.snpeff_header = self.head.snpeff_columns

        raw_variants = self._get_filtered_variants(vcf_file_path, filters)
        
        skip_index = 0
        for index, variant_line in enumerate(raw_variants):
            index += 1
            if skip_index >= skip:
                print(skip_index, index, skip)
                variant_obj = self._format_variants(
                     variant_line=variant_line,
                     index=index,
                     case_obj=case_obj,
                )

                if genes and variant_obj:
                    if not set(variant_obj['genes']).intersection(genes):
                        variant_obj = None

                if impact_severities and variant_obj:
                    if not variant_obj['impact_severity'] in impact_severities:
                        variant_obj = None
                
                if frequency and variant_obj:
                    if variant_obj['max_freq'] > frequency:
                        variant_obj = None
                
                if cadd and variant_obj:
                    if variant_obj['cadd_score'] < cadd:
                        variant_obj = None

                if genetic_models and variant_obj:
                    if not set(variant_obj.genetic_models).intersection(genetic_models):
                        variant_obj = None

                if sv_len and variant_obj:
                    if variant_obj.sv_len < sv_len:
                        variant_obj = None

                if variant_obj:
                    skip_index += 1

                    if skip_index <= limit:
                        yield variant_obj
                    else:
                        break
            else:
                skip_index += 1

    def _get_header(self, vcf_file_path):
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

    def _get_filtered_variants(self, vcf_file_path, filters={}):
        """Check if variants follows the filters

            This function will try to make filters faster for the vcf adapter

            Args:
                vcf_file_path(str): Path to vcf
                filters (dict): A dictionary with filters

            Yields:
                varian_line (str): A vcf variant line
        """

        genes = set()
        consequences = set()
        sv_types = set()

        if filters.get('gene_ids'):
            genes = set([gene_id.strip() for gene_id in filters['gene_ids']])

        if filters.get('consequence'):
            consequences = set(filters['consequence'])

        if filters.get('sv_types'):
            sv_types = set(filters['sv_types'])

        logger.info("Get variants from {0}".format(vcf_file_path))

        handle = get_vcf_handle(infile=vcf_file_path)
        for variant_line in handle:
            if not variant_line.startswith('#'):
                keep_variant = True

                if genes and keep_variant:
                    keep_variant = False
                    for gene in genes:
                        if "{0}".format(gene) in variant_line:
                            keep_variant = True
                            break

                if consequences and keep_variant:
                    keep_variant = False
                    for consequence in consequences:
                        if consequence in variant_line:
                            keep_variant = True
                            break

                if sv_types and keep_variant:
                    keep_variant = False
                    for sv_type in sv_types:
                        if sv_type in variant_line:
                            keep_variant = True
                            break

                if keep_variant:
                    yield variant_line

    def _add_compounds(self, variant_obj, info_dict):
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

                    variant_obj.add_compound(Compound(
                        variant_id=compound_id,
                        combined_score=compound_score
                    ))

    
    def _add_coordinates(self, variant_obj, variant_dict):
        """Add the coordinates for a variant
        
            Args:
                variant_obj (puzzle.models.Variant)
                variant_dict (dict): A variant dictionary
        """
        variant_obj.CHROM = variant_obj.CHROM.lstrip('chrCHR')
        variant_obj.start = int(variant_dict['POS'])
        variant_obj.stop = int(variant_dict['POS']) + \
                (len(variant_dict['REF']) - len(variant_dict['ALT']))
    
    def _add_genotype_calls(self, variant_obj, variant_dict, case_obj, 
                            vcf_individuals):
        """Add the genotype calls for the variant
        
        Args:
            variant_obj (puzzle.models.Variant)
            variant_dict (dict): A variant dictionary
            case_obj (puzzle.models.Case)
            vcf_individuals (set): The vcf individuals
            
        """
        for individual in case_obj.individuals:
            sample_id = individual.ind_id

            if sample_id in vcf_individuals:

                raw_call = dict(zip(
                    variant_dict['FORMAT'].split(':'),
                    variant_dict[sample_id].split(':'))
                )

                genotype = Genotype(**raw_call)

                variant_obj.add_individual(puzzle_genotype(
                    sample_id = sample_id,
                    genotype = genotype.genotype,
                    case_id = individual.case_name,
                    phenotype = individual.phenotype,
                    ref_depth = genotype.ref_depth,
                    alt_depth = genotype.alt_depth,
                    genotype_quality = genotype.genotype_quality,
                    depth = genotype.depth_of_coverage,
                    supporting_evidence = genotype.supporting_evidence,
                    pe_support = genotype.pe_support,
                    sr_support = genotype.sr_support,
                ))
    
    def _add_cadd_score(self, variant_obj, info_dict):
        """Add the cadd score to the variant
        
            Args:
                variant_obj (puzzle.models.Variant)
                info_dict (dict): A info dictionary
            
        """
        cadd_score = info_dict.get('CADD')
        if cadd_score:
            logger.debug("Updating cadd_score to: {0}".format(
                cadd_score))
            variant_obj.cadd_score = float(cadd_score)
        ##TODO if cadd score is annotated with vep or snpeff,
        ## extract from transcripts
    
    def _add_genetic_models(self, variant_obj, info_dict):
        """Add the genetic models found
        
        Args:
            variant_obj (puzzle.models.Variant)
            info_dict (dict): A info dictionary
        
        """
        genetic_models_entry = info_dict.get('GeneticModels')
        if genetic_models_entry:
            genetic_models = []
            for family_annotation in genetic_models_entry.split(','):
                for genetic_model in family_annotation.split(':')[-1].split('|'):
                    genetic_models.append(genetic_model)
            logger.debug("Updating genetic models to: {0}".format(
                ', '.join(genetic_models)))
                
            variant_obj.genetic_models = genetic_models
    
    def _add_rank_score(self, variant_obj, info_dict):
        """Add the rank score if found
        
        Args:
            variant_obj (puzzle.models.Variant)
            info_dict (dict): A info dictionary
        
        """
        rank_score_entry = info_dict.get('RankScore')
        if rank_score_entry:
            for family_annotation in rank_score_entry.split(','):
                rank_score = family_annotation.split(':')[-1]
            logger.debug("Updating rank_score to: {0}".format(
                rank_score))
            variant_obj.rank_score = float(rank_score)

    def _format_variants(self, variant_line, index, case_obj, add_all_info=False):
        """Return a Variant object
        
        Format variant make a variant that includes enough information for 
        the variant view.
        If add_all_info then all transcripts will be parsed

        Args:
            variant_line (str): A raw vcf variant line
            index (int): The index of the variant
            case_obj (puzzle.models.Case): A case object
            head (vcftoolbox.Head): A header object

        """
        header_line = self.head.header
        # Get the individual ids for individuals in vcf file
        vcf_individuals = set([ind_id for ind_id in self.head.individuals])

        #Create a variant dict:
        variant_dict =  get_variant_dict(
            variant_line = variant_line,
            header_line = header_line
        )
        #Create a info dict:
        info_dict = get_info_dict(
            info_line = variant_dict['INFO']
        )

        variant = Variant(
            **{column: variant_dict.get(column, '.')
                for column in self.variant_columns}
            )

        logger.debug("Creating a variant object of variant {0}".format(
            variant.get('variant_id')))

        variant.index = index
        logger.debug("Updating index to: {0}".format(
            index))

        ########### Get the coordinates for the variant ##############
        # Get the chromosome
        self._add_coordinates(variant, variant_dict)
        
        #SV variants needs to be handeled a bit different since the can be huge
        #it would take to much power to parse all vep/snpeff entrys for these.
        if self.variant_type == 'sv':
            variant.stop = int(info_dict.get('END', variant_dict['POS']))
            self._add_sv_coordinates(variant)
            variant.sv_type = info_dict.get('SVTYPE')
            
            # Special for FindSV software:
            #SV specific tag for number of occurances
            occurances = info_dict.get('OCC')
            if occurances:
                logger.debug("Updating occurances to: {0}".format(
                    occurances))
                variant['occurances'] = float(occurances)
                variant.add_frequency('OCC', occurances)
        
        else:
            self._add_thousand_g(variant, info_dict)
            self._add_cadd_score(variant, info_dict)
            self._add_genetic_models(variant, info_dict)
            self._add_transcripts(variant, info_dict)
            
            if add_all_info:
                self._add_genotype_calls(variant, variant_dict, case_obj, 
                                         vcf_individuals)
                self._add_compounds(variant, info_dict)
                self._add_gmaf(variant, info_dict)
                
        
        self._add_genes(variant)
        ##### Add consequences ####
        self._add_consequences(variant, variant_line)
        self._add_most_severe_consequence(variant)
        self._add_impact_severity(variant)
        self._add_rank_score(variant, info_dict)
        variant.set_max_freq()

        return variant

