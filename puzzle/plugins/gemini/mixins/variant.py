import logging

from gemini import GeminiQuery
from gemini.gim import (DeNovo, AutoRec, AutoDom, CompoundHet)

from puzzle.plugins import BaseVariantMixin
from puzzle.plugins.constants import Results

from puzzle.models import (Compound, Variant, Gene, Genotype, Transcript,)
from puzzle.utils import (get_most_severe_consequence, get_omim_number,
                          get_cytoband_coord, build_gemini_query, Args)

from . import VariantExtras

logger = logging.getLogger(__name__)

class VariantMixin(BaseVariantMixin, VariantExtras):
    """Class to store variant specific functions for gemini plugin"""

    def variant(self, case_id, variant_id):
        """Return a specific variant.

            We solve this by building a gemini query and send it to _variants

            Args:
                case_id (str): Path to a gemini database
                variant_id (int): A gemini variant id

            Returns:
                variant_obj (dict): A puzzle variant

        """
        #Use the gemini id for fast lookup
        variant_id = int(variant_id)
        gemini_query = "SELECT * from variants WHERE variant_id = {0}".format(
            variant_id
        )

        individuals = []
        # Get the individuals for the case
        case_obj = self.case(case_id)
        for individual in case_obj.individuals:
            individuals.append(individual)

        self.db = case_obj.variant_source
        self.variant_type = case_obj.variant_type

        gq = GeminiQuery(self.db)
        gq.run(gemini_query)

        for gemini_variant in gq:
            variant = self._format_variant(
                case_id=case_id,
                gemini_variant=gemini_variant,
                individual_objs=individuals,
                index=gemini_variant['variant_id'],
                add_all_info = True
            )
            return variant

        return None

    def variants(self, case_id, skip=0, count=1000, filters=None):
        """Return count variants for a case.

        This function needs to have different behaviours based on what is asked
        for. It should allways try to give minimal information back to improve
        on speed. For example, if consequences are not asked for we will not
        build all transcripts. If not sv variants we will not build sv
        coordinates.
        So the minimal case is to just show what is asked for in the variants
        interface.

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
                    impact_severities: [] (list of consequences),
                    genetic_models [] (list of genetic models)
                }
            Returns:
                puzzle.constants.Results : Named tuple with variants and
                                           nr_of_variants

        """
        filters = filters or {}
        logger.debug("Looking for variants in {0}".format(case_id))

        limit = count + skip
        
        genetic_models = None
        if filters.get('genetic_models'):
            gemini_query = build_gemini_query(filters, add_where=False)
        else:
            gemini_query = build_gemini_query(filters)

        any_filter = False

        filtered_variants = self._variants(
            case_id=case_id,
            gemini_query=gemini_query,
            genetic_models=filters.get('genetic_models')
        )

        if filters.get('consequence'):
            consequences = set(filters['consequence'])

            filtered_variants = (variant for variant in filtered_variants if
                set(variant.consequences).intersection(consequences))

        if filters.get('impact_severities'):
            severities = set([severity.strip()
                    for severity in filters['impact_severities']])
            new_filtered_variants = []
            filtered_variants = (variant for variant in filtered_variants if
                set([variant.impact_severity]).intersection(severities))

        if filters.get('sv_len'):
            sv_len = int(filters['sv_len'])
            filtered_variants = (variant for variant in filtered_variants if
                variant.sv_len >= sv_len)

        variants = []
        for index, variant_obj in enumerate(filtered_variants):
            if index >= skip:
                if index < limit:
                    variants.append(variant_obj)
                else:
                    break

        return Results(variants, len(variants))

    def _variants(self, case_id, gemini_query, genetic_models=None):
        """Return variants found in the gemini database

            Args:
                case_id (str): The case for which we want to see information
                gemini_query (str): What variants should be chosen
                filters (dict): A dictionary with filters

            Yields:
                variant_obj (dict): A Variant formatted dictionary
        """
        individuals = []
        # Get the individuals for the case
        case_obj = self.case(case_id)
        for individual in case_obj.individuals:
            individuals.append(individual)

        self.db = case_obj.variant_source
        self.variant_type = case_obj.variant_type
        
        variant_generators = []
        
        models_found = []
        if genetic_models:
            for genetic_model in genetic_models:
                
                if genetic_model in ['XR', 'XR_dn', 'XD', 'XD_dn']:
                    chrom_x_string = "chrom = 'chrX'"
                    if not gemini_query:
                        gemini_query = chrom_x_string
                    else:
                        gemini_query = "{0} AND {1}".format(gemini_query, chrom_x_string)
                    
                if genetic_model in ['AR_hom', 'AR_hom_dn', 'XR', 'XR_dn']:
                    results = AutoRec(Args(db=self.db,
                             columns="*",
                             filter=gemini_query,
                             families=case_id))
                    variant_generators.append(results.report_candidates())
                    models_found = ['AR_hom']
                elif genetic_model in ['AD', 'XD']:
                    results = AutoDom(Args(db=self.db,
                             columns="*",
                             filter=gemini_query,
                             families=case_id))
                    variant_generators.append(results.report_candidates())
                    models_found = [genetic_model]
                elif genetic_model in ['AD_dn', 'XD_dn']:
                    results = DeNovo(Args(db=self.db,
                             columns="*",
                             filter=gemini_query,
                             families=case_id))
                    variant_generators.append(results.report_candidates())
                    models_found = ['AD_dn']
                elif genetic_model in ['AR_comp', 'AR_comp_dn']:
                    results = CompoundHet(Args(db=self.db,
                             columns="*",
                             filter=gemini_query,
                             families=case_id))
                    models_found = ['AR_comp']
                    variant_generators.append(results.report_candidates())
                    
        
        else:
            gq = GeminiQuery(self.db)
            gq.run(gemini_query)
            variant_generators.append(gq)

        index = 0
        for variants in variant_generators:
            for gemini_variant in variants:
                variant = None
                
                if not genetic_models:
                    # Check if variant is non ref in the individuals
                    is_variant = self._is_variant(gemini_variant, individuals)
                    
                    if self.variant_type == 'snv' and not is_variant:
                        variant = None
            
                    else:
                        index += 1
                        logger.debug("Updating index to: {0}".format(index))
                        variant = self._format_variant(
                                case_id=case_id,
                                gemini_variant=gemini_variant,
                                individual_objs=individuals,
                                index=index,
                                models_found=models_found
                                )
                    
                else:
                    index += 1
                    is_variant = True
                    variant = self.variant(case_id, gemini_variant['variant_id'])
                    variant['index'] = index
            
                if variant:
            
                    yield variant

    def _format_variant(self, case_id, gemini_variant, individual_objs,
                        index=0, add_all_info=False, models_found = []):
        """Make a puzzle variant from a gemini variant

            Args:
                case_id (str): related case id
                gemini_variant (GeminiQueryRow): The gemini variant
                individual_objs (list(dict)): A list of Individuals
                index(int): The index of the variant

            Returns:
                variant (dict): A Variant object
        """
        chrom = gemini_variant['chrom']
        
        if chrom.startswith('chr') or chrom.startswith('CHR'):
            chrom = chrom[3:]

        variant_dict = {
            'CHROM':chrom,
            'POS':str(gemini_variant['start']),
            'ID':gemini_variant['rs_ids'],
            'REF':gemini_variant['ref'],
            'ALT':gemini_variant['alt'],
            'QUAL':gemini_variant['qual'],
            'FILTER':gemini_variant['filter']
        }

        variant = Variant(**variant_dict)

        # Use the gemini id for fast search
        variant.update_variant_id(gemini_variant['variant_id'])
        logger.debug("Creating a variant object of variant {0}".format(
            variant.variant_id))

        variant['index'] = index
        # Add the most severe consequence
        self._add_most_severe_consequence(variant, gemini_variant)

        #Add the impact severity
        self._add_impact_severity(variant, gemini_variant)
        ### POSITON ANNOATTIONS ###
        variant.start = int(gemini_variant['start'])
        variant.stop = int(gemini_variant['end'])

        #Add the sv specific coordinates
        if self.variant_type == 'sv':
            variant.sv_type = gemini_variant['sub_type']
            variant.stop = int(gemini_variant['end'])
            self._add_sv_coordinates(variant)

        else:
            ### Consequence and region annotations
            #Add the transcript information
            self._add_thousand_g(variant, gemini_variant)
            self._add_exac(variant, gemini_variant)
            self._add_gmaf(variant, gemini_variant)
            #### Check the impact annotations ####
            if gemini_variant['cadd_scaled']:
                variant.cadd_score = gemini_variant['cadd_scaled']

            # We use the prediction in text
            polyphen = gemini_variant['polyphen_pred']
            if polyphen:
                variant.add_severity('Polyphen', polyphen)

            # We use the prediction in text
            sift = gemini_variant['sift_pred']
            if sift:
                variant.add_severity('SIFT', sift)
        
        ### GENOTYPE ANNOATTIONS ###
        #Get the genotype info
        if add_all_info:
            self._add_transcripts(variant, gemini_variant)
            self._add_genotypes(variant, gemini_variant, case_id, individual_objs)
            self._add_genes(variant)

        self._add_consequences(variant, gemini_variant)
        self._add_hgnc_symbols(variant, gemini_variant)
        variant.genetic_models = models_found

        return variant

    def _is_variant(self, gemini_variant, ind_objs):
        """Check if the variant is a variation in any of the individuals

        Args:
            gemini_variant (GeminiQueryRow): The gemini variant
            ind_objs (list(puzzle.models.individual)): A list of individuals to check

        Returns:
            bool : If any of the individuals has the variant
        """

        indexes = (ind.ind_index for ind in ind_objs)
        #Check if any individual have a heterozygous or homozygous variant call
        for index in indexes:
            gt_call = gemini_variant['gt_types'][index]
            if (gt_call == 1 or gt_call == 3):
                return True

        return False
