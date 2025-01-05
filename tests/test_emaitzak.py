import pytest
import json

from fastapi.testclient import TestClient

from app.config import config
from app.dao.db_connection import get_db_connection
from app.main import api as app

client = TestClient(app)

@pytest.fixture()
def clean_up():
    yield
    docs = [
        '2019-06-18_ARC1_San-Juan',
        '2019-06-18_ARC1_Donostiarra',
        '2019-06-18_ARC1_Ondarroa'
    ]
    with get_db_connection() as database:
        for doc_id in docs:
            try:
                res = database.get_document(config["DBNAME"], doc_id)
                if res.status_code == 200:
                    doc = res.get_result()
                    database.delete_document(config["DBNAME"], doc_id, rev=doc["_rev"])
            except Exception:
                pass


def testEmaitzakByCriteria():
    query = {
        "type": "emaitza",
        "liga": "ACT",
        "estropada_data": {
            "$and": [{
                "$gt": "2019-01-01"
            }, {
                "$lt": "2019-12-31"
            }
            ]
        },
        "talde_izen_normalizatua": "Hondarribia"
    }
    rv = client.get(f'/emaitzak?criteria={json.dumps(query)}')
    assert rv.status_code == 200
    emaitzak = rv.json()
    assert emaitzak['total'] == 20
    assert len(emaitzak['docs']) == 20


def testEmaitzakByBadCriteria():
    rv = client.get(f'/emaitzak?criteria={"foo"}')
    assert rv.status_code == 400


def testEmaitzakByCriteriaPagination():
    query = {
        "type": "emaitza",
        "liga": "ACT",
        "estropada_data": {
            "$and": [{
                "$gt": "2019-01-01"
            }, {
                "$lt": "2019-12-31"
            }
            ]
        },
        "talde_izen_normalizatua": "Hondarribia"
    }
    rv = client.get(f'/emaitzak?criteria={json.dumps(query)}&page=0&count=5')
    emaitzak = rv.json()
    assert emaitzak['total'] == 20
    assert len(emaitzak['docs']) == 5


@pytest.mark.skip('Test in wrong branch')
def testEmaitzakByCriteriaBadPagination():
    query = {
        "type": "emaitza",
        "liga": "ACT",
        "estropada_data": {
            "$and": [{
                "$gt": "2019-01-01"
            }, {
                "$lt": "2019-12-31"
            }
            ]
        },
        "talde_izen_normalizatua": "Hondarribia"
    }
    rv = client.get(f'/emaitzak?criteria={json.dumps(query)}&page=2&count=20')
    assert rv.status_code == 400


def testEmaitzakCreationWithoutCredentials():
    emaitza_data = {
        "talde_izena": "SAN JUAN",
        "tanda_postua": 2,
        "tanda": 2,
        "denbora": "20:30,28",
        "posizioa": 6,
        "ziabogak": [
            "2:16",
            "7:36",
            "12:35"
        ],
        "puntuazioa": 7,
        "kalea": 5,
        "estropada_izena": "III. FEGEMU BANDERA",
        "estropada_data": "2019-06-18T12:00",  # Fake date, just to not conflict
        "liga": "ARC1",
        "estropada_id": "37a4adac975ce9ab29decb228900718b",
        "talde_izen_normalizatua": "San Juan"
    }
    rv = client.post('/emaitzak', json=emaitza_data)
    assert rv.status_code == 401


def testEmaitzakCreationWithCredentials(credentials, clean_up):
    rv = client.post('/auth', json=credentials)
    token = rv.json()['access_token']
    emaitza_data = {
        "talde_izena": "SAN JUAN",
        "tanda_postua": 2,
        "tanda": 2,
        "denbora": "20:30,28",
        "posizioa": 6,
        "ziabogak": [
            "2:16",
            "7:36",
            "12:35"
        ],
        "puntuazioa": 7,
        "kalea": 5,
        "estropada_izena": "III. FEGEMU BANDERA",
        "estropada_data": "2019-06-18 12:00",  # Fake date, just to not conflict
        "liga": "ARC1",
        "estropada_id": "37a4adac975ce9ab29decb228900718b",
        "type": "emaitza",
        "talde_izen_normalizatua": "San Juan"
    }
    rv = client.post(
        '/emaitzak',
        json=emaitza_data,
        headers=[('Authorization', f'Bearer {token}')])
    assert rv.status_code == 201

    rv = client.get('/emaitzak/2019-06-18_ARC1_San-Juan')
    assert rv.status_code == 200


def testEmaitzakCreationWithInvalidData(credentials):
    rv = client.post('/auth', json=credentials)
    token = rv.json()['access_token']
    emaitza_data = {
        "tanda_postua": 2,
        "tanda": 2,
        "denbora": "20:30,28",
        "posizioa": 6,
        "ziabogak": [
            "2:16",
            "7:36",
            "12:35"
        ],
        "puntuazioa": 7,
        "kalea": 5,
        "estropada_izena": "III. FEGEMU BANDERA",
        "estropada_data": "2019-06-18 12:00",  # Fake date, just to not conflict
        "liga": "ARC1",
        "estropada_id": "37a4adac975ce9ab29decb228900718b",
        "type": "emaitza"
    }
    rv = client.post(
        '/emaitzak',
        json=emaitza_data,
        headers=[('Authorization', f'Bearer {token}')])
    assert rv.status_code == 400


def testEmaitzakModificationWithoutCredentials(credentials, clean_up):
    rv = client.post('/auth', json=credentials)
    token = rv.json()['access_token']
    emaitza_data = {
        "talde_izena": "Donostiarra",
        "tanda_postua": 2,
        "tanda": 2,
        "denbora": "20:30,28",
        "posizioa": 6,
        "ziabogak": [
            "2:16",
            "7:36",
            "12:35"
        ],
        "puntuazioa": 7,
        "kalea": 5,
        "estropada_izena": "III. FEGEMU BANDERA",
        "estropada_data": "2019-06-18 12:00",   # Fake date, just to not conflict
        "liga": "ARC1",
        "estropada_id": "37a4adac975ce9ab29decb228900718b",
        "type": "emaitza",
        "talde_izen_normalizatua": "Donostiarra"
    }
    rv = client.post(
        '/emaitzak',
        json=emaitza_data,
        headers=[('Authorization', f'Bearer {token}')])
    assert rv.status_code == 201

    emaitza_data['posizioa'] = 7
    rv = client.put(
        '/emaitzak/2019-06-18_ARC1_Donostiarra',
        json=emaitza_data)
    assert rv.status_code == 401


def testEmaitzakModificationWithCredentials(credentials, clean_up):
    rv = client.post('/auth', json=credentials)
    token = rv.json()['access_token']
    emaitza_data = {
        "talde_izena": "Donostiarra",
        "tanda_postua": 2,
        "tanda": 2,
        "denbora": "20:30,28",
        "posizioa": 6,
        "ziabogak": [
            "2:16",
            "7:36",
            "12:35"
        ],
        "puntuazioa": 7,
        "kalea": 5,
        "estropada_izena": "III. FEGEM BANDERA",
        "estropada_data": "2019-06-18T12:00",  # Fake date, just to not conflict
        "liga": "ARC1",
        "estropada_id": "37a4adac975ce9ab29decb228900718b",
        "type": "emaitza",
        "talde_izen_normalizatua": "Donostiarra"
    }
    rv = client.post(
        '/emaitzak',
        json=emaitza_data,
        headers=[('Authorization', f'Bearer {token}')])
    assert rv.status_code == 201

    emaitza_data['posizioa'] = 7
    emaitza_data['kalea'] = 3

    rv = client.put(
        '/emaitzak/2019-06-18_ARC1_Donostiarra',
        json=emaitza_data,
        headers=[('Authorization', f'Bearer {token}')])
    assert rv.status_code == 200

    rv = client.get('/emaitzak/2019-06-18_ARC1_Donostiarra')
    assert rv.status_code == 200
    emaitza = rv.json()
    assert emaitza['posizioa'] == 7
    assert emaitza['kalea'] == 3


def testEmaitzakDeletion(credentials, clean_up):
    rv = client.post('/auth', json=credentials)
    token = rv.json()['access_token']
    emaitza_data = {
        "talde_izena": "ONDARROA",
        "tanda_postua": 2,
        "tanda": 2,
        "denbora": "20:30,28",
        "posizioa": 6,
        "ziabogak": [
            "2:16",
            "7:36",
            "12:35"
        ],
        "puntuazioa": 7,
        "kalea": 5,
        "estropada_izena": "III. FEGEMU BANDERA",
        "estropada_data": "2019-06-18 12:00",  # Fake date, just to not conflict
        "liga": "ARC1",
        "estropada_id": "37a4adac975ce9ab29decb228900718b",
        "type": "emaitza",
        "talde_izen_normalizatua": "Ondarroa"
    }
    rv = client.post(
        '/emaitzak',
        json=emaitza_data,
        headers=[('Authorization', f'Bearer {token}')])
    assert rv.status_code == 201

    id = "2019-06-18_ARC1_Ondarroa"
    rv = client.delete(
        f'/emaitzak/{id}',
        headers=[('Authorization', f'Bearer {token}')])
    assert rv.status_code == 204


def test_non_existant_emaitza_deletion(credentials):
    rv = client.post('/auth', json=credentials)
    token = rv.json()['access_token']
    id = "2019-06-18_ARC1_Ondarroaxxxxxx"
    rv = client.delete(
        f'/emaitzak/{id}',
        headers=[('Authorization', f'Bearer {token}')])
    assert rv.status_code == 204
