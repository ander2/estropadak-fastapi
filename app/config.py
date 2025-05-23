import os
import logging

config = {
    'COUCHDB': 'http://couchdb:5984',
    'DBNAME': 'estropadak',
    'DBUSER': 'admin',
    'DBPASS': '',
    'COUCHDB_HOST': 'couchdb3',
    'COUCHDB_PORT': 5984
}

if 'COUCHDB' in os.environ:
    config['COUCHDB'] = os.environ['COUCHDB']

if 'DBNAME' in os.environ:
    config['DBNAME'] = os.environ['DBNAME']

if 'DBUSER' in os.environ:
    config['DBUSER'] = os.environ['DBUSER']

if 'DBPASS' in os.environ:
    config['DBPASS'] = os.environ['DBPASS']

if 'COUCHDB_HOST' in os.environ:
    config['COUCHDB_HOST'] = os.environ['COUCHDB_HOST']

if 'COUCHDB_PORT' in os.environ:
    config['COUCHDB_PORT'] = os.environ['COUCHDB_PORT']


JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', '')
MIN_YEAR = 2002
CATEGORIES = ['IG', 'IN', 'PG', 'PN', 'JG', 'JN', 'SG', 'SN']
PAGE_SIZE = 50

DEFAULT_LOGGER = 'estropadak'
LOG_LEVEL = os.environ.get('LOG_LEVEL', logging.INFO)

LOG_FORMAT = '%(levelname)-9s %(asctime)s %(module)s %(filename)-8s %(message)s'
logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL)