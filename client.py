from requests_oauthlib import OAuth2Session
from flask import Flask, request, redirect, session, url_for
from flask.json import jsonify
import os

app = Flask(__name__)


# This information is obtained upon registration of a new commonscloudapi OAuth
# application here: https://commonscloudapi.com/settings/applications/new
client_id = "nlrgTOQ8nNFvzjtD1ReOsvhtOzgdR46ffLY2SNJU"
client_secret = "VEZjomZxGrOmDMgBndFnpl4P4mrn4yPnsdCaBuT26dEeNxvbhf"
authorization_base_url = 'http://127.0.0.1:5000/oauth/authorize'
token_url = 'http://127.0.0.1:5000/oauth/access_token'


@app.route("/")
def demo():
    """Step 1: User Authorization.

    Redirect the user/resource owner to the OAuth provider (i.e. commonscloudapi)
    using an URL with a few key OAuth parameters.
    """
    commonscloudapi = OAuth2Session(client_id)
    authorization_url, state = commonscloudapi.authorization_url(authorization_base_url)

    # State is used to prevent CSRF, keep this for later.
    session['oauth_state'] = state
    return redirect(authorization_url)


# Step 2: User authorization, this happens on the provider.

@app.route("/callback", methods=["GET"])
def callback():
    """ Step 3: Retrieving an access token.

    The user has been redirected back from the provider to your registered
    callback URL. With this redirection comes an authorization code included
    in the redirect URL. We will use that to obtain an access token.
    """

    commonscloudapi = OAuth2Session(client_id, state=session['oauth_state'])
    token = commonscloudapi.fetch_token(token_url, client_secret=client_secret,
                               authorization_response=request.url)

    # At this point you can fetch protected resources but lets save
    # the token and show how this is done from a persisted token
    # in /profile.
    session['oauth_token'] = token

    return redirect(url_for('.profile'))


@app.route("/profile", methods=["GET"])
def profile():
    """Fetching a protected resource using an OAuth 2 token.
    """
    commonscloudapi = OAuth2Session(client_id, token=session['oauth_token'])
    return jsonify(commonscloudapi.get('http://127.0.0.1:5000/user/profile').json())


if __name__ == "__main__":
    # This allows us to use a plain HTTP callback
    os.environ['DEBUG'] = "1"

    app.secret_key = os.urandom(24)
    app.run(debug=True, port=5001)