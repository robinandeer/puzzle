# -*- coding: utf-8 -*-
import logging
from puzzle.models import (Case, Individual)

logger = logging.getLogger(__name__)

class Plugin(object):
    """docstring for Plugin"""
    def __init__(self):
        super(Plugin, self).__init__()
        self.db = None
        self.puzzle_db = None
        self.individuals = None
        self.case_obj = None
        self.variant_type = 'snv'
        self.can_filter_frequency = False
        self.can_filter_cadd = False
        self.can_filter_consequence = False
        self.can_filter_gene = False
        self.can_filter_inheritance = False
        self.can_filter_sv = False

    def init_app(self, app):
        """Initialize plugin via Flask."""
        self.root_path = app.config['PUZZLE_ROOT']
        self.pattern = app.config['PUZZLE_PATTERN']

    def cases(self, pattern=None):
        """Return all cases."""
        raise NotImplementedError

    def variants(self, case_id, skip=0, count=30, filters=None):
        """Return count variants for a case.

        """
        raise NotImplementedError

    def variant(self, variant_id):
        """Return a specific variant."""
        raise NotImplementedError

    def load_case(self, case_lines=None, bam_paths=None):
        """Load a case to the database"""
        raise NotImplementedError

    def connect(self, db_name, host='localhost', port=27017, username=None,
                password=None):
        """Connect to a database

            For vcf and gemini this is the database with cases and comments.
        """
        raise NotImplementedError

    def _get_individual_object(self, ind_id, case_id, mother=None, father=None,
                        sex=None, phenotype=None, index=None, bam_path=None):
        """Create and return an Individual object

            Args:
                ind_id(str)
                case_id(str)
                mother(str)
                father(str)
                sex(str)
                phenotype(str)
                variant_source(str): Path to variant source
                index(int)
                bam_path(str)

            Returns:
                individual(Individual)

        """
        individual = Individual(
                ind_id=ind_id,
                case_id=case_id,
                mother=mother,
                father=father,
                sex=str(sex),
                phenotype=str(phenotype),
                bam_path=None
        )
        return individual

    def _get_case_object(self, case_id, variant_source=None, name=None):
        """Create and return a Case object

            Args:
                case_id(str)
                variant_source(str)
                name(str)
        """
        case = Case(
            case_id=case_id,
            variant_source=variant_source,
            name=name or case_id
        )
        return case
