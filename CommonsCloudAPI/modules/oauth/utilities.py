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
from CommonsCloudAPI import db
from CommonsCloudAPI import oauth2

from CommonsCloudAPI.models import Client
from CommonsCloudAPI.models import Grant
from CommonsCloudAPI.models import User


@oauth2.clientgetter
def load_client(client_id):
  return Client.query.filter_by(client_id=client_id).first()

@oauth2.clientgetter
def load_client(client_id):
    return Client.query.filter_by(client_id=client_id).first()


@oauth2.grantgetter
def load_grant(client_id, code):
    return Grant.query.filter_by(client_id=client_id, code=code).first()


@oauth2.grantsetter
def save_grant(client_id, code, request, *args, **kwargs):

    # decide the expires time yourself
    expires = datetime.utcnow() + timedelta(seconds=100)

    this_user = current_user

    grant = Grant(
        client_id=client_id,
        code=code['code'],
        redirect_uri=request.redirect_uri,
        _scopes=' '.join(request.scopes),
        user=this_user,
        expires=expires,
        user_id=this_user.id
    )

    db.session.add(grant)
    db.session.commit()

    return grant


@oauth2.tokengetter
def load_token(access_token=None, refresh_token=None):
    if access_token:
        return Token.query.filter_by(access_token=access_token).first()
    elif refresh_token:
        return Token.query.filter_by(refresh_token=refresh_token).first()


@oauth2.tokensetter
def save_token(token, request, *args, **kwargs):
    toks = Token.query.filter_by(
        client_id=request.client.client_id,
        user_id=request.user.id
    )
    # make sure that every client has only one token connected to a user
    for t in toks:
        db.session.delete(t)

    expires_in = token.pop('expires_in')
    expires = datetime.utcnow() + timedelta(seconds=expires_in)

    tok = Token(
        access_token=token['access_token'],
        refresh_token=token['refresh_token'],
        token_type=token['token_type'],
        _scopes=token['scope'],
        expires=expires,
        client_id=request.client.client_id,
        user_id=request.user.id,
    )
    db.session.add(tok)
    db.session.commit()
    return tok