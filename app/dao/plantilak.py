import logging

from .db_connection import get_db_connection
from app.common.errors import NotFoundError
from app.config import config


def get_plantila(team, league, year):
    with get_db_connection() as database:
        try:
            id = f'team_{league}_{year}_{team.capitalize()}'
            res = database.get_document(config["DBNAME"], id)
            taldea = res.get_result()
            res_talde_izenak = database.get_document(config["DBNAME"], 'talde_izenak')
            talde_izenak = res_talde_izenak.get_result()
            talde_izenak = {k.lower(): v for k, v in talde_izenak.items()}
            _rowers = []
            for i, rower in enumerate(taldea['rowers']):
                historial = []
                for h in rower['historial']:
                    t = list(h.items())
                    try:
                        normalized_name = talde_izenak[t[0][1].lower()]
                    except KeyError:
                        normalized_name = t[0][1]
                    historial.append({'name': normalized_name, 'year': t[0][0]})
                rower['historial'] = historial
                rower['name'] = ' '.join(rower['name'].split(' ')[:-1]).title()
                rower['index'] = i
                _rowers.append(rower)
            taldea['rowers'] = _rowers

        except (TypeError, KeyError):
            logging.info("Not found", exc_info=1)
            raise NotFoundError("Not found")
        return taldea
