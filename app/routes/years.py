import logging

from fastapi import APIRouter, HTTPException, Security, Response, status, Query
from fastapi_jwt import JwtAuthorizationCredentials, JwtAccessBearer

from app.config import config, PAGE_SIZE, JWT_SECRET_KEY
from app.models.estropadak import EstropadaTypeEnum
from app.models.years import Year, YearPutModel
from app.dao.years import YearsDAO
from app.config import LEAGUES

access_security = JwtAccessBearer(secret_key=JWT_SECRET_KEY, auto_error=True)
logger = logging.getLogger('estropadak')
MIN_YEAR = 2003
router = APIRouter(
    prefix="/years",
    tags=["years"],
    responses={404: {"description": "Not found"}},
)


@router.get('/')
def get_all_years(historial: bool = False, year: int = 2010) -> list[Year]:
    all_years = YearsDAO.get_years_from_db()
    result = []
    for k, v in all_years.items():
        if k.upper() in LEAGUES or k == 'euskotren':
            if historial:
                if year > 2009:
                    result.append({
                        'name': k,
                        'years': v
                    })
            else:
                result.append({
                    'name': k,
                    'years': v
                })
    return result

@router.get('/{league}')
def get_years(league: EstropadaTypeEnum):
    all_years = YearsDAO.get_years_from_db()
    years = all_years.get(league.lower(), [])
    return {
        'name': league,
        'years': years
    }

# @jwt_required()
# @api.expect(urteak_put_model, validate=True)
@router.put('/{league}')
def put_years(league: EstropadaTypeEnum,
              data: YearPutModel,
              credentials: JwtAuthorizationCredentials = Security(access_security),
              ):
    YearsDAO.update_years_into_db(data.urteak, league.lower())