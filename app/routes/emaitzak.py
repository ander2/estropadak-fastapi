import logging
import json

from json.decoder import JSONDecodeError
from typing import Any
from app.config import PAGE_SIZE, JWT_SECRET_KEY
from fastapi import APIRouter, HTTPException, Security, status
from fastapi_jwt import JwtAuthorizationCredentials, JwtAccessBearer

from ..dao.emaitzak import EmaitzakDAO
from ..logic.emaitzak import EmaitzakLogic
from ..models.emaitzak import Emaitza

access_security = JwtAccessBearer(secret_key=JWT_SECRET_KEY, auto_error=True)

router = APIRouter(
    prefix="/emaitzak",
    tags=["emaitzak"],
    responses={404: {"description": "Not found"}},
)

@router.get("")
def get_emaitzak(criteria: str = '', page: int = 0, count: int = PAGE_SIZE):
    try:
        criteria = json.loads(criteria)
    except JSONDecodeError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Bad criteria, please check the query")
    try:
        docs, total = EmaitzakDAO.get_emaitzak(criteria, page, count)
        return {"docs": docs, "total": total}
    except Exception:
        logging.info("Error", exc_info=1)
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Estropadak not found")

@router.post("", status_code=201)
def post_emaitza(
    emaitza: Emaitza,
    credentials: JwtAuthorizationCredentials = Security(access_security),
):
    doc_created = EmaitzakLogic.create_emaitza(emaitza.model_dump())
    if doc_created:
        return {}, 201
    else:
        return {}, 400

@router.put("/{emaitza_id}")
def put_emaitza(
    emaitza_id: str,
    emaitza: Emaitza,
    credentials: JwtAuthorizationCredentials = Security(access_security),
):
    doc_updated = EmaitzakLogic.update_emaitza(emaitza_id, emaitza.model_dump())
    if doc_updated:
        return {}, 200
    else:
        return {}, 400

@router.get("/{emaitza_id}")
def get_emaitza(emaitza_id: str) -> Any:

    emaitza = EmaitzakDAO.get_emaitza_by_id(emaitza_id)
    if emaitza:
        return emaitza
    else:
        return {}, 404

@router.delete("/{emaitza_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(emaitza_id: str):
    emaitza = EmaitzakDAO.delete_emaitza_from_db(emaitza_id)
    if not emaitza:
        return {"msg": "Cannot delete document"}, 401
