import datetime

from ..models.estropadak import Estropada
from ..dao import estropadak, years
from ..dao.models.estropadak import Estropada as EstropadaModel
from ..dao.models.sailkapenak import Sailkapena
from ..logic.emaitzak import EmaitzakLogic


class EstropadakLogic():

    @staticmethod
    def create_estropada(estropada: Estropada):
        izena = estropada.izena.replace(' ', '-')
        id = f'{estropada.data.strftime("%Y-%m-%d")}_{estropada.liga.value}_{izena}'
        if len(estropada.sailkapena) > 0:
            sailkapena = [Sailkapena(**sailkapena) for sailkapena in estropada.sailkapena]
            delattr(estropada, 'sailkapena')
        else:
            sailkapena = []
            delattr(estropada, 'sailkapena')
        estropada_ = EstropadaModel(
            _id=id,
            type=type,
            sailkapena=sailkapena,
            **estropada.model_dump(exclude_unset=True)
        )
        # data = None
        # try:
        #     data = datetime.datetime.fromisoformat(estropada.data)
        #     logging.info(data)
        # except ValueError:
        #     data = datetime.datetime.strptime(estropada.data, '%Y-%m-%d %H:%M')
        #     estropada['data'] = data.isoformat()

        if estropada_.sailkapena:
            EmaitzakLogic.create_emaitzak_from_estropada(estropada_)

        new_estropada = estropadak.insert_estropada_into_db(estropada_)
        return new_estropada

    @staticmethod
    def update_estropada(estropada_id: str, estropada):
        type = 'estropada'
        if estropada.liga == 'EUSKOTREN':
            estropada.liga = 'euskotren'
        # if estropada.get('sailkapena', []):
        #     # todo implement EmaitzaLogic.create_emaitza
        #     pass
        estropada_ = EstropadaModel(_id=estropada_id,
                                    type=type,
                                    **estropada.model_dump(exclude_unset=True))
        return estropadak.update_estropada_into_db(estropada_id, estropada_)

    @staticmethod
    def get_estropada(estropada_id):
        estropada = estropadak.get_estropada_by_id(estropada_id)
        if estropada and estropada.get('bi_jardunaldiko_bandera'):
            estropada['bi_eguneko_sailkapena'] = []
            estropada_bi = estropadak.get_estropada_by_id(estropada['related_estropada'])
            if (len(estropada.get('sailkapena', [])) > 0 and
                len(estropada_bi.get('sailkapena', [])) > 0):
                denborak_bat = {sailk['talde_izena']: sailk['denbora'] for sailk in estropada['sailkapena']}
                denborak_bi = {sailk['talde_izena']: sailk['denbora'] for sailk in estropada_bi['sailkapena']}
                for taldea, denbora in denborak_bat.items():
                    try:
                        denb1 = datetime.datetime.strptime(denbora, '%M:%S,%f')
                        denb2 = datetime.datetime.strptime(denborak_bi[taldea], '%M:%S,%f')
                        delta = datetime.timedelta(
                            minutes=denb2.minute,
                            seconds=denb2.second,
                            microseconds=denb2.microsecond)
                        totala = denb1 + delta
                        totala_str = totala.strftime('%M:%S,%f')[:-4]
                    except ValueError:
                        if denbora.startswith('Exc') or denborak_bi[taldea].startswith('Exc'):
                            totala_str = 'Excl.'
                    estropada['bi_eguneko_sailkapena'].append({
                        'talde_izena': taldea,
                        'lehen_jardunaldiko_denbora': denbora,
                        'bigarren_jardunaldiko_denbora': denborak_bi[taldea],
                        'denbora_batura': totala_str,
                    })
                    estropada['bi_eguneko_sailkapena'] = sorted(
                        estropada['bi_eguneko_sailkapena'],
                        key=lambda x: x['denbora_batura'])
                    for ind, item in enumerate(estropada['bi_eguneko_sailkapena']):
                        item['posizioa'] = ind + 1
        return estropada

    def _validate_league_year(self, league: str, year: int) -> bool:
        if not league and not year:
            return True
        all_years = years.get_years_from_db()
        if league in all_years:
            return year in all_years[league]
        else:
            return False

    @staticmethod
    def delete_estropada(estropada_id):
        estropadak.delete_estropada_from_db(estropada_id)
