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
Import Flask Dependencies
"""
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from flask.ext.security import current_user
from flask.ext.security import login_required

from werkzeug.security import gen_salt


"""
Import Application Dependencies
"""
from CommonsCloudAPI.extensions import db
from CommonsCloudAPI.extensions import oauth


"""
Import Module Dependencies
"""
from . import module

from .models import Client
from .models import RequestToken
from .models import Nonce
from .models import AccessToken

from .utilities import *


"""
This endpoint creates the necessary client id and client_secret
necessary for secure OAuth2 authentication

To access this endpoint the user must be logged in to the system

"""
@module.route('/oauth/client')
@login_required
def oauth_client():

  next_url = url_for('oauth.oauth_client', **request.args)

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

  # @todo
  #
  # We need to turn this call to Client into a web form so that
  # our application is doing the call to this url .... which should
  # actually just be a utility function
  #
  item = Client(
    client_key=client_id,
    client_secret=client_secret,
    _redirect_uris='http://localhost:8000/authorized',
    user_id=this_user.id,
  )
  #
  # @end
  #
  
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


@module.route('/oauth/request_token')
@oauth.request_token_handler
def request_token():
    return {}


@module.route('/oauth/access_token')
@oauth.access_token_handler
def access_token():
    return {}


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
    client_key = kwargs.get('resource_owner_key')
    client = Client.query.filter_by(client_key=client_key).first()
    kwargs['client'] = client
    kwargs['user'] = this_user
    return render_template('oauth/authorize.html', **kwargs)

  confirm = request.form.get('confirm', 'no')

  return confirm == 'yes'

