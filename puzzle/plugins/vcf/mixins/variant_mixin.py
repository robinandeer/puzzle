import logging

from vcftoolbox import (get_vcf_handle,get_variant_id)

from cyvcf2 import VCF

from puzzle.plugins import BaseVariantMixin
from puzzle.plugins.constants import Results

from puzzle.models import (Variant)

from puzzle.utils import (get_most_severe_consequence, get_omim_number,
                          get_csq, IMPACT_SEVERITIES, get_header)

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
        self.head = get_header(vcf_file_path)

        self.vep_header = self.head.vep_columns
        self.snpeff_header = self.head.snpeff_columns

        handle = VCF(vcf_file_path)

        for index, variant in enumerate(handle):
            index += 1
            line_id = get_variant_id(variant_line=str(variant)).lstrip('chrCHR')
            if line_id == variant_id:
                return self._format_variants(
                    variant=variant,
                    index=index,
                    case_obj=case_obj,
                    add_all_info=True
                    )

        return None

    def variants(self, case_id, skip=0, count=1000, filters=None):
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
            Returns:
                puzzle.constants.Results : Named tuple with variants and
                                           nr_of_variants

        """
        filters = filters or {}
        case_obj = self.case(case_id=case_id)

        limit = count + skip

        genes = set()
        if filters.get('gene_ids'):
            genes = set([gene_id.strip() for gene_id in filters['gene_ids']])

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

        self.head = get_header(vcf_file_path)

        self.vep_header = self.head.vep_columns
        self.snpeff_header = self.head.snpeff_columns

        variants = self._get_filtered_variants(vcf_file_path, filters)

        result = []
        skip_index = 0
        for index, variant in enumerate(variants):
            index += 1
            if skip_index >= skip:
                variant_obj = self._format_variants(
                     variant=variant,
                     index=index,
                     case_obj=case_obj,
                )

                if genes and variant_obj:
                    if not set(variant_obj['gene_symbols']).intersection(genes):
                        variant_obj = None

                if impact_severities and variant_obj:
                    if not variant_obj['impact_severity'] in impact_severities:
                        variant_obj = None

                if frequency and variant_obj:
                    if variant_obj.max_freq > frequency:
                        variant_obj = None

                if cadd and variant_obj:
                    if variant_obj['cadd_score'] < cadd:
                        variant_obj = None

                if genetic_models and variant_obj:
                    models = set(variant_obj.genetic_models)
                    if not models.intersection(genetic_models):
                        variant_obj = None

                if sv_len and variant_obj:
                    if variant_obj.sv_len < sv_len:
                        variant_obj = None

                if variant_obj:
                    skip_index += 1

                    if skip_index <= limit:
                        result.append(variant_obj)
                    else:
                        break
            else:
                skip_index += 1

        return Results(result, len(result))

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

        if filters.get('range'):
            range_str = "{0}:{1}-{2}".format(
                filters['range']['chromosome'],
                filters['range']['start'],
                filters['range']['end'])

            vcf = VCF(vcf_file_path)
            handle = vcf(range_str)
        else:
            handle = VCF(vcf_file_path)

        for variant in handle:
            variant_line = str(variant)
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
                yield variant

    def _format_variants(self, variant, index, case_obj, add_all_info=False):
        """Return a Variant object

        Format variant make a variant that includes enough information for
        the variant view.
        If add_all_info then all transcripts will be parsed

        Args:
            variant (cython2.Variant): A variant object
            index (int): The index of the variant
            case_obj (puzzle.models.Case): A case object

        """
        header_line = self.head.header
        # Get the individual ids for individuals in vcf file
        vcf_individuals = set([ind_id for ind_id in self.head.individuals])

        #Create a info dict:
        info_dict = dict(variant.INFO)

        chrom = variant.CHROM
        if chrom.startswith('chr') or chrom.startswith('CHR'):
            chrom = chrom[3:]

        variant_obj = Variant(
                CHROM=chrom,
                POS=variant.POS,
                ID=variant.ID,
                REF=variant.REF,
                ALT=variant.ALT[0],
                QUAL=variant.QUAL,
                FILTER=variant.FILTER,
            )
        variant_obj._set_variant_id()

        logger.debug("Creating a variant object of variant {0}".format(
            variant_obj.variant_id))

        variant_obj.index = index
        logger.debug("Updating index to: {0}".format(
            index))

        ########### Get the coordinates for the variant ##############
        variant_obj.start = variant.start
        variant_obj.stop = variant.end

        #SV variants needs to be handeled a bit different since the can be huge
        #it would take to much power to parse all vep/snpeff entrys for these.
        if self.variant_type == 'sv':
            variant_obj.stop = int(info_dict.get('END', variant_obj.POS))
            self._add_sv_coordinates(variant_obj)
            variant_obj.sv_type = info_dict.get('SVTYPE')

            # Special for FindSV software:
            # SV specific tag for number of occurances
            occurances = info_dict.get('OCC')
            if occurances:
                logger.debug("Updating occurances to: {0}".format(
                    occurances))
                variant_obj['occurances'] = float(occurances)
                variant_obj.add_frequency('OCC', occurances)

        else:
            self._add_thousand_g(variant_obj, info_dict)
            self._add_cadd_score(variant_obj, info_dict)
            self._add_genetic_models(variant_obj, info_dict)
            self._add_transcripts(variant_obj, info_dict)
            self._add_exac(variant_obj, info_dict)
            
        self._add_hgnc_symbols(variant_obj)

        if add_all_info:
            self._add_genotype_calls(variant_obj, str(variant), case_obj)
            self._add_compounds(variant_obj, info_dict)
            self._add_gmaf(variant_obj, info_dict)
            self._add_genes(variant_obj)


        ##### Add consequences ####
        self._add_consequences(variant_obj, str(variant))
        self._add_most_severe_consequence(variant_obj)
        self._add_impact_severity(variant_obj)
        self._add_rank_score(variant_obj, info_dict)
        variant_obj.set_max_freq()
        return variant_obj

