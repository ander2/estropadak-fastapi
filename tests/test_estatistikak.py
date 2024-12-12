import logging

import pytest

from fastapi.testclient import TestClient

from app.dao.db_connection import get_db_connection
from app.main import api as app

client = TestClient(app)


def test_get_estatistikak_cumulative():
    rv = client.get('/estatistikak?stat=cumulative&year=2017&league=ACT')
    assert rv.status_code == 200
    estatistikak = rv.json()
    logging.info(estatistikak)
    assert estatistikak['total'] == 12
    assert len(estatistikak['docs']) == 12

@pytest.mark.skip('Not sure if we should support this')
def test_get_estatistikak_cumulative_without_year():
    rv = client.get('/estatistikak?stat=cumulative&league=ACT')
    assert rv.status_code == 200
    estatistikak = rv.json()
    logging.info(estatistikak)
    assert estatistikak['total'] == 19
    assert len(estatistikak['docs']) == 19


@pytest.mark.parametrize("stat, league, year, team, category",[
    ("cumulative", 'ACT1', 2017, None, None),
    ("cumulative", 'ACT', None, None, None),
    ("culative", 'ACT', 2017, None, None)
])
def test_get_estatistikak_with_wrong_params(stat, league, year, team, category):
    rv = client.get(f'/estatistikak?stat={stat}&year={year}&league={league}&team={team}&category={category}')
    assert rv.status_code == 400


def test_get_estatistikak_points():
    rv = client.get('/estatistikak?stat=points&year=2017&league=ACT')
    assert rv.status_code == 200
    estatistikak = rv.json()
    logging.info(estatistikak)
    assert estatistikak['total'] == 12
    assert len(estatistikak['docs']) == 12

def test_get_estatistikak_rank():
    rv = client.get('/estatistikak?stat=rank&year=2017&league=ACT')
    assert rv.status_code == 200
    estatistikak = rv.json()
    logging.info(estatistikak)
    assert estatistikak['total'] == 1
    assert len(estatistikak['docs']) == 1

def test_get_estatistikak_ages():
    rv = client.get('/estatistikak?stat=ages&year=2017&league=ACT')
    assert rv.status_code == 200
    estatistikak = rv.json()
    logging.info(estatistikak)
    assert estatistikak['total'] == 3
    assert len(estatistikak['docs']) == 3

def test_get_estatistikak_incorporations():
    rv = client.get('/estatistikak?stat=incorporations&year=2017&league=ACT')
    assert rv.status_code == 200
    estatistikak = rv.json()
    logging.info(estatistikak)
    assert estatistikak['total'] == 2
    assert len(estatistikak['docs']) == 2
