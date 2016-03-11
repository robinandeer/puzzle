# -*- coding: utf-8 -*-
"""
puzzle.plugins.sql.store
~~~~~~~~~~~~~~~~~~
"""
import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from puzzle.models.sql import BASE
from puzzle.plugins import VcfPlugin, Plugin

from .mixins import ActionsMixin, CaseMixin, VariantMixin

try:
    from puzzle.plugins import GeminiPlugin
except ImportError as e:
    pass

logger = logging.getLogger(__name__)


class Store(Plugin, CaseMixin, VariantMixin, ActionsMixin):

    """SQLAlchemy-based database object.

    .. note::
        For testing pourposes use ``:memory:`` as the ``path`` argument to
        set up in-memory (temporary) database.

    Args:
        uri (Optional[str]): path/URI to the database to connect to
        debug (Optional[bool]): whether to output logging information
        phenomizer_auth (Optional[tuple]): username and password

    Attributes:
        uri (str): path/URI to the database to connect to
        engine (class): SQLAlchemy engine, defines what database to use
        session (class): SQLAlchemy ORM session, manages persistance
        query (method): SQLAlchemy ORM query builder method
        classes (dict): bound ORM classes
    """

    def __init__(self, uri=None, debug=False, vtype='snv',
                 phenomizer_auth=None):
        super(Store, self).__init__()
        self.uri = uri
        if uri:
            self.connect(uri, debug=debug)
        self.variant_type = vtype
        self.phenomizer_auth = phenomizer_auth

        # ORM class shortcuts to enable fetching models dynamically
        # self.classes = {'gene': Gene, 'transcript': Transcript,
        #                 'exon': Exon, 'sample': Sample}

    def init_app(self, app):
        pass

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

    def set_up(self, reset=False):
        """Initialize a new database with the default tables and columns.
        Returns:
            Store: self
        """
        if reset:
            self.tear_down()

        logger.info("Creating database")
        # create the tables
        BASE.metadata.create_all(self.engine)
        return self

    def tear_down(self):
        """Tear down a database (tables and columns).
        Returns:
            Store: self
        """
        # drop/delete the tables
        logger.info('resetting database...')
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

    def select_plugin(self, case_obj):
        """Select and initialize the correct plugin for the case."""
        if case_obj.variant_mode == 'vcf':
            logger.debug("Using vcf plugin")
            plugin = VcfPlugin(case_obj.variant_type)
        elif case_obj.variant_mode == 'gemini':
            logger.debug("Using gemini plugin")
            plugin = GeminiPlugin(case_obj.variant_type)
        
        #Add case to plugin
        plugin.add_case(case_obj)

        self.variant_type = case_obj.variant_type

        case_id = case_obj.case_id
        return plugin, case_id
