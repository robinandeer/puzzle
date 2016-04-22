import logging

from puzzle.models import Genotype

logger = logging.getLogger(__name__)


class GenotypeExtras(object):
    """Class to store methods that deals with genotyping"""

    def _add_genotypes(self, variant_obj, gemini_variant, case_id,
                       individual_objs):
        """Add the genotypes for a variant for all individuals

                Args:
                    variant_obj (puzzle.models.Variant)
                    gemini_variant (GeminiQueryRow): The gemini variant
                    case_id (str): related case id
                    individual_objs (list(dict)): A list of Individuals

        """
        for ind in individual_objs:
            index = ind.ind_index
            variant_obj.add_individual(Genotype(
                sample_id=ind.ind_id,
                genotype=gemini_variant['gts'][index],
                case_id=case_id,
                phenotype=ind.phenotype,
                ref_depth=gemini_variant['gt_ref_depths'][index],
                alt_depth=gemini_variant['gt_alt_depths'][index],
                depth=gemini_variant['gt_depths'][index],
                genotype_quality=gemini_variant['gt_quals'][index]
            ))
