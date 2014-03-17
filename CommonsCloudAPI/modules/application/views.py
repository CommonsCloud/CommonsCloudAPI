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
from flask import request


"""
Import Application Module Dependencies
"""
from CommonsCloudAPI.extensions import oauth
from CommonsCloudAPI.extensions import status as status_

from CommonsCloudAPI.models.application import Application

from . import module

from .permissions import permission_required


@module.route('/v2/applications.<string:extension>', methods=['GET'])
# @oauth.require_oauth()
def application_list(extension):

  Application_ = Application()

  applications_ = Application_.application_list()

  arguments = {
    'the_content': applications_,
    'list_name': 'applications',
    'extension': extension
  }

  return Application_.endpoint_response(**arguments)


@module.route('/v2/applications.<string:extension>', methods=['POST'])
# @oauth.require_oauth()
def application_post(extension):

  Application_ = Application()
  new_application = Application_.application_create(request)

  arguments = {
    'the_content': new_application,
    'extension': extension,
    'code': 201
  }

  return Application_.endpoint_response(**arguments)


@module.route('/v2/applications/<int:application_id>.<string:extension>', methods=['GET'])
# @oauth.require_oauth()
@permission_required('can_view')
def application_get(application_id, extension):

  Application_ = Application()
  this_application = Application_.application_get(application_id)

  if type(this_application) is 'Response':
    return this_application, this_application.code

  arguments = {
    'the_content': this_application,
    'extension': extension
  }

  return Application_.endpoint_response(**arguments)


@module.route('/v2/applications/<int:application_id>.<string:extension>', methods=['PUT', 'PATCH'])
# @oauth.require_oauth()
@permission_required('can_edit')
def application_update(application_id, extension):

  Application_ = Application()
  updated_application = Application_.application_update(application_id, request)

  arguments = {
    'the_content': updated_application,
    'extension': extension
  }

  return Application_.endpoint_response(**arguments)


@module.route('/v2/applications/<int:application_id>.<string:extension>', methods=['DELETE'])
# @oauth.require_oauth()
@permission_required('can_delete')
def application_delete(application_id, extension):

  Application().application_delete(application_id)

  return status_.status_204(), 204

