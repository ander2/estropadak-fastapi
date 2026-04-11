import asyncio
import logging
import json

from json.decoder import JSONDecodeError
from app.common.errors import NotFoundError
from app.config import PAGE_SIZE, JWT_SECRET_KEY
from fastapi import APIRouter, HTTPException, Security, status
from fastapi_jwt import JwtAuthorizationCredentials, JwtAccessBearer

from ..dao import emaitzak
from ..logic.emaitzak import EmaitzakLogic
from ..models.emaitzak import Emaitza, EmaitzakList

access_security = JwtAccessBearer(secret_key=JWT_SECRET_KEY, auto_error=True)

router = APIRouter(
    prefix="/emaitzak",
    tags=["emaitzak"],
    responses={404: {"description": "Not found"}},
)

@router.get("", response_model=EmaitzakList)
async def get_emaitzak(criteria: str = '', page: int = 0, count: int = PAGE_SIZE) -> EmaitzakList:
    try:
        criteria = json.loads(criteria)
    except JSONDecodeError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Bad criteria, please check the query")
    try:
        docs, total = await asyncio.to_thread(emaitzak.get_emaitzak, criteria, page, count)
        return {"docs": docs, "total": total}
    except Exception:
        logging.info("Error", exc_info=1)
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Estropadak not found")

@router.post("", status_code=201)
async def post_emaitza(
    emaitza: Emaitza,
    credentials: JwtAuthorizationCredentials = Security(access_security),
) -> dict:
    doc_created = await EmaitzakLogic.create_emaitza(emaitza.model_dump())
    if doc_created:
        return {}
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

@router.put("/{emaitza_id}")
async def put_emaitza(
    emaitza_id: str,
    emaitza: Emaitza,
    credentials: JwtAuthorizationCredentials = Security(access_security),
)->dict:
    doc_updated = await EmaitzakLogic.update_emaitza(emaitza_id, emaitza)
    if doc_updated:
        return {}
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

@router.get("/{emaitza_id}", response_model=Emaitza)
async def get_emaitza(emaitza_id: str) -> Emaitza:
    try:
        emaitza = await asyncio.to_thread(emaitzak.get_emaitza_by_id, emaitza_id)
        return emaitza
    except NotFoundError as e:
        raise HTTPException(code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/{emaitza_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(emaitza_id: str):
    emaitza = await asyncio.to_thread(emaitzak.delete_emaitza_from_db, emaitza_id)
    if not emaitza:
        raise HTTPException(code=status.HTTP_403_FORBIDDEN, detail="Cannot delete document")
