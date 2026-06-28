import textdistance
import logging

from ibm_cloud_sdk_core import ApiException

from app.config import config, DEFAULT_LOGGER
from .db_connection import get_db_connection

logger = logging.getLogger(DEFAULT_LOGGER)


def get_taldeak(league: str, year: str | None = None, category: str | None = None) -> list[dict]:
    league = league.upper()

    taldeak = []
    with get_db_connection() as database:
        try:
            res = database.get_document(config["DBNAME"], 'talde_izenak2')
            all_teams = res.get_result()
            if year is not None:
                key = f'rank_{league}_{year}'
                if category:
                    key = f'rank_{league}_{year}_{category.lower()}'
                res = database.get_document(config["DBNAME"], key)
                resume= res.get_result()
                for taldea in resume['stats'].keys():
                    try:
                        short = all_teams[taldea.title()].get('acronym')
                    except KeyError:
                        s = 0
                        for k in all_teams.keys():
                            simmilarity = textdistance.hamming.similarity(k, taldea.capitalize())
                            if simmilarity > s:
                                s = simmilarity
                                team = k
                        short = all_teams[team].get('acronym') + taldea[-2]
                    taldeak.append({
                        "name": taldea,
                        "alt_names": all_teams.get(taldea, {}).get('alt_names', [taldea]),
                        "short": short
                    })
            else:
                league = league.lower()
                res = database.get_document(config["DBNAME"], f'taldeak_{league}')
                resume =  res.get_result()
                for taldea in resume['taldeak']:
                    taldeak.append({
                        "name": taldea,
                        "alt_names": all_teams[taldea].get('alt_names'),
                        "short": all_teams[taldea].get('acronym')
                    })
        except ApiException as e:
            logger.error(f"Taldeak document for league {league}, year {year} and category {category} not found: {e}")
        return taldeak


def get_talde_izena(taldea: str) -> str:
    talde_izena = ''
    talde_izenak = {}
    with get_db_connection() as database:
        res = database.get_document(config["DBNAME"], 'talde_izenak2')
        talde_izenak2 = res.get_result()
        for k, v in talde_izenak2.items():
            if k.startswith('_'):
                continue
            for alt_name in v['alt_names']:
                talde_izenak[alt_name.lower()] = k

        talde_izena = talde_izenak.get(taldea.lower())
        if not talde_izena:
            s = 0
            for k in talde_izenak.keys():
                simmilarity = textdistance.hamming.similarity(k, taldea.lower())
                if simmilarity > s:
                    s = simmilarity
                    talde_izena = k
    return talde_izena
