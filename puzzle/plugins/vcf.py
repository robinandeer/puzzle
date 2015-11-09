# -*- coding: utf-8 -*-
import os
import logging

from path import path

from puzzle.models import (Case, Compound, Variant, Gene, Genotype, Transcript)
from puzzle.utils import (get_most_severe_consequence, get_hgnc_symbols,
                          get_omim_number, get_ensembl_id)

from puzzle.plugins import Plugin

from vcftoolbox import (get_variant_dict, HeaderParser, get_info_dict,
                        get_vep_dict)

logger = logging.getLogger(__name__)


class VcfPlugin(Plugin):
    """docstring for Plugin"""

    def __init__(self):
        super(VcfPlugin, self).__init__()

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

    def _find_vcfs(self, pattern='*.vcf'):
        """Walk subdirectories and return VCF files."""
        return path(self.root_path).walkfiles(pattern)

    def cases(self, pattern=None):
        """Return all VCF file paths."""
        pattern = pattern or self.pattern

        # if pointing to a single file
        if os.path.isfile(self.root_path):
            vcfs = [path(self.root_path)]
        else:
            vcfs = self._find_vcfs(pattern)

        case_objs = (Case(case_id=vcf.replace('/', '|'),
                          name=vcf.basename()) for vcf in vcfs)
        return case_objs

    def case(self, case_id=None):
        """Return a Case object

            If no case_id is given return one case

            Args:
                case_id (str): A case id

            Returns:
                A Case object
        """
        cases = self.cases()
        if case_id:
            for case in cases:
                if case['case_id'] == case_id:
                    return case
        else:
            if cases:
                return list(cases)[0]

        return Case(case_id='unknown')

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

    def _get_transcripts(self, variant, vep_dict):
        """Get all transcripts for a variant

            Args:
                vep_dict (dict): A vep dict

            Returns:
                transcripts (list): A list of transcripts
        """
        transcripts = []
        for allele in vep_dict:
            for transcript_info in vep_dict[allele]:
                transcripts.append(Transcript(
                    SYMBOL = transcript_info.get('SYMBOL'),
                    Feature = transcript_info.get('Feature'),
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
        individuals = head.individuals

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
                    vep_string = info_dict.get('CSQ')

                    if vep_string:
                        vep_dict = get_vep_dict(
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

                    variant['stop'] = int(variant_dict['POS']) + \
                        (len(variant_dict['REF']) - len(variant_dict['ALT']))

                    # It would be easy to update these keys...
                    thousand_g = info_dict.get('1000GAF')
                    if thousand_g:
                        logger.debug("Updating thousand_g to: {0}".format(
                            thousand_g))
                        variant['thousand_g'] = float(thousand_g)
                    variant.add_frequency('1000GAF', variant.get('thousand_g'))

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
                        for sample_id in individuals:
                            raw_call = dict(zip(
                                variant_dict['FORMAT'].split(':'),
                                variant_dict[sample_id].split(':'))
                            )
                            variant.add_individual(Genotype(
                                sample_id = sample_id,
                                genotype = raw_call.get('GT', './.'),
                                ref_depth = raw_call.get('AD', ',').split(',')[0],
                                alt_depth = raw_call.get('AD', ',').split(',')[1],
                                genotype_quality = raw_call.get('GQ', '.'),
                                depth = raw_call.get('DP', '.')
                            ))

                    # Add transcript information:
                    if vep_string:
                        for transcript in self._get_transcripts(variant, vep_dict):
                            variant.add_transcript(transcript)

                    variant['most_severe_consequence'] = get_most_severe_consequence(
                        variant['transcripts']
                    )
                    for gene in self._get_genes(variant):
                        variant.add_gene(gene)

                    self._add_compounds(variant=variant, info_dict=info_dict)

                    yield variant

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
                    consequence: [] (list of consequences),
                    is_lof: None (Bool),
                    genetic_models [] (list of genetic models)
                }
        """

        vcf_path = case_id.replace('|', '/')
        limit = count + skip

        filtered_variants = self._variants(vcf_path)

        if filters.get('gene_list'):
            gene_list = set(filters['gene_list'])
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

        for index, variant_obj in enumerate(filtered_variants):
            if index >= skip:
                if index <= limit:
                    yield variant_obj
                else:
                    break

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
