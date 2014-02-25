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
import requests

from flask import redirect
from flask import request
from flask import url_for

from flask.ext.security import current_user


from CommonsCloudAPI.extensions import oauth
from CommonsCloudAPI.extensions import status as status_

from CommonsCloudAPI.utilities.format_csv import CSV
from CommonsCloudAPI.utilities.format_json import JSON


"""
Import Application Module Dependencies
"""
from . import module

from .models import Application
from .permissions import check_permissions
from .permissions import permission_required


@module.route('/application/', methods=['GET'])
@oauth.require_oauth()
def application_list():

  applications_ = Application().application_list()

  """
  If the user is properly authenticated, then proceed to see if they
  have requests a type of content we serve
  """
  if request.headers['Content-Type'] == 'application/json' or \
      (hasattr(request.args, 'format') and request.args['format'] == 'json'):

    this_data = JSON(applications_, serialize=True, list_name='applications')
    return this_data.create(), 200

  elif request.headers['Content-Type'] == 'text/csv' or \
      (hasattr(request.args, 'format') and request.args['format'] == 'csv'):

    this_data = CSV(applications_, serialize=True)
    return this_data.create(), 200

  """
  If the user hasn't requested a specific content type then we should
  tell them that, by directing them to an "Unsupported Media Type"
  """
  return status_.status_415(), 415


"""
CREATE

Everyone that has a user account can add new applications, however
in the future we should figure out what the repercussions of that are.
"""
@module.route('/application/', methods=['POST'])
@oauth.require_oauth()
def application_post():

  Application_ = Application()
  new_application = Application_.application_create(request)

  url_arguments = {
    'application_id': new_application.id,
    'format': 'json',
    '_external': True
  }

  return redirect(url_for('application.application_get', **url_arguments)), 201


"""
GET/VIEW

User attempting to access this endpoint must have the `view`
permission associated with them in the `user_applications` table
"""
@module.route('/application/<int:application_id>/', methods=['GET'])
@oauth.require_oauth()
@permission_required('can_view')
def application_get(application_id):

  this_application = Application().application_get(application_id)

  """
  If the user is properly authenticated, then proceed to see if they
  have requests a type of content we serve
  """
  if request.headers['Content-Type'] == 'application/json' or \
      (hasattr(request.args, 'format') and request.args['format'] == 'json'):

    this_data = JSON(this_application, serialize=True)
    return this_data.create(), 200

  elif request.headers['Content-Type'] == 'text/csv' or \
      (hasattr(request.args, 'format') and request.args['format'] == 'csv'):

    this_data = CSV(this_application, serialize=True)
    return this_data.create(), 200

  """
  If the user hasn't requested a specific content type then we should
  tell them that, by directing them to an "Unsupported Media Type"
  """
  return status_.status_415(), 415


"""
PUT/PATCH

User attempting to access this endpoint must have the `edit`
permission associated with them in the `user_applications` table
"""
@module.route('/application/<int:application_id>/', methods=['PUT', 'PATCH'])
@oauth.require_oauth()
@permission_required('can_edit')
def application_update(application_id):

  Application_ = Application()
  new_application = Application_.application_update(application_id, request)

  url_arguments = {
    'application_id': new_application.id,
    'format': 'json',
    '_external': True
  }

  return redirect(url_for('application.application_get', **url_arguments)), 200


"""
DELETE

User attempting to access this endpoint must have the `delete`
permission associated with them in the `user_applications` table
"""
@module.route('/application/<int:application_id>/', methods=['DELETE'])
@oauth.require_oauth()
@permission_required('can_delete')
def application_delete(application_id):

  Application_ = Application()
  new_application = Application_.application_delete(application_id)

  return status_.status_204(), 204


