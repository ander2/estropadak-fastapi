import logging

from ibm_cloud_sdk_core import ApiException

from .models.estropadak import Estropada
from .models.sailkapenak import Sailkapena
from .db_connection import get_db_connection
from app.config import DEFAULT_LOGGER, PAGE_SIZE, config
from typing import Dict, List

logger = logging.getLogger(DEFAULT_LOGGER)


def get_estropada_by_id(id):
    with get_db_connection() as database:
        try:
            res = database.get_document(config["DBNAME"], id)
            estropada = res.get_result()
            estropada['data'] = estropada['data'].replace(' ', 'T')
            if estropada['liga'] == 'euskotren':
                estropada['liga'] = estropada['liga'].upper()
        except TypeError:
            logging.error("Not found", exc_info=1)
            estropada = None
        except ApiException:
            logging.info(f"Estropada document with id {id} not found")
            estropada = None
        return estropada


def get_estropadak_by_league_year(league, year, page=0, count=PAGE_SIZE) -> Dict[str, List[Dict]]:
    logging.info("League:%s and year: %s", league, year)
    print("League:%s and year: %s", league, year)
    start = []
    end = []
    if league:
        league = league.upper()
        if league.lower() == 'euskotren':
            league = league.lower()
        start.append(league)
        end.append(league)

    if year:
        yearz = "{}".format(year)
        fyearz = "{}z".format(year)
        start.append(yearz)
        end.append(fyearz)
    else:
        end = ["{}z".format(league)]

    with get_db_connection() as database:
        try:
            logger.debug(f"Querying DB {start}-{end}")
            response = database.post_view(
                config["DBNAME"],
                "estropadak",
                "all",
                start_key=start,
                end_key=end,
                reduce=True,
            )
            res = response.get_result()
            rows = res['rows']
            logger.debug(rows)
            result = []
            if len(rows) > 0:
                doc_count = rows[0]['value']
            else:
                doc_count = 0
            if doc_count > 0:
                estropadak = database.post_view(
                    config["DBNAME"],
                    "estropadak",
                    "all",
                    start_key=start,
                    end_key=end,
                    include_docs=True,
                    reduce=False,
                    skip=count * page,
                    limit=count)
                res = estropadak.get_result()
                for row in res['rows']:
                    estropada = row['doc']
                    estropada['id'] = row['doc']['_id']
                    estropada['data'] = estropada['data'].replace(' ', 'T')
                    if estropada['liga'] == 'euskotren':
                        estropada['liga'] = estropada['liga'].upper()
                    result.append(estropada)

            return {
                'total': doc_count,
                'docs': result
            }
        except KeyError:
            return {'error': 'Estropadak not found'}, 404


def get_estropadak_by_year(year, page=0, count=20):
    start = [year]
    end = [year + 1]
    result = []
    with get_db_connection() as database:
        try:
            _count = database.post_view(
                config["DBNAME"],
                "estropadak",
                "by_year",
                start_key=start,
                end_key=end,
                reduce=True)
            res = _count.get_result()
            rows = res.get('rows', [{'value': 0}])
            if len(rows) > 0:
                doc_count = rows[0]['value']
            else:
                doc_count = 0
                result = []
            if doc_count > 0:
                estropadak = database.post_view(
                    config["DBNAME"],
                    "estropadak",
                    "by_year",
                    start_key=start,
                    end_key=end,
                    include_docs=True,
                    reduce=False,
                    skip=count*page,
                    limit=count)
                res = estropadak.get_result()
                for row in res['rows']:
                    logger.debug(row)
                    estropada = row['doc']
                    estropada['data'] = estropada['data'].replace(' ', 'T')
                    if estropada['liga'] == 'euskotren':
                        estropada['liga'] = estropada['liga'].upper()
                    result.append(estropada)
        except KeyError:
            return {'error': 'Estropadak not found'}, 404
        return {
            'total': doc_count,
            'docs': result
        }


def get_estropadak(**kwargs):
    if kwargs.get('year') and kwargs.get('league'):
        return get_estropadak_by_league_year(
            kwargs['league'],
            kwargs['year'],
            kwargs['page'],
            kwargs['count'])
    elif kwargs.get('year') and not kwargs.get('league'):
        return get_estropadak_by_year(kwargs.pop('year'), **kwargs)
    elif kwargs.get('league') and not kwargs.get('year'):
        return get_estropadak_by_league_year(
            kwargs['league'],
            None,
            kwargs['page'],
            kwargs['count'])
    else:
        return get_estropadak_by_league_year(None, None)



def insert_estropada_into_db(estropada: Estropada):
    if estropada.liga == 'EUSKOTREN':
        estropada.liga = estropada.liga.lower()
    with get_db_connection() as database:
        res = database.post_document(config["DBNAME"], estropada.dump_dict())
        new_estropada_result = res.get_result()
        res = database.get_document(config["DBNAME"], new_estropada_result["id"])
        new_estropada = res.get_result()
        sailkapenak = [Sailkapena(**sailkapena) for sailkapena in new_estropada['sailkapena']]
        new_estropada['sailkapena'] = sailkapenak
        return Estropada(**new_estropada)


def update_estropada_into_db(estropada_id: str, estropada: Estropada):
    with get_db_connection() as database:
        res = database.get_document(config['DBNAME'], estropada_id)
        doc = res.get_result()
        doc['izena'] = estropada.izena
        doc['data'] = estropada.data.isoformat()
        doc['liga'] = estropada.liga
        if doc['liga'] == 'EUSKOTREN':
            estropada['liga'] = estropada.liga.lower()
        doc['lekua'] = estropada.lekua
        doc['sailkapena'] = estropada.sailkapena
        doc['type'] = estropada.type
        if hasattr(estropada, 'bi_jardunaldiko_bandera'):
            doc['bi_jardunaldiko_bandera'] = estropada.bi_jardunaldiko_bandera
        if hasattr(estropada, 'related_estropada'):
            doc['related_estropada'] = estropada.related_estropada
        if hasattr(estropada, 'jardunaldia'):
            doc['jardunaldia'] = estropada.jardunaldia
        if hasattr(estropada, 'kategoriak'):
            doc['kategoriak'] = estropada.kategoriak
        if hasattr(estropada, 'urla'):
            doc['urla'] = estropada.urla
        database.put_document(config["DBNAME"], estropada_id, doc)


def delete_estropada_from_db(estropada_id):
    with get_db_connection() as database:
        res = database.get_document(config["DBNAME"], estropada_id)
        document = res.get_result()
        if document:
            database.delete_document(config["DBNAME"], estropada_id, rev=document["_rev"])
