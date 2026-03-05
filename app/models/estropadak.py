from enum import Enum
from datetime import datetime

from pydantic import BaseModel, Field

from .emaitzak import EmbedEmaitza, EmaitzaBateratua
from .estropada_type import EstropadaTypeEnum

# class EstropadaTypeEnum(str, Enum):
#     ACT = 'ACT'
#     ARC1 = 'ARC1'
#     ARC2 = 'ARC2'
#     ETE = 'ETE'
#     EUSKOTREN = 'EUSKOTREN'
#     KONTXA = 'KONTXA'

class Estropada(BaseModel):
    id: str = Field(default=None, alias="_id")
    rev: str = Field(default=None, alias="_rev")
    izena: str
    data: datetime
    lekua: str = ''
    liga: EstropadaTypeEnum
    sailkapena: list[EmbedEmaitza] = []
    bi_jardunaldiko_bandera: bool = False
    jardunaldia: int = 1
    bi_eguneko_sailkapena: list[EmaitzaBateratua] = []
    related_estropada: str | None = None
    urla: str | None = None
    puntuagarria: bool =True
    kategoriak: list = []
    oharrak: str | None = None


class EstropadakList(BaseModel):
    total: int = 0
    docs: list[Estropada] = []
