import logging

from app.dao import estatistikak, estropadak
from app.common.utils import get_team_color


def get_culumative_stats(league, year, team, category):
    result = []
    if year is None:
        sailkapenak = estatistikak.get_sailkapenak_by_league(league)
        for sailkapena in sailkapenak:
            urtea = int(sailkapena['_id'][-4:])
            try:
                year_values = {
                    "key": team
                }
                values = [{
                    "label": urtea,
                    "x": i,
                    "value": val}
                    for i, val in enumerate(sailkapena['stats'][team]['cumulative'])]
                year_values["values"] = values
                result.append(year_values)
            except KeyError:
                pass
    else:
        sailkapena = estatistikak.get_sailkapena_by_league_year(league, year, category)
        estropadak_ = estropadak.get_estropadak_by_league_year(league, year)
        estropadak_ = [
            estropada for estropada in estropadak_['docs']
            if not estropada['izena'].startswith('Play')
            and estropada.get('puntuagarria', True)
        ]
        for taldea, stats in sailkapena['stats'].items():
            team_values = {
                "key": taldea,
                "color": get_team_color(taldea),
            }
            values = [{"label": val[1]['izena'],
                        "x": i,
                        "value": val[0]}
                        for i, val in enumerate(zip(stats['cumulative'], estropadak_))]
            team_values["values"] = values
            result.append(team_values)
        try:
            result = sorted(result, key=lambda x: x['values'][-1]['value'])
        except IndexError:
            pass
        return {
            'total': len(result),
            'docs': result
        }

def get_points_per_race(league: str, year: int, category: str):
    result = []
    sailkapena = estatistikak.get_sailkapena_by_league_year(league, year, category)
    estropadak = estropadak.get_estropadak_by_league_year(
        league,
        year)
    estropadak = [estropada for estropada in estropadak['docs'] if not estropada['izena'].startswith('Play')]
    if sailkapena:
        points_max = len(sailkapena['stats'])
        for taldea, stats in sailkapena['stats'].items():
            team_values = {
                "key": taldea,
                "color": get_team_color(taldea),
            }
            if not category:
                points = [stats['cumulative'][0]]
                index = 0
                for point in stats['cumulative'][1:]:
                    points.append(point-stats['cumulative'][index])
                    index += 1
                values = [{
                    "label": val[1]['izena'],
                    "x": i,
                    "value": val[0]}
                    for i, val in enumerate(zip(points, estropadak))]
            else:
                points_max = stats['points'] + stats.get('discard', 0)
                points = []
                cumulative = [0] + stats['cumulative']
                for i, point in enumerate(cumulative):
                    try:
                        points.append(cumulative[i + 1] - point)
                    except Exception:
                        break
                values = [{
                    "label": val[1]['izena'],
                    "x": i,
                    "value": val[0]} for i, val in enumerate(zip(points, estropadak))
                ]

            team_values["values"] = values
            result.append(team_values)
    return {
        'total': len(result),
        'docs': result
    }


def get_points(league: str, team: str):
    result = []
    sailkapenak = estatistikak.get_sailkapenak_by_league(league)
    rank = {
        "key": team,
        "values": [{
            "label": int(sailkapena['_id'][-4:]),
            "x": int(sailkapena['_id'][-4:]),
            "color": get_team_color(team),
            "value": sailkapena['stats'][team]['points']
            } for sailkapena in sailkapenak if team in sailkapena['stats']
        ]
    }
    result.append(rank)
    return {
        'total': len(result),
        'docs': result
    }


def get_rank(league: str, year: int, team: str, category: str):
    result = []
    if team is None:
        sailkapena = estatistikak.get_sailkapena_by_league_year(league, year, category)
        sorted_teams = sorted(
            sailkapena['stats'],
            key=lambda tal: sailkapena['stats'][tal]['position'],
            reverse=False)
        rank = {
            "key": 'Taldea',
            "values": [{
                "label": taldea,
                "color": get_team_color(taldea),
                "value": sailkapena['stats'][taldea]['points']
                } for taldea in sorted_teams
            ]
        }
        result.append(rank)
    else:
        sailkapenak = estatistikak.get_sailkapenak_by_league(league)
        rank = {
            "key": team,
            "values": [{
                "label": int(sailkapena['_id'][-4:]),
                "color": get_team_color(team),
                "value": sailkapena['stats'][team]['position']
                } for sailkapena in sailkapenak if team in sailkapena['stats']
            ]
        }
        result.append(rank)
    return {
        'total': len(result),
        'docs': result
    }


def get_ages(league: str, year: int, team: str):
    result = []
    logging.info(f'Got team {league} {year} {team}')
    if team is None:
        sailkapena = estatistikak.get_sailkapena_by_league_year(league, year, None)
        if not sailkapena or not sailkapena.get('stats', []):
            return result
        logging.info('Got sailkapena')
        min_ages = {
            "key": 'Min',
            "values": [{
                "label": taldea,
                "value": val['age']['min_age']
                } for taldea, val in sailkapena['stats'].items()
            ]
        }
        med_ages = {
            "key": 'Media',
            "values": [{
                "label": taldea,
                "value": val['age']['avg_age']
                } for taldea, val in sailkapena['stats'].items()
            ]
        }
        max_ages = {
            "key": 'Max',
            "values": [{
                "label": taldea,
                "value": val['age']['max_age']
                } for taldea, val in sailkapena['stats'].items()
            ]
        }
        result.append(min_ages)
        result.append(med_ages)
        result.append(max_ages)
    else:
        sailkapenak = estatistikak.get_sailkapenak_by_league(league)
        min_ages = {
            "key": 'Min',
            "values": [{
                "label": int(sailkapena['_id'][-4:]),
                "value": sailkapena['stats'][team]['age']['min_age']
            } for sailkapena in sailkapenak if team in sailkapena['stats']
                        and 'age' in sailkapena['stats'][team]]
        }
        med_ages = {
            "key": 'Media',
            "values": [{
                "label": int(sailkapena['_id'][-4:]),
                "value": sailkapena['stats'][team]['age']['avg_age']
            } for sailkapena in sailkapenak if team in sailkapena['stats']
                        and 'age' in sailkapena['stats'][team]]
        }
        max_ages = {
            "key": 'Max',
            "values": [{
                "label": int(sailkapena['_id'][-4:]),
                "value": sailkapena['stats'][team]['age']['max_age']
            } for sailkapena in sailkapenak if team in sailkapena['stats']
                        and 'age' in sailkapena['stats'][team]]
        }
        result.append(min_ages)
        result.append(med_ages)
        result.append(max_ages)

    return {
        'total': len(result),
        'docs': result
    }


def get_incorporations(league: str, year: int, team: str):
    result = []
    if team is None:
        sailkapena = estatistikak.get_sailkapena_by_league_year(league, year, None)
        altak = {
            "key": 'Altak',
            "values": [{
                "label": taldea,
                "value": val['rowers']['altak']
                } for taldea, val in sailkapena['stats'].items() if 'rowers' in sailkapena['stats'][taldea]
            ]
        }
        bajak = {
            "key": 'Bajak',
            "values": [{
                "label": taldea,
                "value": val['rowers']['bajak']
                } for taldea, val in sailkapena['stats'].items() if 'rowers' in sailkapena['stats'][taldea]
            ]
        }
        result.append(altak)
        result.append(bajak)
    else:
        sailkapenak = estatistikak.get_sailkapenak_by_league(league)
        altak = {
            "key": 'Altak',
            "values": [{
                "label":
                int(sailkapena['_id'][-4:]),
                "value":
                sailkapena['stats'][team]['rowers']['altak']
            } for sailkapena in sailkapenak if team in sailkapena['stats']
                        and 'rowers' in sailkapena['stats'][team]]
        }
        bajak = {
            "key": 'Bajak',
            "values": [{
                "label": int(sailkapena['_id'][-4:]),
                "value": sailkapena['stats'][team]['rowers']['bajak']
            } for sailkapena in sailkapenak if team in sailkapena['stats']
                        and 'rowers' in sailkapena['stats'][team]]
        }
        result.append(altak)
        result.append(bajak)
    return {
        'total': len(result),
        'docs': result
    }