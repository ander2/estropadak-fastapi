import logging
import http.client

from typing import Any
from app.config import config, PAGE_SIZE, JWT_SECRET_KEY
from fastapi import APIRouter, HTTPException, Security, Response, status
from fastapi_jwt import JwtAuthorizationCredentials, JwtAccessBearer

from ..dao.estropadak import EstropadakDAO
from ..logic.estropadak import EstropadakLogic
from ..models.estropadak import Estropada, EstropadakList, EstropadaTypeEnum

access_security = JwtAccessBearer(secret_key=JWT_SECRET_KEY, auto_error=True)

router = APIRouter(
    prefix="/estropadak",
    tags=["estropadak"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=EstropadakList)
async def get_estropadak(year: int | None = None, league: EstropadaTypeEnum | None = None, page: int = 0, count: int | None = PAGE_SIZE) -> Any:
    kwargs = {}
    if year:
        kwargs['year'] = year
    if league:
        kwargs["league"] = league.value
    if count:
        kwargs["count"] = count
    if page is not None:
        kwargs["page"] = page
    estropadak = EstropadakDAO.get_estropadak(**kwargs)
    return estropadak


@router.post("/", response_model=Estropada, status_code=status.HTTP_201_CREATED)
async def post_estropada(
    estropada: Estropada,
    credentials: JwtAuthorizationCredentials = Security(access_security),
) -> Estropada:
    data = estropada
    try:
        estropada_ = EstropadakLogic.create_estropada(data)
        if estropada_:
            return estropada_  # .dump_dict()
        else:
            raise HTTPException(status.HTTP_406_NOT_ACCEPTABLE)
    except Exception as e:
        logging.error("Error while creating an estropada", exc_info=1)
        return str(e), 400


@router.get("/{doc_id}", response_model=Estropada)
async def get_estropada(doc_id: str) -> Any:
    estropada = EstropadakDAO.get_estropada_by_id(doc_id)
    if not estropada:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return estropada


@router.put("/{doc_id}")
async def put_estropada(
    doc_id: str,
    estropada: Estropada,
    credentials: JwtAuthorizationCredentials = Security(access_security),
) -> dict:
    data = estropada
    try:
        EstropadakLogic.update_estropada(doc_id, data)
        return {}
    except Exception as e:
        logging.error("Error while updating an estropada", exc_info=1)
        return str(e), 400


@router.delete("/{doc_id}")
async def delete_estropada(
    doc_id: str,
    credentials: JwtAuthorizationCredentials = Security(access_security),
) -> dict:
    try:
        EstropadakLogic.delete_estropada(doc_id)
        return {}
    except Exception as e:
        logging.error("Error while deleting an estropada", exc_info=1)
        return str(e), 400
