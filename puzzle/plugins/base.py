# -*- coding: utf-8 -*-


class Plugin(object):
    """docstring for Plugin"""
    def __init__(self):
        super(Plugin, self).__init__()
        self.db = None
        self.puzzle_db = None
        self.individuals = None
        self.case_obj = None
        self.mode = 'snv'
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
    
    def connect(self, db_name, host='localhost', port=27017, username=None
                password=None):
        """Connect to a database
        
            For vcf and gemini this is the database with cases and comments.
        """
        raise NotImplementedError
