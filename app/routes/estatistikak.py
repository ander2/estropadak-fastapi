import logging

from fastapi import APIRouter
from app.models.estropadak import EstropadaTypeEnum
from app.models.estatistikak import EstatistikaTypeEnum
from app.logic.estatistikak import (
    get_culumative_stats,
    get_points,
    get_points_per_race,
    get_rank,
    get_ages,
    get_incorporations,
)

router = APIRouter(
    prefix='/estatistikak',
    tags=["estatistikak"],
    responses={404: {"description": "Not found"}}
)

@router.get('')
def get_estatistikak(stat: EstatistikaTypeEnum,
                     league: EstropadaTypeEnum | None = None,
                     year: int | None = None,
                     team: str | None = None,
                     category: str | None = None):
    result = []
    stat_type = stat
    logging.info(f'Stat {stat_type}*{team}*')
    if stat_type == 'cumulative':
        result = get_culumative_stats(league, year, team, category)
    elif stat_type == 'points':
        if team:
            result = get_points(league, team)
        else:
            if not league or not year:
                return {"message": "You need to specify year and league"}, 400
            result = get_points_per_race(league, year, category)
    elif stat_type == 'rank':
        if team and not league:
            return {"message": "You need to specify a league"}, 400
        if not team and (not league or not year):
            return {"message": "You need to specify year and league"}, 400
        result = get_rank(league, year, team, category)
    elif stat_type == 'ages':
        if team and not league:
            return {"message": "You need to specify a league"}, 400
        if not team and (not league or not year):
            return {"message": "You need to specify year and league"}, 400
        result = get_ages(league, year, team)
    elif stat_type == 'incorporations':
        result = get_incorporations(league, year, team)
    return result
