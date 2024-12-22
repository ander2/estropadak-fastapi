from ..dao.models.estropadak import Estropada
from ..dao.models.sailkapenak import SailkapenaDoc
from ..dao.emaitzak import EmaitzakDAO
from ..dao.taldeak import TaldeakDAO


class EmaitzakLogic:
    @staticmethod
    def create_emaitza(emaitza: dict):
        talde_izen_normalizatua = TaldeakDAO.get_talde_izen_normalizatua(emaitza['talde_izena'])
        izena = talde_izen_normalizatua.replace(' ', '-')
        emaitza['_id'] = f'{emaitza['estropada_data'].strftime("%Y-%m-%d")}_{emaitza["liga"].value}_{izena}'
        del emaitza['id']
        emaitza_ = SailkapenaDoc(**emaitza)
        doc_created = EmaitzakDAO.insert_emaitza_into_db(emaitza_)
        return doc_created

    @staticmethod
    def update_emaitza(emaitza_id: str, emaitza: dict):
        del emaitza['id']
        emaitza['_id'] = emaitza_id
        emaitza_ = SailkapenaDoc(**emaitza)
        doc_updated = EmaitzakDAO.update_emaitza_into_db(emaitza_id, emaitza_)
        return doc_updated

    @staticmethod
    def create_emaitzak_from_estropada(estropada: Estropada):
        for emaitza in estropada.sailkapena:
            talde_izen_normalizatua = TaldeakDAO.get_talde_izen_normalizatua(emaitza.talde_izena)
            izena = talde_izen_normalizatua.replace(' ', '-')
            id = f'{estropada.data.strftime("%Y-%m-%d")}_{estropada.liga}_{izena}'
            emaitza_ = SailkapenaDoc(
                _id=id,
                estropada_data=estropada.data,
                estropada_izena=estropada.izena,
                estropada_id=estropada._id,
                liga=estropada.liga,
                talde_izen_normalizatua=talde_izen_normalizatua,
                type="emaitza",
                **emaitza.dump_dict(),
            )
            EmaitzakDAO.insert_emaitza_into_db(emaitza_)
        return True
