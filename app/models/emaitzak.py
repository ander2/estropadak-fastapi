from datetime import datetime
from pydantic import BaseModel, Field
from .estropada_type import EstropadaTypeEnum


class Emaitza(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    rev: str | None = Field(default=None, alias="_rev")
    denbora: str = ''
    estropada_data: datetime
    estropada_id: str
    estropada_izena: str
    kalea: int
    kategoria: str = ''
    liga: EstropadaTypeEnum
    posizioa: int = 0
    puntuazioa: int = 0
    talde_izen_normalizatua: str
    talde_izena: str
    tanda_postua: int
    tanda: int
    ziabogak: list[str] = []


class EmbedEmaitza(BaseModel):
    denbora: str = ''
    kalea: int
    posizioa: int = 0
    puntuazioa: int = 0
    talde_izena: str
    tanda_postua: int
    tanda: int
    ziabogak: list[str] = []


class EmaitzakList(BaseModel):
    total: int = 0
    docs: list[Emaitza] = []

class EmaitzaBateratua(BaseModel):
    talde_izena: str
    lehen_jardunaldiko_denbora: str
    bigarren_jardunaldiko_denbora: str
    denbora_batura: str
    posizioa: int = 0