import logging

from ibm_cloud_sdk_core import ApiException

from .db_connection import get_db_connection
from app.config import config

logger = logging.getLogger('estropadak')


def get_sailkapena_by_league_year(league, year, category):
    if league in ['gbl', 'bbl', 'btl', 'gtl']:
        _category = category.replace(' ', '_').lower()
        key = 'rank_{}_{}_{}'.format(league.upper(), year, _category)
    else:
        key = 'rank_{}_{}'.format(league.upper(), year)
    with get_db_connection() as database:
        try:
            logging.info(f'Getting {key}')
            res = database.get_document(config["DBNAME"], key)
            doc = res.get_result()
        except ApiException:
            logger.info(f'Sailkapena document not found for id {key}')
            return None
        return doc

def get_sailkapenak_by_league(league):
    key = 'rank_{}'.format(league.upper())
    league = league.upper()
    if league.lower() == 'euskotren':
        league = league.lower()
    endkey = "{}z".format(key)

    start = key
    end = endkey
    with get_db_connection() as database:
        try:
            res = database.post_view(
                config["DBNAME"],
                "estropadak",
                "rank",
                start_key=start,
                end_key=end,
                include_docs=True,
                reduce=False,
            )
            result = []
            ranks = res.get_result()
            for rank in ranks['rows']:
                result.append(rank['doc'])
            return result
        except ApiException:
            logger.info(f'Sailkapena document not found for id {key}')
            return {'error': 'Estropadak not found'}, 404
