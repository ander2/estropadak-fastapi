from .db_connection import get_db_connection
from app.config import config


class YearsDAO:
    @staticmethod
    def get_years_from_db():
        with get_db_connection() as database:
            res = database.get_document(config["DBNAME"], 'years')
            years = res.get_result()
            return years

    @staticmethod
    def update_years_into_db(years, league):
        with get_db_connection() as database:
            res = database.get_document(config["DBNAME"], 'years')
            doc = res.get_result()
            if league:
                doc[league] = years
            else:
                doc = years
            database.put_document(config["DBNAME"], 'years', doc, rev=doc["_rev"])


def get_active_year():
    with get_db_connection() as database:
        res = database.get_document(config["DBNAME"], 'active_year')
        doc = res.get_result()
        return doc['year']
