import contextlib
from ibmcloudant.cloudant_v1 import CloudantV1
from ibm_cloud_sdk_core.authenticators import BasicAuthenticator

from app.config import config


@contextlib.contextmanager
def get_db_connection():
    authenticator = BasicAuthenticator(config['DBUSER'], config['DBPASS'])
    service = CloudantV1(authenticator=authenticator)
    service.set_service_url(config['COUCHDB'])

    try:
        yield service
    finally:
        pass
