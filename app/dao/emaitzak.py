import logging

from ibm_cloud_sdk_core import ApiException

from app.config import config
from ..dao.db_connection import get_db_connection
from ..dao.models.sailkapenak import SailkapenaDoc

logger = logging.getLogger('estropadak')

def get_emaitza_by_id(id):
    with get_db_connection() as database:
        try:
            res = database.get_document(config["DBNAME"], id)
            emaitza = res.get_result()
        except KeyError:
            emaitza = None
        return emaitza


def get_emaitzak_by_league_year(league, year, team=None):
    league = league.upper()
    if league.lower() == 'euskotren':
        league = league.lower()
    if year:
        start = [league, team, year]
        end = [league, team, year + 1]
    else:
        start = [league, team]
        end = [league, team + 'z']

    with get_db_connection() as database:
        emaitzak = database.get_view_result("emaitzak", "by_team",
                                            startkey=start,
                                            endkey=end,
                                            include_docs=False,
                                            reduce=False)
        result = []
        for emaitza in emaitzak:
            result.append(database[emaitza['id']])
        return result


def get_estropadak_by_team(team, league_id):
    start = [team]
    if league_id:
        start.append(league_id)
    end = ["{}z".format(team)]
    if league_id:
        end.append(league_id)
    with get_db_connection() as database:
        try:
            estropadak = database.view("estropadak/by_team",
                                        startkey=start,
                                        endkey=end,
                                        include_docs=True,
                                        reduce=False)
            result = []
            for estropada in estropadak.rows:
                result.append(estropada)
            return result
        except KeyError:
            return {'error': 'Estropadak not found'}, 404


def get_emaitzak(criteria: dict, page: int, count: int):
    start = page * count
    end = start + count
    docs = []
    total = 0
    if 'liga' in criteria:
        if criteria['liga'] == 'EUSKOTREN':
            criteria['liga'] = criteria['liga'].lower()
    with get_db_connection() as database:
        res = database.post_find(config["DBNAME"], criteria)
        emaitzak = res.get_result()
        try:
            total = len(emaitzak['docs'])
            docs = emaitzak['docs'][start:end]
        except IndexError:
            return {'error': 'Bad pagination'}, 400
        return (docs, total,)


def insert_emaitza_into_db(emaitza: SailkapenaDoc):
    emaitza_ = emaitza.dump_dict()
    logger.debug(emaitza_)
    with get_db_connection() as database:
        res = database.post_document(config["DBNAME"], emaitza_)
        document = res.get_result()
        return document is not None


def update_emaitza_into_db(emaitza_id, emaitza):
    emaitza_ = emaitza.dump_dict()
    with get_db_connection() as database:
        res = database.get_document(config["DBNAME"], emaitza_id)
        document = res.get_result()
        if document:
            document.update(emaitza_)
            database.put_document(config["DBNAME"], emaitza_id, document, rev=document["_rev"])
            return True
        else:
            return None


def delete_emaitza_from_db(emaitza_id):
    with get_db_connection() as database:
        try:
            res = database.get_document(config["DBNAME"], emaitza_id)
            document = res.get_result()
            if document:
                database.delete_document(config["DBNAME"], emaitza_id, rev=document["_rev"])
                return True
        except ApiException:
            logger.error(f'Emaitza document with id {emaitza_id} not found on deletion')
            return True
    return False
