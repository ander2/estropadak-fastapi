from enum import StrEnum

from pydantic import BaseModel
from datetime import datetime


class EstropadaTypeEnum(StrEnum):
    ACT = 'ACT'
    ARC1 = 'ARC1'
    ARC2 = 'ARC2'
    ETE = 'ETE'
    EUSKOTREN = 'EUSKOTREN'
    euskotren = 'euskotren'
    KONTXA = 'KONTXA'
    GBL = 'GBL'
    BBL = 'BBL'
    BTL = 'BTL'
    GTL = 'GTL'
    TXAPELKETAK = 'TXAPELKETAK'


class Estropada(BaseModel):
    id: str | None = None
    izena: str
    data: datetime
    lekua: str = None
    liga: EstropadaTypeEnum
    sailkapena: list = []
    bi_jardunaldiko_bandera: bool = False
    jardunaldia: int = 1
    bi_eguneko_sailkapena: list = []
    related_estropada: str | None = None
    urla: str | None = None
    puntuagarria: bool =True
    kategoriak: list = []
    oharrak: str | None = None


class EstropadakList(BaseModel):
    total: int = 0
    docs: list[Estropada] = []
