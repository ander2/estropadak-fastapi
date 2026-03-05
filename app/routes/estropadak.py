import logging

from app.config import PAGE_SIZE, JWT_SECRET_KEY
from fastapi import APIRouter, HTTPException, Security, status
from fastapi_jwt import JwtAuthorizationCredentials, JwtAccessBearer

from ..dao import estropadak
from ..logic.estropadak import EstropadakLogic
from ..models.estropadak import Estropada, EstropadakList, EstropadaTypeEnum
from app.config import DEFAULT_LOGGER

logger = logging.getLogger(DEFAULT_LOGGER)

access_security = JwtAccessBearer(secret_key=JWT_SECRET_KEY, auto_error=True)

router = APIRouter(
    prefix="/estropadak",
    tags=["estropadak"],
    responses={404: {"description": "Not found"}},
)


@router.get("", response_model=EstropadakList, response_model_by_alias=False)
async def get_estropadak(year: int | None = None,
                         league: EstropadaTypeEnum | None = None,
                         page: int = 0, count: int | None = PAGE_SIZE) -> EstropadakList:
    kwargs = {}
    if year:
        kwargs['year'] = year
    if league:
        kwargs["league"] = league.value
    if count:
        kwargs["count"] = count
    if page is not None:
        kwargs["page"] = page
    try:
        estropadak_ = estropadak.get_estropadak(**kwargs)
        return estropadak_
    except Exception as e:
        msg = "Error listing estropadak: %s"
        logger.exception(msg, e, exc_info=True)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("", status_code=status.HTTP_201_CREATED, response_model_by_alias=False)
async def post_estropada(
    estropada: Estropada,
    credentials: JwtAuthorizationCredentials = Security(access_security),
) -> Estropada:
    data = estropada
    try:
        estropada_ = EstropadakLogic.create_estropada(data)
        if estropada_:
            logger.info(estropada_)
            return estropada_
        else:
            raise HTTPException(status.HTTP_406_NOT_ACCEPTABLE)
    except Exception as e:
        logging.error("Error while creating an estropada", exc_info=1)
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))


@router.get("/{doc_id}", response_model_by_alias=False)
async def get_estropada(doc_id: str) -> Estropada:
    estropada = EstropadakLogic.get_estropada(doc_id)
    if not estropada:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    logger.info(estropada)
    return estropada


@router.put("/{doc_id}")
async def put_estropada(
    doc_id: str,
    estropada: Estropada,
    credentials: JwtAuthorizationCredentials = Security(access_security),
) -> dict:
    try:
        EstropadakLogic.update_estropada(doc_id, estropada)
        return {}
    except Exception as e:
        logging.error("Error while updating estropada %s", doc_id, exc_info=1)
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_estropada(
    doc_id: str,
    credentials: JwtAuthorizationCredentials = Security(access_security),
) -> None:
    try:
        EstropadakLogic.delete_estropada(doc_id)
    except Exception:
        logging.error("Error while deleting estropada %s", doc_id, exc_info=1)
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
