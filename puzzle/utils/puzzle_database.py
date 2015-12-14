import dataset
from contextlib import closing

def connect_database(db_path):
    """Connect to the event database"""
    return sqlite3.connect(db_path)

def init_db(db_path, schema):
    """Build the sqlite database"""
    with closing(connect_database(db_path)) as db:
        with open(schema, 'r') as f:
            db.cursor().executescript(f.read())
        db.commit()
    return