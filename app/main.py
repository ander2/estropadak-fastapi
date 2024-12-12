import http.client
import json
import urllib

from fastapi import FastAPI, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi_jwt import JwtAccessBearer
from app.config import config, JWT_SECRET_KEY
from .models.login import Login
from .routes.estatistikak import router as estatistikak_router
from .routes.estropadak import router as estropadak_router
from .routes.emaitzak import router as emaitzak_router
from .routes.sailkapenak import router as sailkapenak_router
from .routes.taldeak import router as taldeak_router
from .routes.years import router as year_router


api = FastAPI()
access_security = JwtAccessBearer(secret_key=JWT_SECRET_KEY, auto_error=True)

api.include_router(estatistikak_router)
api.include_router(estropadak_router)
api.include_router(emaitzak_router)
api.include_router(sailkapenak_router)
api.include_router(taldeak_router)
api.include_router(year_router)


@api.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Overrides FastAPI default status code for validation errors from 422 to 400."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


@api.get("/")
async def root():
    return {"message": "estropadak API"}


@api.post("/auth")
async def auth(login: Login):
    params = urllib.parse.urlencode({
        "username": login.username,
        "password": login.password
    })
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        "Accept": "text/plain"
    }
    host = config['COUCHDB_HOST']
    port = int(config['COUCHDB_PORT'])
    conn = http.client.HTTPConnection(host, port)
    conn.request("POST", "/_session", params, headers)
    response = conn.getresponse()
    if response.status == 200:
        res = json.loads(response.read())
        if 'error' in res:
            return {}
        else:
            subject = {"username": login.username, "role": "user"}
            access_token = access_security.create_access_token(subject=subject)
            return {"access_token": access_token}
    else:
        return {}

