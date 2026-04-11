import asyncio
from ..dao import emaitzak, taldeak
from ..models.emaitzak import Emaitza
from ..models.estropadak import Estropada


def get_emaitza_id(estropada: Estropada, talde_izena: str) -> str:
    talde_izena = talde_izena.replace(' ', '-')
    id = f'{estropada.data.strftime("%Y-%m-%d")}_{estropada.liga}_{talde_izena}'
    return id

class EmaitzakLogic:
    @staticmethod
    async def create_emaitza(emaitza: dict):
        talde_izen_normalizatua = await asyncio.to_thread(taldeak.get_talde_izen_normalizatua, emaitza['talde_izena'])
        izena = talde_izen_normalizatua.replace(' ', '-')
        emaitza['_id'] = f'{emaitza['estropada_data'].strftime("%Y-%m-%d")}_{emaitza["liga"].value}_{izena}'
        del emaitza['id']
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
                **emaitza.model_dump(),
            )
            emaitzak.insert_emaitza_into_db(emaitza_)
        return True
