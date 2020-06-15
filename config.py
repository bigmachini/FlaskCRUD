import configparser
import logging.config
import logging
import os

config_parser = configparser.ConfigParser()
_config_file = os.path.abspath(os.path.join(os.path.dirname(__file__), ".", "logging.ini"))

d = config_parser.read(_config_file)

logging.config.fileConfig(_config_file)

_logger = logging.getLogger(__name__)


def access_secret_version():
    """
    Access the payload for the given secret version if one exists. The version
    can be a version number as a string (e.g. "5") or an alias (e.g. "latest").
    """

    # Import the Secret Manager client library.
    from google.cloud import secretmanager
    project_id = os.environ.get('PROJECT_ID')
    secret_id = os.environ.get('SECRET_ID')
    version_id = os.environ.get('SECRET_VERSION')
    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version.
    name = client.secret_version_path(project_id, secret_id, version_id)

    # Access the secret version.
    response = client.access_secret_version(name)

    # Print the secret payload.
    #
    # WARNING: Do not print the secret in a production environment - this
    # snippet is showing how to access the secret material.
    payload = response.payload.data.decode('UTF-8')
    return json.loads(payload)


def access_token_version():
    """
    Access the payload for the given secret version if one exists. The version
    can be a version number as a string (e.g. "5") or an alias (e.g. "latest").
    """

    # Import the Secret Manager client library.
    from google.cloud import secretmanager
    project_id = os.environ.get('PROJECT_ID')
    secret_id = os.environ.get('TOKEN_ID')
    version_id = os.environ.get('TOKEN_VERSION')
    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version.
    name = client.secret_version_path(project_id, secret_id, version_id)

    # Access the secret version.
    response = client.access_secret_version(name)

    # Print the secret payload.
    #
    # WARNING: Do not print the secret in a production environment - this
    # snippet is showing how to access the secret material.
    payload = response.payload.data.decode('UTF-8')
    return json.loads(payload)


import time
import jwt
import json
import requests
import urllib


def get_id_token(credentials_json, run_service_url):
    # Load service account credentials to dictionary

    # Create and return a signed JWT token to the designated service endpoint
    def create_signed_jwt():
        iat = time.time()
        exp = iat + 3600
        payload = {
            'iss': credentials_json['client_email'],
            'sub': credentials_json['client_email'],
            'target_audience': run_service_url,
            'aud': 'https://www.googleapis.com/oauth2/v4/token',
            'iat': iat,
            'exp': exp
        }
        additional_headers = {
            'kid': credentials_json['private_key_id']
        }
        signed_jwt = jwt.encode(
            payload,
            credentials_json['private_key'],
            headers=additional_headers,
            algorithm='RS256'
        )
        return signed_jwt

    # Exchange JWT token for a google-signed OIDC token
    def exchange_jwt_for_token(signed_jwt):
        body = {
            'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
            'assertion': signed_jwt
        }
        token_request = requests.post(
            url='https://www.googleapis.com/oauth2/v4/token',
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data=urllib.parse.urlencode(body)
        )
        return token_request.json()['id_token']

    # Main
    return exchange_jwt_for_token(create_signed_jwt())
