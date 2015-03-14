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
from CommonsCloudAPI.models.application import UserApplications
from CommonsCloudAPI.models.application import is_public

from . import module


@module.route('/v2/applications.<string:extension>', methods=['OPTIONS'])
def application_preflight(extension):
  return status_.status_200(), 200


@module.route('/v2/applications/<int:application_id>.<string:extension>', methods=['OPTIONS'])
def application_single_preflight(application_id, extension):
  return status_.status_200(), 200


@module.route('/v2/applications/<int:application_id>/users/<int:user_id>.<string:extension>', methods=['OPTIONS'])
def application_user_preflight(application_id, user_id, extension):
  return status_.status_200(), 200


@module.route('/v2/applications.<string:extension>', methods=['GET'])
@oauth.require_oauth('applications')
def application_list(oauth_request, extension):

  Application_ = Application()
  Application_.current_user = oauth_request.user

  applications_ = Application_.application_list()

  if type(applications_) is tuple:
    return applications_

  arguments = {
    'the_content': applications_,
    'list_name': 'applications',
    'extension': extension
  }

  return Application_.endpoint_response(**arguments)


@module.route('/v2/applications/<int:application_id>.<string:extension>', methods=['GET'])
@is_public()
@oauth.oauth_or_public()
def application_get(oauth_request, application_id, extension, is_public):

  Application_ = Application()
  Application_.current_user = oauth_request.user

  this_application = Application_.application_get(application_id, is_public)

  if type(this_application) is tuple:
    return this_application

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

  if type(new_application) is tuple:
    return new_application

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

  if type(updated_application) is tuple:
    return updated_application

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

  application_deleted = Application_.application_delete(application_id)

  if type(application_deleted) is tuple:
    return application_deleted

  return status_.status_204(), 204


@module.route('/v2/applications/<int:application_id>/users/<int:user_id>.<string:extension>', methods=['GET'])
@oauth.require_oauth('applications')
def application_user_get(oauth_request, application_id, user_id, extension):

  UserApplications_ = UserApplications(application_id, user_id)
  UserApplications_.current_user = oauth_request.user

  user_permissions = UserApplications_.permission_get(application_id, user_id)

  if type(user_permissions) is tuple:
    return user_permissions

  arguments = {
    'the_content': user_permissions,
    'extension': extension
  }

  return UserApplications_.endpoint_response(**arguments)


@module.route('/v2/applications/<int:application_id>/users/<int:user_id>.<string:extension>', methods=['POST'])
@oauth.require_oauth('applications')
def application_user_create(oauth_request, application_id, user_id, extension):

  UserApplications_ = UserApplications(application_id, user_id)
  UserApplications_.current_user = oauth_request.user

  user_permissions = UserApplications_.permission_create(application_id, user_id, request)

  if type(user_permissions) is tuple:
    return user_permissions

  arguments = {
    'the_content': user_permissions,
    'extension': extension
  }

  return UserApplications_.endpoint_response(**arguments)


@module.route('/v2/applications/<int:application_id>/users/<int:user_id>.<string:extension>', methods=['PUT', 'PATCH'])
@oauth.require_oauth('applications')
def application_user_update(oauth_request, application_id, user_id, extension):

  UserApplications_ = UserApplications(application_id, user_id)
  UserApplications_.current_user = oauth_request.user

  user_permissions = UserApplications_.permission_update(application_id, user_id, request)

  if type(user_permissions) is tuple:
    return user_permissions

  arguments = {
    'the_content': user_permissions,
    'extension': extension
  }

  return UserApplications_.endpoint_response(**arguments)


@module.route('/v2/applications/<int:application_id>/users/<int:user_id>.<string:extension>', methods=['DELETE'])
@oauth.require_oauth('applications')
def application_user_delete(oauth_request, application_id, user_id, extension):

  UserApplications_ = UserApplications(application_id, user_id)
  UserApplications_.current_user = oauth_request.user

  user_permissions = UserApplications_.permission_delete(application_id, user_id)

  if type(user_permissions) is tuple:
    return user_permissions

  arguments = {
    'the_content': user_permissions,
    'extension': extension
  }

  return status_.status_204(), 204
