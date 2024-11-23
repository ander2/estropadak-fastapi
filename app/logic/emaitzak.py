from ..dao.models.estropadak import Estropada
from ..dao.models.sailkapenak import Sailkapena, SailkapenaDoc
from ..dao.emaitzak import EmaitzakDAO
from ..dao.taldeak import TaldeakDAO


class EmaitzakLogic:
    @staticmethod
    def update_emaitza(emaitza_id, emaitza):
        pass
        # emaitza['type'] = 'emaitza'
        # talde_izen_normalizatua = TaldeakDAO.get_talde_izen_normalizatua(emaitza['talde_izena'])
        # emaitza['talde_izen_normalizatua'] = talde_izen_normalizatua
        # return EmaitzakDAO.update_emaitza_into_db(emaitza_id, emaitza)

    @staticmethod
    def create_emaitzak_from_estropada(estropada: Estropada):
        for emaitza in estropada.sailkapena:
            talde_izen_normalizatua = TaldeakDAO.get_talde_izen_normalizatua(emaitza.talde_izena)
            izena = talde_izen_normalizatua.replace(' ', '-')
            id = f'{estropada.data.strftime("%Y-%m-%d")}_{estropada.liga}_{izena}'
            emaitza_ = SailkapenaDoc(
                _id=id,
                estropada_data=estropada.data.isoformat(),
                estropada_izena=estropada.izena,
                estropada_id=estropada._id,
                liga=estropada.liga,
                talde_izen_normalizatua=talde_izen_normalizatua,
                type="emaitza",
                **emaitza.dump_dict(),
            )
            EmaitzakDAO.insert_emaitza_into_db(emaitza_)
        return True
