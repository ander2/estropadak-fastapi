from dataclasses import dataclass, field


@dataclass(kw_only=True)
class Sailkapena:
    talde_izena: str
    kalea: int
    tanda: int
    tanda_postua: int
    denbora: str
    posizioa: int
    puntuazioa: int
    kategoria: str | None = None
    ziabogak: list[str] = field(default_factory=list)

    def format_for_json(self):
        tanda_obj = {
            "talde_izena": self.talde_izena,
            "kalea": self.kalea,
            "tanda": self.tanda,
            "tanda_postua": self.tanda_postua,
            "ziabogak": self.ziabogak,
            "denbora": self.denbora,
            "posizioa": self.posizioa,
            "puntuazioa": self.puntuazioa,
        }
        if hasattr(self, 'kategoria') and self.kategoria:
            tanda_obj['kategoria'] = self.kategoria
        return tanda_obj
    
    def dump_dict(self):
        doc = self.__dict__
        if '_rev' in doc and not doc['_rev']:
            del doc['_rev']
        return doc


@dataclass(kw_only=True)
class SailkapenaDoc(Sailkapena):
    _id: str | None = None
    _rev: str | None = None
    type: str
    estropada_data: str
    estropada_izena: str
    estropada_id: str
    liga: str
    talde_izen_normalizatua: str
    # talde_izena: str
    # kalea: int
    # tanda: int
    # tanda_postua: int
    # denbora: str
    # posizioa: int
    # puntuazioa: int
    # kategoria: str | None = None
    # ziabogak: list[str] = field(default_factory=list)
