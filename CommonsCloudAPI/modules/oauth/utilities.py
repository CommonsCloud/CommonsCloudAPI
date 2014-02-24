"""
For CommonsCloud copyright information please see the LICENSE document
(the "License") included with this software package. This file may not
be used in any manner except in compliance with the License

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


"""
Import System Dependencies
"""
from datetime import datetime, timedelta


"""
Import Flask Dependencies
"""
from flask.ext.security import current_user


"""
Import Application Dependencies
"""
from CommonsCloudAPI.extensions import db
from CommonsCloudAPI.extensions import oauth

from .models import Client
from .models import RequestToken
from .models import Nonce
from .models import AccessToken


@oauth.clientgetter
def load_client(client_key):
    return Client.query.get(client_key)


@oauth.grantgetter
def load_request_token(token):
    return RequestToken.query.filter_by(token=token).first()


@oauth.grantsetter
def save_request_token(token, request):
    if hasattr(oauth, 'realms') and oauth.realms:
        realms = ' '.join(request.realms)
    else:
        realms = None
    grant = RequestToken(
        token=token['oauth_token'],
        secret=token['oauth_token_secret'],
        client=request.client,
        redirect_uri=request.redirect_uri,
        _realms=realms,
    )
    db.session.add(grant)
    db.session.commit()
    return grant


@oauth.verifiergetter
def load_verifier(verifier, token):
    return RequestToken.query.filter_by(
        verifier=verifier, token=token
    ).first()


@oauth.verifiersetter
def save_verifier(token, verifier, *args, **kwargs):
    tok = RequestToken.query.filter_by(token=token).first()
    tok.verifier = verifier['oauth_verifier']
    tok.user = current_user
    db.session.add(tok)
    db.session.commit()
    return tok


@oauth.noncegetter
def load_nonce(client_key, timestamp, nonce, request_token, access_token):
    return Nonce.query.filter_by(
        client_key=client_key, timestamp=timestamp, nonce=nonce,
        request_token=request_token, access_token=access_token,
    ).first()


@oauth.noncesetter
def save_nonce(client_key, timestamp, nonce, request_token, access_token):
    nonce = Nonce(
        client_key=client_key,
        timestamp=timestamp,
        nonce=nonce,
        request_token=request_token,
        access_token=access_token,
    )
    db.session.add(nonce)
    db.session.commit()
    return nonce


@oauth.tokengetter
def load_access_token(client_key, token, *args, **kwargs):
    return AccessToken.query.filter_by(
        client_key=client_key, token=token
    ).first()


@oauth.tokensetter
def save_access_token(token, request):
    tok = AccessToken(
        client=request.client,
        user=request.user,
        token=token['oauth_token'],
        secret=token['oauth_token_secret'],
        _realms=token['oauth_authorized_realms'],
    )
    db.session.add(tok)
    db.session.commit()
