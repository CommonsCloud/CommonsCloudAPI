from flask import Flask, url_for, session, request, jsonify, redirect
from flask_oauthlib.client import OAuth


CLIENT_ID = '0A7Fs4a9AKO0Rqa0dc2FIpHH9s1NWnn6O1PQSvDw'
CLIENT_SECRET = 'jimsP5dLi25h4YM17Ra2U7jEowSVMvxaOViFPxoVKegUagMKmP'


app = Flask(__name__)
app.debug = True
app.secret_key = 'secret'
oauth = OAuth(app)

remote = oauth.remote_app(
    'remote',
    consumer_key=CLIENT_ID,
    consumer_secret=CLIENT_SECRET,
    request_token_params={'scope': 'email'},
    base_url='http://127.0.0.1:5000/v2/',
    request_token_url=None,
    access_token_url='http://127.0.0.1:5000/oauth/token',
    authorize_url='http://127.0.0.1:5000/oauth/authorize'
)


@app.route('/')
def index():

    if 'remote_oauth' in session:
        resp = remote.get('applications.json')
        if resp.status != 403:
            return jsonify(resp.data)

        del session['remote_oauth']

    next_url = request.args.get('next') or request.referrer or None
    return remote.authorize(
        callback=url_for('authorized', next=next_url, _external=True)
    )


@app.route('/authorized')
@remote.authorized_handler
def authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    print "resp['access_token']", resp['access_token']
    session['remote_oauth'] = (resp['access_token'], '')
    return redirect('/')


@remote.tokengetter
def get_oauth_token():
    return session.get('remote_oauth')


if __name__ == '__main__':
    import os
    os.environ['DEBUG'] = 'true'
    app.run(host='localhost', port=8000)
