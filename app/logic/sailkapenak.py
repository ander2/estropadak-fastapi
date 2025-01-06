from ..dao.sailkapenak import get_sailkapena_by_id, insert_sailkapena_into_db, update_sailkapena_into_db
from ..models.sailkapenak import Sailkapena


def _encode_sailkapena(sailkapena: Sailkapena) -> dict:
    rank_id = f'rank_{sailkapena.league.upper()}_{sailkapena.year}'
    sailkapena_ = sailkapena.model_dump()
    stats = sailkapena_['stats']
    del sailkapena_['stats']
    sailkapena_['stats'] = {}
    for stat in stats:
        team_name = stat['name']
        sailkapena_['stats'][team_name] = stat['value']
    sailkapena_['_id'] = rank_id
    return sailkapena_


def _decode_sailkapena(sailkapena: dict) -> Sailkapena:
    # rank_id = f'rank_{sailkapena.league}_{sailkapena.year}'
    _, league, year = sailkapena['_id'].split('_')
    result = {
        'id': sailkapena['_id'],
        'league': league.upper(),
        'year': int(year),
        'stats': []
    }
    for k, v in sailkapena['stats'].items():
        result['stats'].append({
            'name': k,
            'value': v
        })
    return Sailkapena(**result)


def create_sailkapena(sailkapena: Sailkapena):
    sailkapena_ = _encode_sailkapena(sailkapena)
    insert_sailkapena_into_db(sailkapena_)
    sailk = get_sailkapena(sailkapena_['_id'])
    return sailk


def get_sailkapena(sailkapena_id: str) -> Sailkapena:
    sailkapena = get_sailkapena_by_id(sailkapena_id)
    sailkapena_ = _decode_sailkapena(sailkapena)
    return sailkapena_


def update_sailkapena(sailkapena_id: str, sailkapena: Sailkapena) -> Sailkapena:
    sailkapena_ = sailkapena.model_dump()
    stats = sailkapena_['stats']
    del sailkapena_['stats']
    sailkapena_['stats'] = {}
    for stat in stats:
        team_name = stat['name']
        sailkapena_['stats'][team_name] = stat['value']
    res = update_sailkapena_into_db(sailkapena_id, sailkapena_)
    _, league, year = sailkapena_id.split('_')
    result = {
        'id': res['_id'],
        'league': league,
        'year': int(year),
        'stats': []
    }

    for k, v in res['stats'].items():
        result['stats'].append({
            'name': k,
            'value': v
        })
    return Sailkapena(**result)
