import asyncio
import logging
from datetime import datetime
from typing import Annotated

from app.common.errors import NotFoundError
from app.config import JWT_SECRET_KEY
from fastapi import APIRouter, HTTPException, Security, status, Query
from fastapi_jwt import JwtAuthorizationCredentials, JwtAccessBearer
from app.models.estropadak import EstropadaTypeEnum
from app.models.sailkapenak import Sailkapena, SailkapenakList
from ..logic.sailkapenak import (
    create_sailkapena,
    get_sailkapena as get_sailkapena_logic,
    update_sailkapena as update_sailkapena_logic
)
from ..dao.sailkapenak import (
    delete_sailkapena_from_db,
    get_sailkapena_by_league,
    get_sailkapena_by_league_year,
    get_sailkapenak_by_teams,
)

access_security = JwtAccessBearer(secret_key=JWT_SECRET_KEY, auto_error=True)

MIN_YEAR = 2003
CURRENT_YEAR = datetime.now().year
router = APIRouter(
    prefix="/sailkapenak",
    tags=["sailkapenak"],
    responses={404: {"description": "Not found"}},
)


@router.get("", response_model=SailkapenakList)
async def get_sailkapenak(
    league: EstropadaTypeEnum | None = None,
    year: int | None = Query(None, ge=MIN_YEAR, le=CURRENT_YEAR),
    teams: Annotated[list[str] | None, Query()] = None,
    category=None
) -> SailkapenakList:
    stats = None
    if not year:
        stats = await asyncio.to_thread(get_sailkapena_by_league, league.value)
    elif not league:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You need to provide a league with a year")
    else:
        try:
            stats = await asyncio.to_thread(get_sailkapena_by_league_year, league, year, category)
        except NotFoundError:
            return {'total': 0, 'docs': []}
    if teams:
        try:
            team_stats = await asyncio.to_thread(get_sailkapenak_by_teams, league.name, year, teams)
        except NotFoundError:
            team_stats = {'total': 0, 'docs': []}
        return team_stats
    else:
        res = []
        for stat in stats['docs']:
            res.append({
                "id": stat['_id'],
                "year": int(stat['_id'][-4:]),
                "league": league,
                "stats": [{'name': k, 'value': v} for k, v in stat['stats'].items()]
            })
        result = {
            'total': stats['total'],
            'docs': res
        }
        return result


@router.get("/{sailkapena_id}", response_model=Sailkapena)
async def get_sailkapena(sailkapena_id: str) -> Sailkapena:
    try:
        sailkapena = await get_sailkapena_logic(sailkapena_id)
        return sailkapena
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{sailkapena_id}", response_model=Sailkapena)
async def put_sailkapena(sailkapena_id: str,
                         sailkapena: Sailkapena,
                         credentials: JwtAuthorizationCredentials = Security(access_security),
                         ) -> Sailkapena:
    try:
        _ = await get_sailkapena_logic(sailkapena_id)
        return await update_sailkapena_logic(sailkapena_id, sailkapena)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{sailkapena_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sailkapena(
    sailkapena_id: str,
    credentials: JwtAuthorizationCredentials = Security(access_security),
) -> None:
    await asyncio.to_thread(delete_sailkapena_from_db, sailkapena_id)


@router.post("", response_model=Sailkapena, status_code=status.HTTP_201_CREATED)
async def post_sailkapenak(
    sailkapena: Sailkapena,
    credentials: JwtAuthorizationCredentials = Security(access_security)
):
    try:
        res = await create_sailkapena(sailkapena)
        if res:
            return res
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    except Exception:
        logging.info("Error", exc_info=1)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
