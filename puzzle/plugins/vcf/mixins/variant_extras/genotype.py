import logging

from vcftoolbox import Genotype

from puzzle.models import Genotype as puzzle_genotype

logger = logging.getLogger(__name__)

class GenotypeExtras(object):
    """Class to store methods that deals with genotyping"""

    def _add_genotype_calls(self, variant_obj, variant_line, case_obj):
        """Add the genotype calls for the variant

        Args:
            variant_obj (puzzle.models.Variant)
            variant_dict (dict): A variant dictionary
            case_obj (puzzle.models.Case)

        """
        variant_line = variant_line.split('\t')
        #if there is gt calls we have no individuals to add
        if len(variant_line) > 8:
            gt_format = variant_line[8].split(':')
            for individual in case_obj.individuals:
                sample_id = individual.ind_id
                index = individual.ind_index

                gt_call = variant_line[9+index].split(':')

                raw_call = dict(zip(gt_format, gt_call))

                genotype = Genotype(**raw_call)

                variant_obj.add_individual(puzzle_genotype(
                    sample_id = sample_id,
                    genotype = genotype.genotype,
                    case_id = case_obj.name,
                    phenotype = individual.phenotype,
                    ref_depth = genotype.ref_depth,
                    alt_depth = genotype.alt_depth,
                    genotype_quality = genotype.genotype_quality,
                    depth = genotype.depth_of_coverage,
                    supporting_evidence = genotype.supporting_evidence,
                    pe_support = genotype.pe_support,
                    sr_support = genotype.sr_support,
                ))
