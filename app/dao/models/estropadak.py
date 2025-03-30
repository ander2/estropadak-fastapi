import json
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from .sailkapenak import Sailkapena


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
    bi_eguneko_sailkapena: list = field(default_factory=list)
    related_estropada: str | None = None
    urla: str | None = None
    puntuagarria: bool = True
    kategoriak: list = field(default_factory=list)
    oharrak: str | None = None

    def print_json(self):
        print(json.dumps(self, default=self.format_for_json,
                         ensure_ascii=False, indent=4))

    def dump_json(self):
        return json.dumps(self, default=self.format_for_json,
                          ensure_ascii=False, cls=Encoder, indent=4)

    def dump_dict(self):
        return self.format_for_json(self)

    def format_for_json(self, o):
        attrs = ['_id', 'izena', 'data', 'liga',
                 'urla', 'lekua', 'oharrak', 'kategoriak',
                 'puntuagarria', 'type']
        obj = {}
        for at in attrs:
            if hasattr(o, at):
                if at == 'data' and type(getattr(o, at)) is datetime:
                    obj[at] = getattr(o, at).isoformat()
                else:
                    obj[at] = getattr(o, at)
        if hasattr(o, 'sailkapena'):
            obj['sailkapena'] = [sailk.format_for_json() for sailk in sorted(o.sailkapena)]
        return obj
