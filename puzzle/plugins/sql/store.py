# -*- coding: utf-8 -*-
"""
puzzle.plugins.sql.store
~~~~~~~~~~~~~~~~~~
"""
import os

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql.expression import ClauseElement

from puzzle.models.sql import (BASE, Case, Individual)


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
            # expect only a path to a sqlite database
            db_path = os.path.abspath(os.path.expanduser(db_uri))
            db_uri = "sqlite:///{}".format(db_path)

        self.engine = create_engine(db_uri, **kwargs)
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