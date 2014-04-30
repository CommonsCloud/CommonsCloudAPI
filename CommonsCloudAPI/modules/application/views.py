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

from flask.ext.security import current_user


"""
Import Application Module Dependencies
"""
from CommonsCloudAPI.extensions import oauth
from CommonsCloudAPI.extensions import status as status_

from CommonsCloudAPI.models.application import Application

from . import module

from .permissions import permission_required


@module.route('/v2/applications.<string:extension>', methods=['OPTIONS'])
def application_preflight(extension):

  return status_.status_200(), 200


@module.route('/v2/applications/<int:application_id>.<string:extension>', methods=['OPTIONS'])
def application_single_preflight(application_id, extension):

  return status_.status_200(), 200


@module.route('/v2/applications.<string:extension>', methods=['GET'])
@oauth.require_oauth('applications')
def application_list(oauth_request, extension):

  Application_ = Application()
  Application_.current_user = oauth_request.user

  applications_ = Application_.application_list()

  arguments = {
    'the_content': applications_,
    'list_name': 'applications',
    'extension': extension
  }

  return Application_.endpoint_response(**arguments)


@module.route('/v2/applications/<int:application_id>.<string:extension>', methods=['GET'])
@oauth.require_oauth('applications')
def application_get(oauth_request, application_id, extension):

  Application_ = Application()
  Application_.current_user = oauth_request.user

  this_application = Application_.application_get(application_id)

  if type(this_application) is 'Response':
    return this_application, this_application.code

  arguments = {
    'the_content': this_application,
    'extension': extension
  }

  return Application_.endpoint_response(**arguments)


@module.route('/v2/applications.<string:extension>', methods=['POST'])
@oauth.require_oauth('applications')
def application_post(oauth_request, extension):

  Application_ = Application()
  Application_.current_user = oauth_request.user

  new_application = Application_.application_create(request)

  arguments = {
    'the_content': new_application,
    'extension': extension,
    'code': 201
  }

  return Application_.endpoint_response(**arguments)


@module.route('/v2/applications/<int:application_id>.<string:extension>', methods=['PUT', 'PATCH'])
@oauth.require_oauth('applications')
def application_update(oauth_request, application_id, extension):

  Application_ = Application()
  Application_.current_user = oauth_request.user

  updated_application = Application_.application_update(application_id, request)

  arguments = {
    'the_content': updated_application,
    'extension': extension
  }

  return Application_.endpoint_response(**arguments)


@module.route('/v2/applications/<int:application_id>.<string:extension>', methods=['DELETE'])
@oauth.require_oauth('applications')
def application_delete(oauth_request, application_id, extension):

  Application_ = Application()
  Application_.current_user = oauth_request.user

  Application_.application_delete(application_id)

  return status_.status_204(), 204

