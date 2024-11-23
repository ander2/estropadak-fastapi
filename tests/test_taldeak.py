import pytest
from fastapi.testclient import TestClient

from app.main import api

client = TestClient(api)


def testTaldeak():
    rv = client.get('/taldeak?league=ACT&year=2019')
    assert rv.status_code == 200
    taldeak = rv.json()
    assert len(taldeak) == 12
    assert all(['name' in taldea for taldea in taldeak])
    assert all(['alt_names' in taldea for taldea in taldeak])
    assert all(['short' in taldea for taldea in taldeak])


@pytest.mark.parametrize('year, league',
                         [('aaa', 'ACT'),
                          ('', 'AT'),
                          (2015, 1),
                          (2015, 'ATC')])
def testTaldeakInvalidParams(year, league):
    rv = client.get(f'/taldeak?league={league}&year={year}')
    assert rv.status_code == 400
