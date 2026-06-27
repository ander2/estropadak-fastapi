import asyncio
import logging
from datetime import datetime

from ..dao import emaitzak, taldeak
from ..models.emaitzak import Emaitza, EmbedEmaitza
from ..models.estropadak import Estropada
from app.config import DEFAULT_LOGGER

logger = logging.getLogger(DEFAULT_LOGGER)


def get_emaitza_id(estropada: Estropada, talde_izena: str) -> str:
    taldea = taldeak.get_talde_izena(talde_izena)
    taldea = taldea.replace(' ', '-')
    id = f'{estropada.data.strftime("%Y-%m-%d")}_{estropada.liga}_{taldea}'
    return id

async def create_emaitza(new_emaitza: EmbedEmaitza, estropada_id: str, estropada_izena: str, estropada_data: datetime, liga: str) -> Emaitza:
    talde_izen_normalizatua = await asyncio.to_thread(taldeak.get_talde_izen_normalizatua, new_emaitza.talde_izena)
    emaitza = Emaitza(**new_emaitza.model_dump(exclude_none=True),
                      estropada_data=estropada_data,
                      estropada_id=estropada_id,
                      estropada_izena=estropada_izena,
                      liga=liga,
                      talde_izen_normalizatua=talde_izen_normalizatua,
                     )
    return emaitza

class EmaitzakLogic:
    @staticmethod
    async def create_emaitza(emaitza: dict):
        talde_izen_normalizatua = await asyncio.to_thread(taldeak.get_talde_izen_normalizatua, emaitza['talde_izena'])
        izena = talde_izen_normalizatua.replace(' ', '-')
        emaitza['_id'] = f'{emaitza['estropada_data'].strftime("%Y-%m-%d")}_{emaitza["liga"].value}_{izena}'
        del emaitza['id']
        logger.info(f"Creating new emaitza {emaitza['_id']}")
        emaitza_ = Emaitza(**emaitza)
        doc_created = await asyncio.to_thread(emaitzak.insert_emaitza_into_db, emaitza_)
        return doc_created

    @staticmethod
    async def update_emaitza(emaitza_id: str, emaitza: Emaitza):
        doc_updated = await asyncio.to_thread(emaitzak.update_emaitza_into_db, emaitza_id, emaitza)
        return doc_updated

    @staticmethod
    def create_emaitzak_from_estropada(estropada: Estropada):
        for emaitza in estropada.sailkapena:
            talde_izen_normalizatua = taldeak.get_talde_izen_normalizatua(emaitza.talde_izena)
            izena = talde_izen_normalizatua.replace(' ', '-')
            id = f'{estropada.data.strftime("%Y-%m-%d")}_{estropada.liga}_{izena}'
            emaitza_ = Emaitza(
                _id=id,
                estropada_data=estropada.data,
                estropada_izena=estropada.izena,
                estropada_id=estropada.id,
                liga=estropada.liga,
                talde_izen_normalizatua=talde_izen_normalizatua,
                **emaitza.model_dump(exclude_none=True),
            )
            emaitzak.insert_emaitza_into_db(emaitza_)
        return True
