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
    