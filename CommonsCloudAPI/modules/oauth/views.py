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
from flask import request
from flask import render_template

from flask.ext.security import current_user
from flask.ext.security import login_required

from werkzeug.security import gen_salt


"""
Import Application Dependencies
"""
from CommonsCloudAPI import db
from CommonsCloudAPI import oauth2

from CommonsCloudAPI.models import Client


"""
Import Module Dependencies
"""
from . import module
from .utilities import *


"""
This endpoint creates the necessary client id and client_secret
necessary for secure OAuth2 authentication

To access this endpoint the user must be logged in to the system

"""
@module.route('/oauth/client')
@login_required
def oauth_client():

  if not current_user:
    return redirect('/')

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
    client_id=client_id,
    client_secret=client_secret,
    _redirect_uris='http://127.0.0.1:5001/profile',
    _default_scopes='email',
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
    client_id=client_id,
    client_secret=client_secret,
  )


@module.route('/api/me')
@oauth2.require_oauth()
def me(req):
    return jsonify(username=req.user.username)

@module.route('/oauth/access_token')
@oauth2.token_handler
def oauth_access_token():
    return None


@module.route('/oauth/authorize', methods=['GET', 'POST'])
@oauth2.authorize_handler
def oauth_authorize(*args, **kwargs):

  if not current_user:
    return redirect('/')

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
  return confirm == 'yes'