import logging
from typing import Any, Annotated

from app.config import config, PAGE_SIZE, JWT_SECRET_KEY
from fastapi import APIRouter, HTTPException, Security, Response, status, Query
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

logger = logging.getLogger('estropadak')
MIN_YEAR = 2003
router = APIRouter(
    prefix="/sailkapenak",
    tags=["sailkapenak"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=SailkapenakList)
async def get_sailkapenak(
    year: int | None = None,
    league: EstropadaTypeEnum | None = None,
    teams: Annotated[list[str] | None, Query()] = None,
    category=None
) -> Any:
    stats = None
    if year is None:
        stats = get_sailkapena_by_league(league)
    else:
        if year and year < MIN_YEAR:
            return "Year not found", 400
        stats = get_sailkapena_by_league_year(league, year, category)
    if stats is None:
        return {'total': 0, 'docs': []}

    if teams:
        team_stats = get_sailkapenak_by_teams(league, year, teams)
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
    sailkapena = get_sailkapena_logic(sailkapena_id)
    if sailkapena is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return sailkapena


@router.put("/{sailkapena_id}", response_model=Sailkapena)
async def put_sailkapena(sailkapena_id: str,
                         sailkapena: Sailkapena,
                         credentials: JwtAuthorizationCredentials = Security(access_security),
                         ) -> Sailkapena:
    return update_sailkapena_logic(sailkapena_id, sailkapena)


@router.delete("/{sailkapena_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sailkapena(
    sailkapena_id: str,
    credentials: JwtAuthorizationCredentials = Security(access_security),
) -> None:
    delete_sailkapena_from_db(sailkapena_id)


@router.post("/", response_model=Sailkapena, status_code=status.HTTP_201_CREATED)
def post_sailkapenak(
    sailkapena: Sailkapena,
    credentials: JwtAuthorizationCredentials = Security(access_security)
):
    try:
        res = create_sailkapena(sailkapena)
        if res:
            return res
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    except Exception:
        logging.info("Error", exc_info=1)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
