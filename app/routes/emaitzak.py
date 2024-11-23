import logging
import http.client
import json

from json.decoder import JSONDecodeError
from typing import Any
from config import config, PAGE_SIZE, JWT_SECRET_KEY
from fastapi import APIRouter, HTTPException, Security, Response, status
from fastapi_jwt import JwtAuthorizationCredentials, JwtAccessBearer

from ..dao.emaitzak import EmaitzakDAO
from ..logic.estropadak import EstropadakLogic
from ..models.estropadak import Estropada, EstropadakList, EstropadaTypeEnum 

access_security = JwtAccessBearer(secret_key=JWT_SECRET_KEY, auto_error=True)

router = APIRouter(
    prefix="/emaitzak",
    tags=["emaitzak"],
    responses={404: {"description": "Not found"}},
)


# @api.expect(emaitzak_parser, validate=True)
# @api.marshal_with(emaitzak_list_model)
@router.get("/")
def get_emaitzak(criteria: str = '', page: int = 1, count: int = PAGE_SIZE):
    try:
        criteria = json.loads(criteria)
    except JSONDecodeError:
        return {"message": "Bad criteria, please check the query"}, 400
    try:
        docs, total = EmaitzakDAO.get_emaitzak(criteria, page, count)
        return {"docs": docs, "total": total}
    except Exception:
        logging.info("Error", exc_info=1)
        return {'error': 'Estropadak not found'}, 404

#     @jwt_required()
#     @api.expect(emaitza_model, validate=True)
#     def post(self):
#         emaitza = api.payload
#         doc_created = EmaitzakDAO.insert_emaitza_into_db(emaitza)
#         if doc_created:
#             return {}, 201  # , "Estropada created"
#         else:
#             return {}, 400  # , "Cannot create estropada"


# @api.route('/<string:emaitza_id>', strict_slashes=False)
# class Emaitza(Resource):

@router.get("/{emaitza_id}")
def get_emaitza(emaitza_id: str) -> Any:

    emaitza = EmaitzakDAO.get_emaitza_by_id(emaitza_id)
    if emaitza:
        return emaitza
    else:
        return {}, 404

#     @jwt_required()
#     @api.expect(emaitza_model, validate=True)
#     def put(self, emaitza_id):

#         data = api.payload

#         emaitza = EmaitzakLogic.update_emaitza(emaitza_id, data)

#         if emaitza:
#             return emaitza
#         else:
#             return {}, 404

#     @jwt_required()
#     def delete(self, emaitza_id):

#         emaitza = EmaitzakDAO.delete_emaitza_from_db(emaitza_id)

#         if emaitza:
#             return {}, 200
#         else:
#             return {"msg": "Cannot delete document"}, 401