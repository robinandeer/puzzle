import logging
import sqlite3

from contextlib import closing

from .constants import SCHEMA

logger = logging.getLogger(__name__)

def connect_database(db_path):
    """Connect to the event database"""
    logger.info("Connecting to database {0}".format(db_path))
    return sqlite3.connect(db_path)

def init_db(db_path):
    """Build the sqlite database"""
    logger.info("Creating database")
    with closing(connect_database(db_path)) as db:
        with open(SCHEMA, 'r') as f:
            db.cursor().executescript(f.read())
        db.commit()
    return