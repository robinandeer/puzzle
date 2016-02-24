import logging

from gemini import GeminiQuery

from puzzle.plugins import BaseVariantMixin

from puzzle.models import (Compound, Variant, Gene, Genotype, Transcript,)
from puzzle.utils import (get_most_severe_consequence, get_omim_number,
                          get_cytoband_coord)


logger = logging.getLogger(__name__)

class VariantMixin(BaseVariantMixin):
    """Class to store variant specific functions for gemini plugin"""


    def build_gemini_query(self, query, extra_info):
        """Append sql to a gemini query

        Args:
            query(str): The gemini query
            extra_info(str): The text that should be added

        Return:
            extended_query(str)
        """
        if 'WHERE' in query:
            return "{0} AND {1}".format(query, extra_info)
        else:
            return "{0} WHERE {1}".format(query, extra_info)

    def variants(self, case_id, skip=0, count=30, filters=None):
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

        """
        filters = filters or {}
        logger.debug("Looking for variants in {0}".format(case_id))

        limit = count + skip

        gemini_query = filters.get('gemini_query') or "SELECT * from variants"

        any_filter = False

        if filters.get('frequency'):
            frequency = filters['frequency']

            extra_info = "(max_aaf_all < {0} or max_aaf_all is"\
                         " Null)".format(frequency)
            gemini_query = self.build_gemini_query(gemini_query, extra_info)

        if filters.get('cadd'):
            cadd_score = filters['cadd']

            extra_info = "(cadd_scaled > {0})".format(cadd_score)
            gemini_query = self.build_gemini_query(gemini_query, extra_info)

        if filters.get('gene_ids'):
            gene_list = [gene_id.strip() for gene_id in filters['gene_ids']]

            gene_string = "gene in ("
            for index, gene_id in enumerate(gene_list):
                if index == 0:
                    gene_string += "'{0}'".format(gene_id)
                else:
                    gene_string += ", '{0}'".format(gene_id)
            gene_string += ")"

            gemini_query = self.build_gemini_query(gemini_query, gene_string)


        if filters.get('impact_severities'):
            severities_list = [severity.strip()
                    for severity in filters['impact_severities']]
            severity_string = "impact_severity in ("
            for index, severity in enumerate(severities_list):
                if index == 0:
                    severity_string += "'{0}'".format(severity)
                else:
                    severity_string += ", '{0}'".format(severity)
            severity_string += ")"

            gemini_query = self.build_gemini_query(gemini_query, severity_string)

        filtered_variants = self._variants(
            case_id=case_id,
            gemini_query=gemini_query,
            filters=filters,
        )

        if filters.get('consequence'):
            consequences = set(filters['consequence'])

            filtered_variants = (variant for variant in filtered_variants if
                set(variant.consequences).intersection(consequences))

        if filters.get('sv_len'):
            sv_len = int(filters['sv_len'])
            filters = (variant for variant in filtered_variants if
                variant.sv_len >= sv_len)

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
            index = ind.ind_index
            individuals.append(Genotype(
                sample_id=ind.ind_id,
                genotype=gemini_variant['gts'][index],
                case_id=ind.case_id,
                phenotype=ind.phenotype,
                ref_depth=gemini_variant['gt_ref_depths'][index],
                alt_depth=gemini_variant['gt_alt_depths'][index],
                depth=gemini_variant['gt_depths'][index],
                genotype_quality=gemini_variant['gt_quals'][index]
            ))

        return individuals

    def _get_hgnc_symbols(self, gemini_variant):
        """Get the hgnc symbols for all transcripts in a variant

        Right now this function only use the
            Args:
                gemini_variant (GeminiQueryRow): The gemini variant

            Returns:
                hgnc_symbols(list(str)): List hgnc symbols

        """

        # query = "SELECT * from variant_impacts WHERE variant_id = {0}".format(
        #     gemini_variant['variant_id']
        # )
        # gq = GeminiQuery(self.db)
        # gq.run(query)

        # hgnc_symbols = set([transcript['gene']])
        hgnc_symbols = [gemini_variant['gene']]

        return hgnc_symbols

    def _get_transcripts(self, gemini_variant):
        """Return a Transcript object

        Go through all transcripts found for the variant

            Args:
                gemini_variant (GeminiQueryRow): The gemini variant

            Yields:
                transcript (puzzle.models.Transcript)

        """
        query = "SELECT * from variant_impacts WHERE variant_id = {0}".format(
            gemini_variant['variant_id']
        )

        gq = GeminiQuery(self.db)
        gq.run(query)

        for genimi_transcript in gq:
            transcript = Transcript(
                hgnc_symbol=genimi_transcript['gene'],
                transcript_id=genimi_transcript['transcript'],
                consequence=genimi_transcript['impact_so'],
                biotype=genimi_transcript['biotype'],
                polyphen=genimi_transcript['polyphen_pred'],
                sift=genimi_transcript['sift_pred'],
                HGVSc=genimi_transcript['codon_change'],
                HGVSp=genimi_transcript['aa_change']
                )
            yield transcript

    def _variants(self, case_id, gemini_query, filters=None):
        """Return variants found in the gemini database

            Args:
                case_id (str): The case for which we want to see information
                gemini_query (str): What variants should be chosen
                filters (dict): A dictionary with filters

            Yields:
                variant_obj (dict): A Variant formatted dictionary
        """

        gq = GeminiQuery(self.db)

        gq.run(gemini_query)

        individuals = []
        # Get the individuals for the case
        case = self.case(case_id)
        for individual in case.individuals:
            individuals.append(individual)

        index = 0
        for gemini_variant in gq:
            # Check if variant is non ref in the individuals
            variant = None
            if self.variant_type == 'sv':
                index += 1
                variant = self._format_sv_variants(
                        gemini_variant=gemini_variant,
                        index=index,
                        filters=filters
                        )
            else:
                if self._is_variant(gemini_variant, individuals):
                    index += 1
                    logger.debug("Updating index to: {0}".format(index))

                    variant = self._format_variants(
                        gemini_variant=gemini_variant,
                        index=index,
                        filters=filters
                        )

            if variant:

                yield variant

    def _get_puzzle_variant(self, gemini_variant, index):
        """Take a gemini variant and return a basic puzzle variant

            For the overview we only need limited variant information
        """
        variant_dict = {
            'CHROM':gemini_variant['chrom'].lstrip('chrCHR'),
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

        #Add the most severe consequence
        variant['most_severe_consequence'] = gemini_variant['impact_so']

        #Add the impact severity
        variant['impact_severity'] = gemini_variant['impact_severity']

        max_freq = gemini_variant['max_aaf_all']
        if max_freq:
            variant.set_max_freq(max_freq)

        #### Check the impact annotations ####
        if gemini_variant['cadd_scaled']:
            variant['cadd_score'] = gemini_variant['cadd_scaled']

        return variant

    def _format_variants(self, gemini_variant, index=0, filters=None):
        """Format the variant for the variants view

            We want to have it's own function for doing this since it includes
            much less information than in the variant view

            Args:
                gemini_variant (GeminiQueryRow): The gemini variant
                ind_objs (list(puzzle.models.individual))
                index(int): The index of the variant

            Returns:
                variant (dict): A Variant object
        """
        variant = self._get_puzzle_variant(gemini_variant, index)

        if filters.get('consequence'):
            #If filter for consequence we need to parse the transcript
            #information
            if len(filters['consequence']) > 0:
                for transcript in self._get_transcripts(gemini_variant):
                    variant.add_transcript(transcript)

                self._add_consequences(variant)
        else:
            for hgnc_symbol in self._get_hgnc_symbols(gemini_variant):
                variant.add_transcript(Transcript(
                                hgnc_symbol=hgnc_symbol,
                                transcript_id='dummy',
                                consequence='dummy')
                                )

        for gene in self._get_genes(variant):
            variant.add_gene(gene)


        return variant

    def _format_sv_variants(self, gemini_variant, index=0, filters=None):
        """Format the variant for the sv variants view

            We want to have it's own function for doing this since it includes
            much less information than in the variant view

            Args:
                gemini_variant (GeminiQueryRow): The gemini variant
                ind_objs (list(puzzle.models.individual))
                index(int): The index of the variant

            Returns:
                variant (dict): A Variant object
        """
        variant = self._get_puzzle_variant(gemini_variant, index)

        variant.sv_type = gemini_variant['sub_type']
        variant.stop = int(gemini_variant['end'])

        ##TODO this whould be replaced with a faster lookup via phizz
        for transcript in self._get_transcripts(gemini_variant):
            variant.add_transcript(transcript)
        ##TODO same as above
        for gene in self._get_genes(variant):
            variant.add_gene(gene)

        self._add_sv_coordinates(variant)

        return variant

    def _format_variant(self, gemini_variant, individual_objs, index=0):
        """Make a puzzle variant from a gemini variant

            Args:
                gemini_variant (GeminiQueryRow): The gemini variant
                individual_objs (list(dict)): A list of Individuals
                index(int): The index of the variant

            Returns:
                variant (dict): A Variant object
        """
        variant = self._get_puzzle_variant(gemini_variant, index)

        ### GENOTYPE ANNOATTIONS ###
        #Get the genotype info
        individual_genotypes = self._get_genotypes(
            gemini_variant=gemini_variant,
            individual_objs=individual_objs
            )

        #Add the genotype info to the variant
        for individual in individual_genotypes:
            # Add the genotype calls to the variant
            variant.add_individual(individual)

        ### POSITON ANNOATTIONS ###
        variant.start = int(variant.POS)

        #Add the sv specific coordinates
        if self.variant_type == 'sv':
            variant.sv_type = gemini_variant['sub_type']
            variant.stop = int(gemini_variant['end'])
            self._add_sv_coordinates(variant)

        ### Consequence and region annotations
        #Add the transcript information
        for transcript in self._get_transcripts(gemini_variant):
            variant.add_transcript(transcript)

        #Add the genes based on the hgnc symbols
        hgnc_symbols = (transcript.hgnc_symbol for transcript in variant.transcripts)
        for gene in self._get_genes(variant):
            variant.add_gene(gene)


        # We use the prediction in text
        polyphen = gemini_variant['polyphen_pred']
        if polyphen:
            variant.add_severity('Polyphen', polyphen)

        # We use the prediction in text
        sift = gemini_variant['sift_pred']
        if sift:
            variant.add_severity('SIFT', sift)


        #### Frequencies ####
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

        return variant

    def _is_variant(self, gemini_variant, ind_objs):
        """Check if the variants is a variation in any of the individuals

        This means that at least one of the individuals should have the
        alternative symbol.

        Args:
            gemini_variant (GeminiQueryRow): The gemini variant
            ind_objs (list(puzzle.models.individual)): A list of individuals to check

        Returns:
            bool : If any of the individuals has the variant
        """

        alt = gemini_variant['alt']
        indexes = (ind.ind_index for ind in ind_objs)
        #Merge all genotypes into one string
        genotypes = "".join([gemini_variant['gts'][index] for index in indexes])
        #Check if the alternative allele is found within the genotypes
        if alt in genotypes:
            return True

        return False
