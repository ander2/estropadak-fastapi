import logging
import pytest

from fastapi.testclient import TestClient
from app.main import api as app
from app.config import DEFAULT_LOGGER, PAGE_SIZE

client = TestClient(app)
logger = logging.getLogger(DEFAULT_LOGGER)

@pytest.fixture()
def create_estropada(credentials):
    rv = client.post('/auth', json=credentials)
    token = rv.json()['access_token']
    rv = client.post('/estropadak', json={
        "izena": "Estropada test4",
        "data": "2021-06-02 17:00",
        "liga": "ARC1",
        "sailkapena": [],
        "type": "estropada"
    }, headers=[('Authorization', f'Bearer {token}')])
    yield "2021-06-02_ARC1_Estropada-test4"
    client.delete('/estropadak/2021-06-02_ARC1_Estropada-test4', headers=[('Authorization', f'Bearer {token}')])
    client.delete('/emaitzak/2021-06-02_ARC1_Arkote', headers=[('Authorization', f'Bearer {token}')])


@pytest.fixture()
def estropada_with_sailkapena(credentials):
    yield {
        "izena": "Estropada test",
        "data": "2021-06-01T17:00:00",
        "lekua": "Leku bat",
        "liga": "ACT",
        "sailkapena": [{
            "talde_izena": "KAIKU",
            "denbora": "20:14,84",
            "puntuazioa": 5,
            "posizioa": 8,
            "tanda": 1,
            "tanda_postua": 1,
            "kalea": 1,
            "ziabogak": [
                "05:06",
                "09:56",
                "15:24"
            ]
        }]
    }
    rv = client.post('/auth', json=credentials)
    token = rv.json()['access_token']
    estropada_id = "2021-06-01_ACT_Estropada-test"
    client.delete(f'/estropadak/{estropada_id}', headers=[('Authorization', f'Bearer {token}')])
    emaitza_id = "2021-06-01_ACT_Kaiku"
    client.delete(f'/emaitzak/{emaitza_id}', headers=[('Authorization', f'Bearer {token}')])

@pytest.fixture()
def clean_up(credentials):
    yield
    rv = client.post('/auth', json=credentials)
    doc_ids = (
        "2021-06-01_ACT_Estropada-test",
        "2021-06-01_EUSKOTREN_Estropada-test",
    )
    token = rv.json()['access_token']
    for doc_id in doc_ids:
        try:
            client.delete(f'/estropadak/{doc_id}', headers=[('Authorization', f'Bearer {token}')])
        except Exception:
            pass


def test_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "estropadak API"}


def test_estropadak():
    response = client.get("/estropadak")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0
    assert len(data["docs"]) == PAGE_SIZE


def test_estropadak_list():
    response = client.get('/estropadak?league=ACT&year=2010', )
    estropadak = response.json()
    assert response.status_code == 200
    assert len(estropadak['docs']) == 20
    assert estropadak['total'] == 20
    assert estropadak['docs'][0]['id'] == "2010-07-03_ACT_I-Bandera-SEAT---G.P.-Villa-de-Bilbao"
    assert estropadak['docs'][0]["izena"] == "I Bandera SEAT - G.P. Villa de Bilbao"
    assert estropadak['docs'][0]["data"] == "2010-07-03T17:00:00"
    assert estropadak['docs'][0]["liga"] == "ACT"
    assert estropadak['docs'][0]["urla"] == "http://www.euskolabelliga.com/resultados/ver.php?id=eu&r=1269258408"
    assert estropadak['docs'][0]["lekua"] == "Bilbao Bizkaia"
    assert estropadak['docs'][0]["kategoriak"] == []


def test_estropadak_list_only_year():
    rv = client.get('/estropadak?year=2022&count=20')
    assert rv.status_code == 200
    estropadak = rv.json()
    assert 'docs' in estropadak
    assert 'total' in estropadak
    assert len(estropadak['docs']) == 20
    assert estropadak['total'] == 115


def test_estropadak_list_only_league():
    rv = client.get('/estropadak?league=ACT&count=20', )
    assert rv.status_code == 200
    estropadak = rv.json()
    assert 'docs' in estropadak
    assert 'total' in estropadak
    assert len(estropadak['docs']) == 20
    # assert estropadak['total'] == 418


def test_estropadak_list_without_results():
    rv = client.get('/estropadak?league=ACT&year=1900')
    assert rv.status_code == 200
    estropadak = rv.json()
    assert estropadak['total'] == 0


def test_estropadak_list_only_count_limit():
    rv = client.get('/estropadak?count=2')
    assert rv.status_code == 200
    estropadak = rv.json()
    assert 'docs' in estropadak
    assert 'total' in estropadak
    assert len(estropadak['docs']) == 2


def test_estropadak_list_with_wrong_league():
    rv = client.get('/estropadak?league=actt&year=2010')
    assert rv.status_code == 400


def test_estropadak_list_with_Euskotren_league():
    rv = client.get('/estropadak?league=EUSKOTREN&year=2020')
    assert rv.status_code == 200
    estropadak = rv.json()
    assert estropadak['total'] == 14


def test_estropadak_with_bad_pagination_params():
    rv = client.get('/estropadak?page=r')
    assert rv.status_code == 400
    rv = client.get('/estropadak?count=r')
    assert rv.status_code == 400


def test_estropada():
    rv = client.get('/estropadak/1c79d46b8c74ad399d54fd7ee40005e3')
    assert rv.status_code == 200
    estropada = rv.json()
    assert estropada["izena"] == "III Bandera Euskadi Basque Country"
    assert estropada["id"] == "1c79d46b8c74ad399d54fd7ee40005e3"
    assert estropada["data"] == "2015-06-28T12:00:00"
    assert estropada["lekua"] == "Málaga"
    assert estropada["liga"] == "ACT"
    assert not estropada["bi_jardunaldiko_bandera"]
    assert estropada["urla"] == "http://www.euskolabelliga.com/resultados/ver.php?id=eu&r=1427700021"
    assert estropada["puntuagarria"]
    assert estropada["oharrak"] == "" or estropada["oharrak"] is None
    assert len(estropada["sailkapena"]) == 12


def test_estropada_two_rounds():
    rv = client.get('/estropadak/2017-08-20_ACT_XL.-Zarauzko-Estropadak')
    assert rv.status_code == 200
    estropada = rv.json()
    assert estropada["bi_jardunaldiko_bandera"]
    assert estropada["jardunaldia"] == 2
    assert estropada["related_estropada"] == "2017-08-19_ACT_XL.-Zarauzko-Estropadak"
    assert len(estropada["bi_eguneko_sailkapena"]) == 12
    assert estropada["bi_eguneko_sailkapena"][8] == {
        "talde_izena": "Tirán Pereira",
        "lehen_jardunaldiko_denbora": "21:49,88",
        "bigarren_jardunaldiko_denbora": "20:56,54",
        "denbora_batura": "42:46,42",
        "posizioa": 9
    }


def test_estropada_two_rounds_with_excluded_team():
    rv = client.get('/estropadak/2018-07-07_ACT_II-Bandeira-Cidade-da-Coruña-J1')
    assert rv.status_code == 200
    estropada = rv.json()
    assert estropada["bi_jardunaldiko_bandera"]
    assert estropada["bi_eguneko_sailkapena"][11] == {
        "talde_izena": "San Pedro",
        "lehen_jardunaldiko_denbora": "Excl",
        "bigarren_jardunaldiko_denbora": "22:05,28",
        "denbora_batura": "Excl.",
        "posizioa": 12
    }

def test_estropada_not_found():
    rv = client.get('/estropadak/fuck')
    assert rv.status_code == 404


def test_estropada_creation_with_credentials(credentials, clean_up):
    rv = client.post('/auth', json=credentials)
    token = rv.json()['access_token']
    rv = client.post('/estropadak', json={
        "izena": "Estropada test",
        "data": "2021-06-01 17:00",
        "liga": "ACT",
        "sailkapena": [],
        "lekua": "Nonbait",
        "type": "estropada"
    }, headers=[('Authorization', f'Bearer {token}')])
    assert rv.status_code == 201
    estropada = rv.json()
    assert estropada['id'] == '2021-06-01_ACT_Estropada-test'
    assert estropada['izena'] == 'Estropada test'


def test_estropada_creation_with_credentials_Euskotren_liga(credentials):
    rv = client.post('/auth', json=credentials)
    token = rv.json()['access_token']
    rv = client.post('/estropadak', json={
        "izena": "Estropada test",
        "data": "2021-06-01 17:00",
        "liga": "EUSKOTREN",
        "sailkapena": [],
        "lekua": "Nonbait"
    }, headers=[('Authorization', f'Bearer {token}')])
    assert rv.status_code == 201


def test_estropada_creation_without_credentials(credentials):
    rv = client.post('/estropadak', json={
        "izena": "Estropada test",
        "data": "2021-06-01 17:00",
        "liga": "ACT",
        "sailkapena": []
    })
    assert rv.status_code == 401


def test_estropada_modification_without_credentials(credentials):
    rv = client.put('/estropadak/2021_act_estropada', json={
        "izena": "Estropada test",
        "data": "2021-06-01 17:00",
        "liga": "ACT",
        "sailkapena": [],
    })
    assert rv.status_code == 401


def test_estropada_modification_with_credentials(credentials, create_estropada):
    estropada_id = create_estropada
    rv = client.post('/auth', json=credentials)
    token = rv.json()['access_token']
    rv = client.put(f'/estropadak/{estropada_id}', json={
        "izena": "Estropada test2",
        "data": "2021-06-01 17:30",
        "liga": "ARC1",
        "sailkapena": [],
        "lekua": "Nonbait"
    }, headers=[('Authorization', f'Bearer {token}')])
    assert rv.status_code == 200
    rv = client.get(f'/estropadak/{estropada_id}')
    assert rv.status_code == 200
    recovered_doc = rv.json()
    recovered_doc['izena'] == "Estropada test2"
    recovered_doc['data'] == "2021-06-01 17:30"
    recovered_doc['liga'] == "arc1"
    recovered_doc['lekua'] == 'Nonbait'
    recovered_doc['sailkapena'] == []


def test_estropada_deletion_without_credentials(create_estropada):
    estropada_id = create_estropada
    rv = client.delete(f'/estropadak/{estropada_id}')
    assert rv.status_code == 401


def test_estropada_deletion_with_credentials(credentials):
    rv = client.post('/auth', json=credentials)
    token = rv.json()['access_token']
    rv = client.post('/estropadak', json={
        "izena": "Estropada test3",
        "data": "2021-06-02 17:00",
        "liga": "ARC1",
        "lekua": "Leku bat",
        "sailkapena": []
    }, headers=[('Authorization', f'Bearer {token}')])
    assert rv.status_code == 201

    rv = client.delete('/estropadak/2021-06-02_ARC1_Estropada-test3',
                       headers=[('Authorization', f'Bearer {token}')])
    assert rv.status_code == 204

def test_estropada_deletion_with_db_error(credentials, mocker):
    rv = client.post('/auth', json=credentials)
    token = rv.json()['access_token']

    mocker.patch("app.dao.estropadak.get_db_connection", side_effect=Exception("Connection error"))
    estropada_id = "foofoo"
    rv = client.delete(f'/estropadak/{estropada_id}',
                       headers=[('Authorization', f'Bearer {token}')])
    assert rv.status_code == 400

def test_estropada_deletion_on_non_existant_estropada(credentials):
    rv = client.post('/auth', json=credentials)
    token = rv.json()['access_token']

    estropada_id = "foofoo"
    rv = client.delete(f'/estropadak/{estropada_id}',
                       headers=[('Authorization', f'Bearer {token}')])
    assert rv.status_code == 204


def test_estropada_creation_with_missing_data_in_model(credentials):
    rv = client.post('/auth', json=credentials)
    token = rv.json()['access_token']
    rv = client.post('/estropadak', json={
        "izena": "Estropada test5",
        "data": "2021-06-10 17:00",
        "sailkapena": []
    }, headers=[('Authorization', f'Bearer {token}')])
    assert rv.status_code == 400

    rv = client.post('/estropadak', json={
        "izena": "Estropada test5",
        "liga": "ARC1",
        "sailkapena": []
    }, headers=[('Authorization', f'Bearer {token}')])
    assert rv.status_code == 400


def test_estropada_creation_with_unsupported_liga(credentials):
    rv = client.post('/auth', json=credentials)
    token = rv.json()['access_token']
    rv = client.post('/estropadak', json={
        "izena": "Estropada test5",
        "liga": "ACTT",
        "data": "2021-06-10 17:00",
        "sailkapena": []
    }, headers=[('Authorization', f'Bearer {token}')])
    assert rv.status_code == 400


def test_estropada_creation_with_sailkapena(credentials, estropada_with_sailkapena):
    rv = client.post('/auth', json=credentials)
    token = rv.json()['access_token']

    rv = client.post('/estropadak', json=estropada_with_sailkapena, headers=[('Authorization', f'Bearer {token}')])
    estropada_id = rv.json()["id"]

    rv = client.get(f'/estropadak/{estropada_id}')
    assert rv.status_code == 200

    rv = client.get('/emaitzak/2021-06-01_ACT_Kaiku')
    assert rv.status_code == 200

def test_estropada_modification_with_sailkapena(credentials, create_estropada):
    estropada_id = create_estropada
    rv = client.post('/auth', json=credentials)
    token = rv.json()['access_token']
    rv = client.put(f'/estropadak/{estropada_id}', json={
        "izena": "Estropada test2",
        "data": "2021-06-02 17:30",
        "liga": "ARC1",
        "sailkapena": [{
            "talde_izena": "ARKOTE SEGUROS BILBAO",
            "denbora": "20:14,84",
            "puntuazioa": 5,
            "posizioa": 8,
            "tanda": 1,
            "tanda_postua": 1,
            "kalea": 1,
            "ziabogak": [
                "05:06",
                "09:56",
                "15:24"
            ]
        }],
        "lekua": "Nonbait"
    }, headers=[('Authorization', f'Bearer {token}')])
    assert rv.status_code == 200
    emaitza_id = '2021-06-02_ARC1_Arkote'
    res = client.get(f'/emaitzak/{emaitza_id}')
    assert res.status_code == 200
