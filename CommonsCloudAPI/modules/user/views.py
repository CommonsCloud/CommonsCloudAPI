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
from flask import render_template
from flask import request
from flask import jsonify

from flask.ext.security import current_user
from flask.ext.security import login_required

from CommonsCloudAPI.utilities.format_csv import CSV
from CommonsCloudAPI.utilities.format_json import JSON


"""
Import Module Dependencies
"""
from . import module


@module.route('/user/me', methods=['GET'])
def user_me():
   
  if not current_user.is_authenticated():
    error = {
      'error': '415 Unsupported Media Type',
      'status_code': '415',
      'message': 'The server does not support the media type transmitted in the request.'
    }
    return jsonify(error), 415

  if request.headers['Content-Type'] == 'application/json' or ('format' in request.args and request.args['format'] == 'json'):
    
    user_me = JSON()
    user_me.the_content = current_user
    return user_me.create(), 200

  elif request.headers['Content-Type'] == 'text/csv' or ('format' in request.args and request.args['format'] == 'csv'):
    
    user_me = CSV(current_user)
    return user_me.create(), 200




@module.route('/user/profile')
@login_required
def user_profile():
  return render_template('user/profile.html', user=current_user), 200