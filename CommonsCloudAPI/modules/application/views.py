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
from flask import request
from flask import url_for

from flask.ext.security import current_user


from CommonsCloudAPI.extensions import oauth
from CommonsCloudAPI.extensions import status as status_


"""
Import Application Module Dependencies
"""
from . import module

from .models import Application

from .permissions import check_permissions
from .permissions import permission_required

from .utilities import application_response


@module.route('/application/', methods=['GET'])
# @oauth.require_oauth()
def application_list():

  Application_ = Application()

  applications_ = Application_.application_list()

  arguments = {
    'the_content': applications_,
    'list_name': 'applications'
  }

  return Application_.application_response(**arguments)

"""
CREATE

Everyone that has a user account can add new applications, however
in the future we should figure out what the repercussions of that are.
"""
@module.route('/application/', methods=['POST'])
# @oauth.require_oauth()
def application_post():

  Application_ = Application()
  new_application = Application_.application_create(request)

  return Application_.application_response(new_application)


"""
GET/VIEW

User attempting to access this endpoint must have the `view`
permission associated with them in the `user_applications` table
"""
@module.route('/application/<int:application_id>/', methods=['GET'])
# @oauth.require_oauth()
@permission_required('can_view')
def application_get(application_id):

  Application_ = Application()
  this_application = Application_.application_get(application_id)

  return Application_.application_response(this_application)


"""
PUT/PATCH

User attempting to access this endpoint must have the `edit`
permission associated with them in the `user_applications` table
"""
@module.route('/application/<int:application_id>/', methods=['PUT', 'PATCH'])
# @oauth.require_oauth()
@permission_required('can_edit')
def application_update(application_id):

  Application_ = Application()
  updated_application = Application_.application_update(application_id, request)

  return Application_.application_response(updated_application)


"""
DELETE

User attempting to access this endpoint must have the `delete`
permission associated with them in the `user_applications` table
"""
@module.route('/application/<int:application_id>/', methods=['DELETE'])
# @oauth.require_oauth()
@permission_required('can_delete')
def application_delete(application_id):

  Application().application_delete(application_id)

  return status_.status_204(), 204

