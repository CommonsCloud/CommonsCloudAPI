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


from CommonsCloudAPI.extensions import status as status_

from CommonsCloudAPI.utilities.format_csv import CSV
from CommonsCloudAPI.utilities.format_json import JSON


"""
Import Application Module Dependencies
"""
from . import module

from .models import Application
from .permissions import check_permissions


@module.route('/application/', methods=['GET'])
def application_list():

  if not current_user.is_authenticated():
    return status_.status_401(), 401

  applications_ = Application().application_list()

  """
  If the user is properly authenticated, then proceed to see if they
  have requests a type of content we serve
  """
  if request.headers['Content-Type'] == 'application/json' or ('format' in request.args and request.args['format'] == 'json'):    
    this_data = JSON(applications_, serialize=True, list_name='applications')
    return this_data.create(), 200

  elif request.headers['Content-Type'] == 'text/csv' or ('format' in request.args and request.args['format'] == 'csv'):
    this_data = CSV(applications_, serialize=True)
    return this_data.create(), 200

  """
  If the user hasn't requested a specific content type then we should
  tell them that, by directing them to an "Unsupported Media Type"
  """
  return status_.status_415(), 415


@module.route('/application/', methods=['POST'])
@login_required
def application_post():

  print request.data
  return jsonify({'response': request.data}), 200

  # if not current_user.is_authenticated():
  #   return status_.status_401(), 401

  # Application_ = Application()
  # new_application = Application_.application_create(request.form)

  # return redirect(url_for('application.application_get', application_id=new_application.id))


@module.route('/application/<int:application_id>/', methods=['GET'])
@login_required
def application_get(application_id):

  permission = check_permissions(application_id)

  if not permission.get('can_view', True):
    return status_.status_401(), 401

  this_application = Application().application_get(application_id)

  """
  If the user is properly authenticated, then proceed to see if they
  have requests a type of content we serve
  """
  if request.headers['Content-Type'] == 'application/json' or ('format' in request.args and request.args['format'] == 'json'):    
    this_data = JSON(this_application, serialize=True)
    return this_data.create(), 200

  elif request.headers['Content-Type'] == 'text/csv' or ('format' in request.args and request.args['format'] == 'csv'):
    this_data = CSV(this_application, serialize=True)
    return this_data.create(), 200

  """
  If the user hasn't requested a specific content type then we should
  tell them that, by directing them to an "Unsupported Media Type"
  """
  return status_.status_415(), 415

