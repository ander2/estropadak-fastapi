import logging
import pytest

from fastapi.testclient import TestClient
from app.main import api as app


client = TestClient(app)


@pytest.fixture()
def clean_up(credentials):
    yield
    rv = client.post('/auth', json=credentials)
    doc_ids = (
        "rank_ACT_2122",
    )
    token = rv.json()['access_token']
    for doc_id in doc_ids:
        try:
            client.delete(f'/sailkapenak/{doc_id}', headers=[('Authorization', f'Bearer {token}')])
        except Exception:
            pass


def test_sailkapena_with_lowercase_league():
    rv = client.get('/sailkapenak?league=act&year=2017')
    assert rv.status_code == 400
    # sailkapena = rv.json()['data']
    # assert sailkapena['total'] == 1
    # assert len(sailkapena['docs'][0]['stats']) == 12


def test_sailkapena_with_uppercase_league():
    rv = client.get('/sailkapenak?league=ACT&year=2017')
    assert rv.status_code == 200
    sailkapena = rv.json()
    assert sailkapena['total'] == 1
    assert len(sailkapena['docs'][0]['stats']) == 12


def test_sailkapena_for_team():
    rv = client.get('/sailkapenak?league=ACT&year=2017&team=Orio')
    assert rv.status_code == 200
    sailkapena = rv.json()
    keys = ['wins', 'positions', 'position', 'points', 'best', 'worst',
            'cumulative', 'age', 'rowers']
    assert sailkapena['total'] == 1
    team_is_there = False
    for stat in sailkapena['docs'][0]['stats']:
        if stat['name'] == 'Orio':
            team_is_there = True
            assert all(izenburua in keys for izenburua in stat['value'].keys())
    assert team_is_there


def test_sailkapena_for_multiple_teams():
    rv = client.get('/sailkapenak?league=ARC1&teams=Arkote&teams=Astillero')
    assert rv.status_code == 200
    sailkapena = rv.json()
    keys = ['wins', 'positions', 'position', 'points', 'best', 'worst',
            'cumulative', 'age', 'rowers']
    assert sailkapena['total'] == 9
    team_are_there = False
    for stat in sailkapena['docs'][0]['stats']:
        if stat['name'] == 'Arkote' or stat['name'] == 'Astillero':
            team_are_there = True
            assert all(izenburua in keys for izenburua in stat['value'].keys())
        assert team_are_there
        team_are_there = False


def test_sailkapena_for_team_that_not_exists():
    rv = client.get('/sailkapenak?league=ACT&teams=Oria')
    assert rv.status_code == 200
    assert rv.json()['total'] == 0
    assert rv.json()['docs'] == []


def testSailkapenaForTeamWithYearThatNotExists():
    rv = client.get('/sailkapenak?league=act&year=1900&teams=Orio')
    assert rv.status_code == 400


def test_sailkapena_creation_without_credentials():
    rv = client.post('/sailkapenak', json={
        "league": "ACT",
        "year": 2022,
        "stats": []
    })
    assert rv.status_code == 401


def test_sailkapena_creation_with_credentials(credentials, clean_up):
    rv = client.post('/auth', json=credentials)
    token = rv.json()['access_token']
    rv = client.post('/sailkapenak', json={
        "league": "ACT",
        "year": 2122,
        "stats": []
    }, headers=[('Authorization', f'Bearer {token}')])
    assert rv.status_code == 201


def test_get_sailkapena_for_id():
    rv = client.get('/sailkapenak/rank_ACT_2019')
    assert rv.status_code == 200
    sailkapena = rv.json()
    assert sailkapena['id'] == 'rank_ACT_2019'
    assert sailkapena['year'] == 2019
    assert sailkapena['league'] == 'ACT'
    assert len(sailkapena['stats']) == 12


def test_put_sailkapena_for_id_without_credentials():
    rv = client.get('/sailkapenak/rank_ACT_2019')
    sailkapena = rv.json()
    rv = client.put('/sailkapenak/rank_ACT_2019', json=sailkapena)
    assert rv.status_code == 401


def test_put_sailkapena_for_id_with_credentials(credentials):
    rv = client.get('/sailkapenak/rank_ACT_2019')
    sailkapena = rv.json()
    sailkapena['stats'].append({
        'name': 'fantomas',
        'value': {
            'best': 1,
            'worst': 2,
            'wins': 1,
            'points': 23,
            'position': 2,
            'positions': [1, 2],
            'cumulative': [12, 23],
        }
    })
    rv = client.post('/auth', json=credentials)
    token = rv.json()['access_token']
    rv = client.put(
        '/sailkapenak/rank_ACT_2019',
        json=sailkapena,
        headers=[('Authorization', f'Bearer {token}')])
    assert rv.status_code == 200
    rv = client.get('/sailkapenak/rank_ACT_2019')
    sailkapena = rv.json()
    assert len(rv.json()['stats']) == 13
    fantomas_stats = sailkapena['stats'][12]
    assert fantomas_stats['value']['best'] == 1
    assert fantomas_stats['value']['worst'] == 2
    assert fantomas_stats['value']['points'] == 23
    assert fantomas_stats['value']['position'] == 2
    assert fantomas_stats['value']['positions'] == [1, 2]
    assert fantomas_stats['value']['cumulative'] == [12, 23]
    sailkapena['stats'] = sailkapena['stats'][0:12]
    rv = client.put(
        '/sailkapenak/rank_ACT_2019',
        json=sailkapena,
        headers=[('Authorization', f'Bearer {token}')])
    assert rv.status_code == 200


def test_delete_sailkapena_for_id_without_credentials():
    rv = client.delete('/sailkapenak/rank_ACT_2019')
    assert rv.status_code == 401


def test_delete_sailkapena_for_id_with_credentials(credentials):
    sailkapena = {
        'league': 'ACT',
        'year': 2100,
        'stats': []
    }
    rv = client.post('/auth', json=credentials)
    token = rv.json()['access_token']
    rv = client.post(
        '/sailkapenak',
        json=sailkapena,
        headers=[('Authorization', f'Bearer {token}')])
    assert rv.status_code == 201
    logging.info(rv.json())
    rv = client.delete(
        '/sailkapenak/rank_ACT_2100',
        headers=[('Authorization', f'Bearer {token}')])
    assert rv.status_code == 204
