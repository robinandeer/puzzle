# -*- coding: utf-8 -*-
import logging

from path import path

from puzzle.models import (Case, Variant, Genotype, Transcript, Gene, Compound)
from puzzle.utils import (get_most_severe_consequence, get_hgnc_symbols, 
get_omim_number)

from vcftoolbox import (get_variant_dict, HeaderParser, get_info_dict,
                        get_vep_dict)

logger = logging.getLogger(__name__)


class Plugin(object):
    """docstring for Plugin"""
    def __init__(self, vcf_file=None):
        self.vcf_file = vcf_file

    def init_app(self, app):
        """Initialize plugin via Flask."""
        self.root_path = app.config['PUZZLE_ROOT']
        self.pattern = app.config['PUZZLE_PATTERN']

    def _find_vcfs(self, pattern='*.vcf'):
        """Walk subdirectories and return VCF files."""
        return path(self.root_path).walkfiles(pattern)

    def cases(self, pattern=None):
        """Return all VCF file paths."""
        pattern = pattern or self.pattern
        vcfs = self._find_vcfs(pattern)
        case_objs = (Case(case_id=vcf.replace('/', '|'),
                          name=vcf.basename()) for vcf in vcfs)
        return case_objs

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
                        variant_id = compound_id, 
                        combined_score = compound_score
                    ))
    
    def _add_genes(self, variant):
        """Add the genes for a variant"""
        
        hgnc_symbols = get_hgnc_symbols(
            transcripts = variant['transcripts']
        )
    
        variant['hgnc_symbols'] = list(hgnc_symbols)
    
        for hgnc_id in hgnc_symbols:
            variant.add_gene(Gene(
                symbol = hgnc_id, 
                omim_number = get_omim_number(hgnc_id)
            ))
    
    def _add_transcripts(self, variant, vep_dict):
        """Add the transcripts for a variant"""
        
        for allele in vep_dict:
            for transcript_info in vep_dict[allele]:
                variant.add_transcript(Transcript(
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

        variant_columns = ['CHROM','POS','ID','REF','ALT','QUAL','FILTER']

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

                    cadd_score = info_dict.get('CADD')
                    if cadd_score:
                        logger.debug("Updating cadd_score to: {0}".format(
                            cadd_score))
                        variant['cadd_score'] = float(cadd_score)

                    rank_score_entry = info_dict.get('RankScore')
                    if rank_score_entry:
                        for family_annotation in rank_score_entry.split(','):
                            rank_score = family_annotation.split(':')[-1]
                        logger.debug("Updating cadd_score to: {0}".format(
                            cadd_score))
                        variant['rank_score'] = float(rank_score)

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

                    if vep_string:
                        #Add transcript information:
                        self._add_transcripts(variant, vep_dict)
                    
                    variant['most_severe_consequence'] = get_most_severe_consequence(
                        variant['transcripts']
                    )
                    self._add_genes(variant)
                    
                    self._add_compounds(variant=variant, info_dict=info_dict)

                    yield variant

    def variants(self, case_id, skip=0, count=30, gene_list=[]):
        """Return all variants in the VCF.

            Args:
                case_id (str): Path to a vcf file(for this adapter)
                skip (int): Skip first variants
                count (int): The number of variants to return
                gene_list (list): A list of genes
        """
        limit = count + skip

        if gene_list:
            gene_list = set(gene_list)
            filtered_variants = (variant for variant in self._variants(case_id)
                                 if set(variant['hgnc_symbols'].intersection(gene_list)))
        else:
            vcf_path = case_id.replace('|', '/')
            filtered_variants = self._variants(vcf_path)

        for variant in filtered_variants:
            if variant['index'] >= skip:
                if variant['index'] <= limit:
                    yield variant
                else:
                    break

    def variant(self, case_id, variant_id):
        """Return a specific variant."""
        for variant in self.variants(case_id):
            if variant['variant_id'] == variant_id:
                return variant
        return None


if __name__ == '__main__':
    import sys
    from pprint import pprint as pp
    vcf_file = sys.argv[1]
    plugin = Plugin()
    for variant in plugin.variants(case_id=vcf_file):
        print(variant)
        print('')

