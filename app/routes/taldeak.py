import logging

from fastapi import APIRouter, HTTPException, Security, Response, status, Query

from app.models.estropadak import EstropadaTypeEnum
from app.dao.taldeak import TaldeakDAO
from app.dao.plantilak import PlantilakDAO

logger = logging.getLogger('estropadak')
MIN_YEAR = 2003
router = APIRouter(
    prefix="/taldeak",
    tags=["taldeak"],
    responses={404: {"description": "Not found"}},
)


@router.get('')
def get_taldeak(year: int, league: EstropadaTypeEnum, category: str | None = None):
    teams = []
    # if league.upper() not in ('GBL', 'GTL', 'BBL', 'BTL'):
    #     category = None
    teams = TaldeakDAO.get_taldeak(league, year, category)
    return teams


@router.get('/{team_id}')
def get_taldea(self, team_id: str, year: int, league: EstropadaTypeEnum):
    leagues = ['ACT', 'ARC1', 'ARC2', 'ETE', 'EUSKOTREN']
    league = league.upper()
    if league not in leagues:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Not valid league')
    team = PlantilakDAO.get_plantila(team_id, league, year)
    if team is None:
        return {'message': 'Team not found'}, 404
    return team
