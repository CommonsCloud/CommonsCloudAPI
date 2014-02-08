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

from flask.ext.security import current_user
from flask.ext.security import login_required

from werkzeug.security import gen_salt


"""
Import Application Dependencies
"""
from CommonsCloudAPI import db

from CommonsCloudAPI.models import Client


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
    _redirect_uris='http://localhost:8000/authorized',
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

