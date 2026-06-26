import asyncio
import datetime
import logging

from ..dao import emaitzak, estropadak, years
from ..logic.emaitzak import EmaitzakLogic, create_emaitza, get_emaitza_id
from ..models.estropadak import Estropada
from ..models.emaitzak import Emaitza, EmaitzaBateratua
from app.common.errors import NotFoundError
from app.config import DEFAULT_LOGGER

logger = logging.getLogger(DEFAULT_LOGGER)


class EstropadakLogic():

    @staticmethod
    async def create_estropada(estropada: Estropada) -> Estropada:
        izena = estropada.izena.replace(' ', '-')
        id = f'{estropada.data.strftime("%Y-%m-%d")}_{estropada.liga.value}_{izena}'
        estropada_ = Estropada(
            _id=id,
            **estropada.model_dump(exclude_unset=True)
        )

        new_estropada = await asyncio.to_thread(estropadak.insert_estropada_into_db, estropada_)

        logger.info(f"Generating emaitza for sailkapena: {len(estropada.sailkapena) > 0}")
        if len(estropada.sailkapena) > 0:
            EmaitzakLogic.create_emaitzak_from_estropada(new_estropada)

        return Estropada(**new_estropada.model_dump(by_alias=True))

    @staticmethod
    async def update_estropada(estropada_id: str, estropada: Estropada):
        if estropada.liga == 'EUSKOTREN':
            estropada.liga = 'euskotren'
        for new_emaitza in estropada.sailkapena:
            emaitza_id = get_emaitza_id(estropada, new_emaitza.talde_izena)
            try:
                emaitza = emaitzak.get_emaitza_by_id(emaitza_id)
                await EmaitzakLogic.update_emaitza(emaitza.id, emaitza)
            except NotFoundError:
                emaitza = await create_emaitza(new_emaitza,
                                               estropada_id,
                                               estropada.izena,
                                               estropada.data,
                                               estropada.liga)
                await EmaitzakLogic.create_emaitza(emaitza.model_dump())
        return await asyncio.to_thread(estropadak.update_estropada_into_db, estropada_id, estropada)

    @staticmethod
    async def get_estropada(estropada_id) -> Estropada:
        estropada = await asyncio.to_thread(estropadak.get_estropada_by_id, estropada_id)
        if estropada.bi_jardunaldiko_bandera:
            estropada.bi_eguneko_sailkapena = []
            estropada_bi = await asyncio.to_thread(estropadak.get_estropada_by_id, estropada.related_estropada)
            if (len(estropada.sailkapena) > 0 and
                len(estropada_bi.sailkapena) > 0):
                if estropada.jardunaldia == 1:
                    denborak_bat = {sailk.talde_izena: sailk.denbora for sailk in estropada.sailkapena}
                    denborak_bi = {sailk.talde_izena: sailk.denbora for sailk in estropada_bi.sailkapena}
                else:
                    denborak_bat = {sailk.talde_izena: sailk.denbora for sailk in estropada_bi.sailkapena}
                    denborak_bi = {sailk.talde_izena: sailk.denbora for sailk in estropada.sailkapena}
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
                    estropada.bi_eguneko_sailkapena.append(EmaitzaBateratua(
                        talde_izena=taldea,
                        lehen_jardunaldiko_denbora=denbora,
                        bigarren_jardunaldiko_denbora=denborak_bi[taldea],
                        denbora_batura=totala_str
                    ))
                    estropada.bi_eguneko_sailkapena = sorted(
                        estropada.bi_eguneko_sailkapena,
                        key=lambda x: x.denbora_batura)
                    for ind, item in enumerate(estropada.bi_eguneko_sailkapena):
                        item.posizioa = ind + 1
        return Estropada(**estropada.model_dump(by_alias=True))

    def _validate_league_year(self, league: str, year: int) -> bool:
        if not league and not year:
            return True
        all_years = years.get_years_from_db()
        if league in all_years:
            return year in all_years[league]
        else:
            return False

    @staticmethod
    async def delete_estropada(estropada_id):
        await asyncio.to_thread(estropadak.delete_estropada_from_db, estropada_id)
