from datetime import datetime
from pydantic import BaseModel
from .estropadak import EstropadaTypeEnum

class Emaitza(BaseModel):
    id: str  | None = None
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
