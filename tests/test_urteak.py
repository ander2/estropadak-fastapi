import json
import logging
import pytest

from fastapi.testclient import TestClient
from app.config import LEAGUES
from app.main import api as app

client = TestClient(app)
logger = logging.getLogger('estropadak')


def testYears():
    rv = client.get('/years')
    assert rv.status_code == 200
    years = rv.json()
    supported_leagues = ['act', 'arc1', 'arc2', 'euskotren', 'ete', 'gbl', 'bbl', 'gtl', 'btl', 'txapelketak']
    for res in years:
        assert res['name'] in supported_leagues
        if res['name'] == 'act':
            assert min(res['years']) > 2002
        elif res['name'] == 'arc1' or res['name'] == 'arc2':
            assert min(res['years']) > 2005
        elif res['name'] == 'euskotren':
            assert min(res['years']) > 2008
        elif res['name'] == 'ete':
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
