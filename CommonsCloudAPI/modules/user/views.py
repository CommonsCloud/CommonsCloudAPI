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
from flask import current_app
from flask import jsonify
from flask import render_template
from flask import request

from flask.ext.security import current_user
from flask.ext.security import login_required

"""
Import CommonsCloudAPI Dependencies
"""
from CommonsCloudAPI.extensions import status

from CommonsCloudAPI.utilities.format_csv import CSV
from CommonsCloudAPI.utilities.format_json import JSON


"""
Import Module Dependencies
"""
from . import module


"""
Basic route for currently logged in user
"""
@module.route('/user/me', methods=['GET'])
def user_me():
  
  if not current_user.is_authenticated():
      return status.status_401(), 401

  """
  If the user is properly authenticated, then proceed to see if they
  have requests a type of content we serve
  """
  if request.headers['Content-Type'] == 'application/json' or ('format' in request.args and request.args['format'] == 'json'):    
    user_me = JSON(current_user)
    return user_me.create(), 200

  elif request.headers['Content-Type'] == 'text/csv' or ('format' in request.args and request.args['format'] == 'csv'):
    user_me = CSV(current_user)
    return user_me.create(), 200


  """
  If the user hasn't requested a specific content type then we should
  tell them that, by directing them to an "Unsupported Media Type"
  """
  return status.status_415(), 415




@module.route('/user/profile')
@login_required
def user_profile():
  return render_template('user/profile.html', user=current_user), 200

