import logging
import operator

from puzzle.models import (Compound)

logger = logging.getLogger(__name__)

class AnnotationExtras(object):
    """Mixin class to store methods that deals with parsing annotations"""
    
    def _add_compounds(self, variant_obj, info_dict):
        """Check if there are any compounds and add them to the variant
        
            The compounds that are added should be sorted on rank score
        """
        compound_list = []
        compound_entry = info_dict.get('Compounds')
        if compound_entry:
            for family_annotation in compound_entry.split(','):
                compounds = family_annotation.split(':')[-1].split('|')
                for compound in compounds:
                    splitted_compound = compound.split('>')

                    compound_score = None
                    if len(splitted_compound) > 1:
                        compound_id = splitted_compound[0]
                        compound_score = int(splitted_compound[-1])
                    
                    compound_list.append(Compound(
                        variant_id=compound_id,
                        combined_score=compound_score
                        )
                    )
        
        #Sort the compounds based on rank score
        compound_list.sort(key = operator.attrgetter('combined_score'), reverse=True)
        
        for compound in compound_list:
            variant_obj.add_compound(compound)

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
    