import logging

from ibm_cloud_sdk_core import ApiException

from .db_connection import get_db_connection
from app.config import config, DEFAULT_LOGGER


logger = logging.getLogger(DEFAULT_LOGGER)


def get_sailkapena_by_league_year(league, year, category):
    with get_db_connection() as database:
        if league in ['gbl', 'bbl', 'btl', 'gtl']:
            _category = category.replace(' ', '_').lower()
            key = 'rank_{}_{}_{}'.format(league.upper(), year, _category)
        else:
            key = 'rank_{}_{}'.format(league.upper(), year)
        try:
            res = database.get_document(config["DBNAME"], key)
            doc = res.get_result()
        except ApiException:
            return None
        result = {
            'total': 1,
            'docs': [doc]
        }
        return result


def get_sailkapena_by_league(league):
    league = league.upper()
    key = 'rank_{}'.format(league)
    endkey = "{}z".format(key)

    start = key
    end = endkey
    with get_db_connection() as database:
        try:
            result = []
            res = database.post_view(
                config["DBNAME"],
                "estropadak",
                "rank",
                start_key=start,
                end_key=end,
                reduce=True,
            )
            ranks = res.get_result()
            count = ranks.get('rows', [{'value': 0}])[0]['value']
            if count > 0:
                res = database.post_view(
                    config["DBNAME"],
                    "estropadak",
                    "rank",
                    start_key=start,
                    end_key=end,
                    include_docs=True,
                    reduce=False,
                )
                ranks = res.get_result()
                for rank in ranks['rows']:
                    result.append(rank['doc'])
        except KeyError:
            return {'error': 'Estropadak not found'}, 404
        return {
            'total': count,
            'docs': result
        }


def get_sailkapena_by_id(id: str):
    with get_db_connection() as database:
        try:
            res = database.get_document(config["DBNAME"], id)
            doc = res.get_result()
            return doc
        except KeyError:
            return None  # {'error': 'Sailkapena not found'}, 404


def get_sailkapenak_by_teams(league: str, year: str, teams: list[str]):
    with get_db_connection() as database:
        try:
            doc_count = 0
            result = []
            for team in teams:
                key = [team, league, year]
                res = database.post_view(
                    config["DBNAME"],
                    "sailkapenak",
                    "by_team",
                    key=key,
                    include_docs=False,
                    reduce=True,
                )
                sailkapenak_count = res.get_result()
                if len(sailkapenak_count['rows']) > 0:
                    doc_count = doc_count + sailkapenak_count.get('rows', [{'value': 0}])[0]['value']
                    sailkapenak = database.post_view(
                        config["DBNAME"],
                        "sailkapenak",
                        "by_team",
                        key=key,
                        include_docs=False,
                        reduce=False,
                    )
                    for emaitza in sailkapenak['rows']:
                        doc = database[emaitza['id']]
                        for name, stat in doc['stats'].items():
                            if name == team:
                                doc['stats'] = [{
                                    "name": team,
                                    "value": stat
                                }]
                                break
                        result.append(doc)
            logger.debug(result)
            return {
                'total': doc_count,
                'docs': result
            }
        except KeyError:
            return None  # {'error': 'Sailkapena not found'}, 404


def insert_sailkapena_into_db(sailkapena):
    with get_db_connection() as database:
        res = database.post_document(config["DBNAME"], sailkapena)
        doc = res.get_result()
        return doc


def update_sailkapena_into_db(sailkapena_id, sailkapena):
    with get_db_connection() as database:
        res = database.get_document(config["DBNAME"], sailkapena_id)
        doc = res.get_result()
        doc["stats"] = sailkapena["stats"]
        database.put_document(config["DBNAME"], sailkapena_id, doc, rev=doc["_rev"])
        return doc


def delete_sailkapena_from_db(sailkapena_id):
    with get_db_connection() as database:
        try:
            res = database.get_document(config["DBNAME"], sailkapena_id)
            doc = res.get_result()
            database.delete_document(config["DBNAME"], sailkapena_id, rev=doc["_rev"])
        except ApiException:
            logger.info(f"Sailkapenak document with id {sailkapena_id} not found")
