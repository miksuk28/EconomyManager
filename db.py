import psycopg2
import psycopg2.extras
from config import db_config as conf

class DatabaseConnection:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=conf["host"],
            port=conf["port"],
            database=conf["database"],
            user=conf["user"],
            password=conf["password"],
            cursor_factory=psycopg2.extras.RealDictCursor
        )


    def _list_and_dictify(self, items, one=False):
        if items is None:
            return None

        elif one:
            return dict(items)

        new_list = []
        for row in items:
            new_list.append(dict(row))

        return new_list