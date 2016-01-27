# -*- coding: utf-8 -*-
"""
puzzle.plugins.sql.store
~~~~~~~~~~~~~~~~~~
"""
import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql.expression import ClauseElement

from puzzle.models import Case as BaseCase
from puzzle.models.sql import (BASE, Case, Individual)

logger = logging.getLogger(__name__)


class Store(object):

    """SQLAlchemy-based database object.
    .. note::
        For testing pourposes use ``:memory:`` as the ``path`` argument to
        set up in-memory (temporary) database.
    Args:
        uri (Optional[str]): path/URI to the database to connect to
        debug (Optional[bool]): whether to output logging information
    Attributes:
        uri (str): path/URI to the database to connect to
        engine (class): SQLAlchemy engine, defines what database to use
        session (class): SQLAlchemy ORM session, manages persistance
        query (method): SQLAlchemy ORM query builder method
        classes (dict): bound ORM classes
    """

    def __init__(self, uri=None, debug=False):
        super(Store, self).__init__()
        self.uri = uri
        if uri:
            self.connect(uri, debug=debug)

        # ORM class shortcuts to enable fetching models dynamically
        # self.classes = {'gene': Gene, 'transcript': Transcript,
        #                 'exon': Exon, 'sample': Sample}

    def connect(self, db_uri, debug=False):
        """Configure connection to a SQL database.

        Args:
            db_uri (str): path/URI to the database to connect to
            debug (Optional[bool]): whether to output logging information
        """
        kwargs = {'echo': debug, 'convert_unicode': True}
        # connect to the SQL database
        if 'mysql' in db_uri:
            kwargs['pool_recycle'] = 3600
        elif '://' not in db_uri:
            logger.debug("detected sqlite path URI: {}".format(db_uri))
            db_path = os.path.abspath(os.path.expanduser(db_uri))
            db_uri = "sqlite:///{}".format(db_path)

        self.engine = create_engine(db_uri, **kwargs)
        logger.debug('connection established successfully')
        # make sure the same engine is propagated to the BASE classes
        BASE.metadata.bind = self.engine
        # start a session
        self.session = scoped_session(sessionmaker(bind=self.engine))
        # shortcut to query method
        self.query = self.session.query
        return self

    @property
    def dialect(self):
        """Return database dialect name used for the current connection.
        Dynamic attribute.
        Returns:
            str: name of dialect used for database connection
        """
        return self.engine.dialect.name

    def set_up(self):
        """Initialize a new database with the default tables and columns.
        Returns:
            Store: self
        """
        # create the tables
        BASE.metadata.create_all(self.engine)
        return self

    def tear_down(self):
        """Tear down a database (tables and columns).
        Returns:
            Store: self
        """
        # drop/delete the tables
        BASE.metadata.drop_all(self.engine)
        return self

    def save(self):
        """Manually persist changes made to various elements. Chainable.

        Returns:
            Store: ``self`` for chainability
        """
        # commit/persist dirty changes to the database
        self.session.flush()
        self.session.commit()
        return self

    def add_case(self, case_obj, vtype='snv', mode='vcf', ped_svg=None):
        """Load a case with individuals.

        Args:
            case_obj (puzzle.models.Case): initialized case model
        """
        new_case = Case(case_id=case_obj['case_id'],
                        name=case_obj['name'],
                        variant_source=case_obj['variant_source'],
                        variant_type=vtype,
                        variant_mode=mode,
                        pedigree=ped_svg)

        # build individuals
        inds = [Individual(
            ind_id=ind['ind_id'],
            mother=ind['mother'],
            father=ind['father'],
            sex=ind['sex'],
            phenotype=ind['phenotype'],
            ind_index=ind['index'],
            variant_source=ind['variant_source'],
            bam_path=ind['bam_path'],
        ) for ind in case_obj['individuals']]

        new_case.individuals = inds
        self.session.add(new_case)
        self.save()
        return new_case

    def case(self, case_id):
        """Fetch a case from the database."""
        case_obj = self.query(Case).filter_by(case_id=case_id).first()
        if case_obj is None:
            case_obj = BaseCase(case_id='unknown')
        return case_obj
