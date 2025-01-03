import json
import logging

from .models.estropadak import Estropada
from .models.sailkapenak import Sailkapena
from .db_connection import get_db_connection
from app.config import PAGE_SIZE
from typing import Dict, List

logger = logging.getLogger('estropadak')
logger.setLevel(logging.DEBUG)


class EstropadakDAO:
    @staticmethod
    def get_estropada_by_id(id):
        with get_db_connection() as database:
            try:
                estropada = database[id]
                estropada['data'] = estropada['data'].replace(' ', 'T')
                if estropada['liga'] == 'euskotren':
                    estropada['liga'] = estropada['liga'].upper()
            except TypeError:
                logging.error("Not found", exc_info=1)
                estropada = None
            except KeyError:
                logging.error("Not found", exc_info=1)
                estropada = None
            return estropada

    @staticmethod
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
                res = database.get_view_result("estropadak", "all",
                                               startkey=start,
                                               endkey=end,
                                               raw_result=True,
                                               reduce=True)
                rows = res.get('rows', [{'value': 0}])
                if len(rows) > 0:
                    doc_count = rows[0]['value']
                else:
                    doc_count = 0
                    result = []
                if doc_count > 0:
                    estropadak = database.get_view_result("estropadak",
                                                          "all",
                                                          raw_result=True,
                                                          startkey=start,
                                                          endkey=end,
                                                          include_docs=True,
                                                          reduce=False,
                                                          skip=count * page,
                                                          limit=count)
                    result = []
                    for row in estropadak['rows']:
                        estropada = row['doc']
                        estropada['id'] = row['doc']['_id']
                        estropada['data'] = estropada['data'].replace(' ', 'T')
                        if estropada['liga'] == 'euskotren':
                            estropada['liga'] = estropada['liga'].upper()
                        result.append(estropada)

                print(f"Doc count {len(result)}")
                return {
                    'total': doc_count,
                    'docs': result
                }
            except KeyError:
                return {'error': 'Estropadak not found'}, 404

    @staticmethod
    def get_estropadak_by_year(year, page=0, count=20):
        start = [year]
        end = [year + 1]
        result = []
        with get_db_connection() as database:
            try:

                _count = database.get_view_result(
                    "estropadak",
                    "by_year",
                    raw_result=True,
                    startkey=start,
                    endkey=end,
                    reduce=True)
                logging.info(f"Total:{_count}")
                rows = _count.get('rows', [{'value': 0}])
                if len(rows) > 0:
                    doc_count = rows[0]['value']
                else:
                    doc_count = 0
                    result = []
                if doc_count > 0:
                    estropadak = database.get_view_result(
                        "estropadak",
                        "by_year",
                        raw_result=True,
                        startkey=start,
                        endkey=end,
                        include_docs=True,
                        reduce=False,
                        skip=count*page,
                        limit=count)
                    for row in estropadak['rows']:
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

    @staticmethod
    def get_estropadak(**kwargs):
        if kwargs.get('year') and kwargs.get('league'):
            return EstropadakDAO.get_estropadak_by_league_year(
                kwargs['league'],
                kwargs['year'],
                kwargs['page'],
                kwargs['count'])
        elif kwargs.get('year') and not kwargs.get('league'):
            return EstropadakDAO.get_estropadak_by_year(kwargs.pop('year'), **kwargs)
        elif kwargs.get('league') and not kwargs.get('year'):
            return EstropadakDAO.get_estropadak_by_league_year(
                kwargs['league'],
                None,
                kwargs['page'],
                kwargs['count'])
        else:
            return EstropadakDAO.get_estropadak_by_league_year(None, None)


    @staticmethod
    def insert_estropada_into_db(estropada: Estropada):
        if estropada.liga == 'EUSKOTREN':
            estropada.liga = estropada.liga.lower()
        with get_db_connection() as database:
            document = database.create_document(estropada.dump_dict())
            new_estropada = json.loads(document.json())
            sailkapenak = [Sailkapena(**sailkapena) for sailkapena in new_estropada['sailkapena']]
            new_estropada['sailkapena'] = sailkapenak
            return Estropada(**new_estropada)

    @staticmethod
    def update_estropada_into_db(estropada_id: str, estropada: Estropada):
        with get_db_connection() as database:
            doc = database[estropada_id]
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
            doc.save()

    @staticmethod
    def delete_estropada_from_db(estropada_id):
        with get_db_connection() as database:
            doc = database[estropada_id]
            if doc.exists():
                doc.fetch()
                doc.delete()
