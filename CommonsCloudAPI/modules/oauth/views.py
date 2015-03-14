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
from flask import jsonify
from flask import url_for
from flask import redirect
from flask import render_template
from flask import request

from werkzeug.security import gen_salt

from flask.ext.security import current_user
from flask.ext.security import login_required

from flask.ext.oauthlib.provider import OAuth2RequestValidator


"""
Import Application Dependencies
"""
from CommonsCloudAPI.extensions import db
from CommonsCloudAPI.extensions import logger
from CommonsCloudAPI.extensions import oauth


"""
Import Module Dependencies
"""
from . import module


"""
This endpoint creates the necessary client id and client_secret
necessary for secure OAuth2 authentication

To access this endpoint the user must be logged in to the system

"""
@module.route('/oauth/client')
@login_required
def oauth_client():

  next_url = url_for('oauth.oauth_client', **request.args)

  """
  If the user is not authenticated we should redirect them
  to the login page
  """
  if not hasattr(current_user, 'id'):
    return redirect(url_for('security.login', next=next_url))

  """
  Assign the current_user object to a variable so that we don't
  accidently alter the object during this process.
  """
  this_user = current_user

  """
  Generate a client_id and client_secret for our OAuth2 authentication
  """
  client_id = gen_salt(40)
  client_secret = gen_salt(50)
  _redirect_uris = ''
  _default_scopes = ''
  user_id = this_user.id

  # @todo
  #
  # We need to turn this call to Client into a web form so that
  # our application is doing the call to this url .... which should
  # actually just be a utility function
  #
  # item = Client(
  #   client_id=client_id,
  #   client_secret=client_secret,
  #   _redirect_uris='http://localhost:9000/authorized',
  #   _default_scopes='user,applications',
  #   user_id=this_user.id,
  # )
  #
  # @end
  #
  
  item = Client(
    client_id = client_id,
    client_secret = client_secret,
    _redirect_uris = _redirect_uris,
    _default_scopes = _default_scopes,
    user_id = user_id,
  )
  
  """
  Save the OAuth2 authentication information to the database
  """
  db.session.add(item)
  db.session.commit()

  """
  Return the client id and secret as a JSON object ... Why? Do we need to?
  """
  return jsonify(
    client_key=client_id,
    client_secret=client_secret,
  ), 200


@module.route('/oauth/token')
@oauth.token_handler
def access_token():
    return None

@module.route('/oauth/authorize', methods=['GET', 'POST'])
@oauth.authorize_handler
def authorize(*args, **kwargs):

  next_url = url_for('oauth.authorize', **request.args)

  if not hasattr(current_user, 'id'):
    return redirect(url_for('security.login', next=next_url))

  """
  Assign the current_user object to a variable so that we don't
  accidently alter the object during this process.
  """
  this_user = current_user

  if request.method == 'GET':

    client_id = kwargs.get('client_id')
    client = Client.query.filter_by(client_id=client_id).first()
    kwargs['client'] = client
    kwargs['user'] = this_user
    return render_template('oauth/authorize.html', **kwargs)

  confirm = request.form.get('confirm', 'no')
  return confirm == 'Allow Access'

@oauth.clientgetter
def load_client(client_id):
    return Client.query.filter_by(client_id=client_id).first()


@oauth.grantgetter
def load_grant(client_id, code):
    return Grant.query.filter_by(client_id=client_id, code=code).first()


@oauth.grantsetter
def save_grant(client_id, code, request, *args, **kwargs):
    # decide the expires time yourself
    expires = datetime.utcnow() + timedelta(days=1)
    grant = Grant(
        client_id=client_id,
        code=code['code'],
        redirect_uri=request.redirect_uri,
        _scopes=' '.join(request.scopes),
        user=current_user,
        expires=expires
    )
    db.session.add(grant)
    db.session.commit()
    return grant


@oauth.tokengetter
def load_token(access_token=None, refresh_token=None):
    if access_token:
        return Token.query.filter_by(access_token=access_token).first()
    elif refresh_token:
        return Token.query.filter_by(refresh_token=refresh_token).first()


@oauth.tokensetter
def save_token(token, oauth_request, *args, **kwargs):

    toks = Token.query.filter_by(
        client_id=oauth_request.client.client_id,
        user_id=current_user.id
    )

    # make sure that every client has only one token connected to a user
    for t in toks:
        db.session.delete(t)

    expires = datetime.utcnow() + timedelta(days=1)

    tok = Token(
        access_token=token['access_token'],
        # refresh_token=token['refresh_token'],
        token_type=token['token_type'],
        _scopes=token['scope'],
        expires=expires,
        client_id=oauth_request.client.client_id,
        user_id=current_user.id,
    )
    db.session.add(tok)
    db.session.commit()
    return tok
