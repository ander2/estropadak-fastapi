import logging

from fastapi.testclient import TestClient
from app.models.estropadak import EstropadaTypeEnum
from app.main import api as app

client = TestClient(app)
logger = logging.getLogger('estropadak')


def testYears():
    rv = client.get('/years')
    assert rv.status_code == 200
    years = rv.json()
    for res in years:
        assert res['name'] in EstropadaTypeEnum
        if res['name'] == EstropadaTypeEnum.ACT:
            assert min(res['years']) > 200
        elif res['name'] == EstropadaTypeEnum.ARC1 or res['name'] == EstropadaTypeEnum.ARC2:
            assert min(res['years']) > 2005
        elif res['name'] == EstropadaTypeEnum.EUSKOTREN:
            assert min(res['years']) > 2008
        elif res['name'] == EstropadaTypeEnum.ETE:
            assert min(res['years']) > 2017


def testYearsByLeague():
    rv = client.get('/years/ACT')
    res = rv.json()
    assert len(res['years']) > 0


def testYearsPutProtectedEndpointWithoutCredentials():
    rv = client.put('/years/ACT', json={'urteak': list(range(2003, 2022))})
    logger.debug(rv.text)
    assert rv.status_code == 401


def testYearsPutProtectedEndpoint(credentials):
    rv = client.post('/auth', json=credentials)
    token = rv.json()['access_token']
    rv = client.put('/years/ACT', json={'urteak': list(range(2003, 2022))}, headers=[('Authorization', f'Bearer {token}')])
    assert rv.status_code == 200


def testYearsPutBadParams(credentials):
    rv = client.post('/auth', json=credentials)
    token = rv.json()['access_token']
    # Bad param name
    rv = client.put('/years/ACT', json={'urte': list(range(2003, 2022))}, headers=[('Authorization', f'Bearer {token}')])
    assert rv.status_code == 400

    # Bad values
    rv = client.put('/years/ACT', json={'urteak': list('abc')}, headers=[('Authorization', f'Bearer {token}')])
    assert rv.status_code == 400
