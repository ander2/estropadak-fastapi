import asyncio
from fastapi import APIRouter, HTTPException, status

from app.models.estropada_type import EstropadaTypeEnum, LigaWithStaff
from app.dao import taldeak
from app.dao import plantilak

MIN_YEAR = 2003
router = APIRouter(
    prefix="/taldeak",
    tags=["taldeak"],
    responses={404: {"description": "Not found"}},
)


@router.get('')
async def get_taldeak(league: EstropadaTypeEnum, year: int | None = None, category: str | None = None):
    teams = []
    categorised_leagues = (EstropadaTypeEnum.GBL, EstropadaTypeEnum.GTL, EstropadaTypeEnum.BBL, EstropadaTypeEnum.BTL)
    if league.upper() not in categorised_leagues:
        category = None
    teams = await asyncio.to_thread(taldeak.get_taldeak, league, year, category)
    return teams


@router.get('/{team_id}')
async def get_taldea(team_id: str, year: int, league: LigaWithStaff):
    try:
        team = await asyncio.to_thread(plantilak.get_plantila, team_id, league, year)
    except Exception:
        msg = f"Team {team_id} on {league=} and {year=} not found"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
    return team
