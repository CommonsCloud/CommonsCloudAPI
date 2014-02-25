# coding: utf-8

import os

from flask import Flask, session, url_for, request, jsonify
from flask_oauthlib.client import OAuth


app = Flask(__name__)
app.debug = True
app.secret_key = 'secret'

# TODO: fill them
CLIENT_KEY = 'PdXWzvHM7YRY5SSVF2U6e0ETMxUdsjoaVpSNil1t'
CLIENT_SECRET = 'BRfQaHWJjk3ab1bItH3Kpq0xz0SsP6d3DuIOHf2WD5JQCPufzb'

oauth = OAuth(app)
remote = oauth.remote_app(
    'remote',
    consumer_key=CLIENT_KEY,
    consumer_secret=CLIENT_SECRET,
    base_url='http://127.0.0.1:5000/',
    request_token_url='http://127.0.0.1:5000/oauth/request_token',
    access_token_method='GET',
    access_token_url='http://127.0.0.1:5000/oauth/access_token',
    authorize_url='http://127.0.0.1:5000/oauth/authorize',
)


@app.route('/')
def home():
    if 'example_oauth' in session:
        resp = remote.get('application/')
        return jsonify({"status":"success", "data": resp.data})
    return remote.authorize(callback=url_for('authorized', _external=False))


@app.route('/authorized')
@remote.authorized_handler
def authorized(resp):
    if resp is None:
        return 'Access denied: error=%s' % (
            request.args['error']
        )
    if 'oauth_token' in resp:
        session['example_oauth'] = resp
        print 'oauth_token'
        return jsonify(resp)
    return str(resp)


@remote.tokengetter
def example_oauth_token():
    if 'example_oauth' in session:
        resp = session['example_oauth']
        return resp['oauth_token'], resp['oauth_token_secret']


import logging
logger = logging.getLogger('flask_oauthlib')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


if __name__ == '__main__':

    os.environ['DEBUG'] = "1"

    app.run(host='localhost', port=8000)
