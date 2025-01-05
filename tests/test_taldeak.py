import pytest
from fastapi.testclient import TestClient

from app.main import api

client = TestClient(api)


def test_taldeak():
    rv = client.get('/taldeak?league=ACT&year=2019')
    assert rv.status_code == 200
    taldeak = rv.json()
    assert len(taldeak) == 12
    assert all(['name' in taldea for taldea in taldeak])
    assert all(['alt_names' in taldea for taldea in taldeak])
    assert all(['short' in taldea for taldea in taldeak])

def test_taldeak_by_league():
    rv = client.get('/taldeak?league=ACT')
    assert rv.status_code == 200
    taldeak = rv.json()
    assert len(taldeak) == 26


@pytest.mark.parametrize('year, league',
                         [('aaa', 'ACT'),
                          ('', 'AT'),
                          (2015, 1),
                          (2015, 'ATC')])
def test_taldeak_invalid_params(year, league):
    rv = client.get(f'/taldeak?league={league}&year={year}')
    assert rv.status_code == 400
