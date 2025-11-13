import json
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from .sailkapenak import Sailkapena, SailkapenBateratua
from typing import TypedDict


class Encoder(json.JSONEncoder):

    def default(self, o):
        return dict(
            izena=o.__izena,
            data=o.__data,
            liga=o.__liga,
            urla=o.__urla,
            lekua=o.__lekua,
            sailkapena=o.__sailkapena)


class EstropadaTypeEnum(str, Enum):
    ACT = 'ACT'
    ARC1 = 'ARC1'
    ARC2 = 'ARC2'
    ETE = 'ETE'
    EUSKOTREN = 'EUSKOTREN'
    KONTXA = 'KONTXA'


@dataclass(kw_only=True)
class Estropada:
    type: str = 'estropada'
    izena: str
    data: datetime
    liga: EstropadaTypeEnum
    _id: str = None
    _rev: str = None
    lekua: str = ''
    sailkapena: list[Sailkapena] = field(default_factory=list)
    bi_jardunaldiko_bandera: bool = False
    jardunaldia: int = 1
    bi_eguneko_sailkapena: list[SailkapenBateratua] = field(default_factory=list)
    related_estropada: str | None = None
    urla: str | None = None
    puntuagarria: bool = True
    kategoriak: list = field(default_factory=list)
    oharrak: str | None = None


class EstropadaListResult(TypedDict):
   total: int
   docs: list[Estropada]