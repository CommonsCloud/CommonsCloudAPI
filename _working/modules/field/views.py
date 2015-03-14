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
Import Application Dependencies
"""
from CommonsCloudAPI.extensions import oauth
from CommonsCloudAPI.extensions import status as status_

from CommonsCloudAPI.models.template import Template
from CommonsCloudAPI.models.field import Field
from CommonsCloudAPI.models.field import is_public

from . import module


@module.route('/v2/templates/<int:template_id>/fields.<string:extension>', methods=['OPTIONS'])
def fields_preflight(template_id, extension):
    return status_.status_200(), 200

@module.route('/v2/templates/<int:template_id>/fields/<int:field_id>.<string:extension>', methods=['OPTIONS'])
def fields_single_preflight(template_id, field_id, extension):
    return status_.status_200(), 200


@module.route('/v2/templates/<int:template_id>/fields/<int:field_id>.<string:extension>', methods=['GET'])
@is_public()
@oauth.oauth_or_public()
def field_get(oauth_request, template_id, field_id, extension, is_public):

  Field_ = Field()
  Field_.current_user = oauth_request.user
  this_field = Field_.field_get(field_id, is_public)

  if type(this_field) is tuple:
    return this_field

  arguments = {
    'the_content': this_field,
    'extension': extension
  }

  return Field_.endpoint_response(**arguments)


"""
A list of templates that belongs to a specific application
"""
@module.route('/v2/templates/<int:template_id>/fields.<string:extension>', methods=['GET'])
@is_public()
@oauth.oauth_or_public()
def template_fields_get(oauth_request, template_id, extension, is_public):

  Field_ = Field()
  Field_.current_user = oauth_request.user
  these_fields = Field_.template_fields_get(template_id, is_public)

  if type(these_fields) is tuple:
    return these_fields

  arguments = {
    'the_content': these_fields,
    'list_name': 'fields',
    'extension': extension
  }

  return Field_.endpoint_response(**arguments)



@module.route('/v2/templates/<int:template_id>/fields.<string:extension>', methods=['POST'])
@oauth.require_oauth()
def field_post(oauth_request, template_id, extension):

  Field_ = Field()
  Field_.current_user = oauth_request.user
  new_field = Field_.field_create(request, template_id)

  if type(new_field) is tuple:
    return new_field

  arguments = {
    'the_content': new_field,
    'extension': extension,
    'code': 201
  }

  return Field_.endpoint_response(**arguments)


"""
PUT/PATCH

User attempting to access this endpoint must have the `edit`
permission associated with them in the `user_templates` table
"""
@module.route('/v2/templates/<int:template_id>/fields/<int:field_id>.<string:extension>', methods=['PUT', 'PATCH'])
@oauth.require_oauth()
def field_update(oauth_request, template_id, field_id, extension):

  Field_ = Field()
  Field_.current_user = oauth_request.user
  updated_field = Field_.field_update(request, template_id, field_id)

  if type(updated_field) is tuple:
    return updated_field

  arguments = {
    'the_content': updated_field,
    'extension': extension
  }

  return Field_.endpoint_response(**arguments)


@module.route('/v2/templates/<int:template_id>/fields/<int:field_id>.<string:extension>', methods=['DELETE'])
@oauth.require_oauth()
def field_delete(oauth_request, template_id, field_id, extension):

  Field_ = Field()
  Field_.current_user = oauth_request.user
  deleted_field =Field_.field_delete(template_id, field_id)

  if type(deleted_field) is tuple:
    return deleted_field

  return status_.status_204(), 204
