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

from . import module


@module.route('/v2/templates.<string:extension>', methods=['OPTIONS'])
def templates_preflight(extension):
    return status_.status_200(), 200


@module.route('/v2/templates/<int:template_id>.<string:extension>', methods=['OPTIONS'])
def templates_single_preflight(template_id, extension):
    return status_.status_200(), 200


@module.route('/v2/applications/<int:application_id>/templates.<string:extension>', methods=['OPTIONS'])
def application_templates_preflight(application_id, extension):
    return status_.status_200(), 200


@module.route('/v2/templates.<string:extension>', methods=['GET'])
@oauth.require_oauth()
def template_list(extension):
  return status_.status_303(), 303


@module.route('/v2/applications/<int:application_id>/templates.<string:extension>', methods=['GET'])
@oauth.require_oauth()
def application_templates_get(oauth_request, application_id, extension):

  Template_ = Template()
  Template_.current_user = oauth_request.user

  these_templates = Template_.application_templates_get(application_id)

  if type(these_templates) is 'Response':
    return these_templates, these_templates.code

  arguments = {
    'the_content': these_templates,
    'list_name': 'templates',
    'extension': extension
  }

  return Template_.endpoint_response(**arguments)


@module.route('/v2/applications/<int:application_id>/templates.<string:extension>', methods=['POST'])
@oauth.require_oauth()
def template_post(oauth_request, application_id, extension):

  Template_ = Template()
  Template_.current_user = oauth_request.user
  new_template = Template_.template_create(request, application_id)

  arguments = {
    'the_content': new_template,
    'extension': extension,
    'code': 201
  }

  return Template_.endpoint_response(**arguments)


@module.route('/v2/templates/<int:template_id>.<string:extension>', methods=['GET'])
@oauth.require_oauth()
def template_get(oauth_request, template_id, extension):

  Template_ = Template()
  Template_.current_user = oauth_request.user
  this_template = Template_.template_get(template_id)

  arguments = {
    'the_content': this_template,
    'extension': extension
  }

  return Template_.endpoint_response(**arguments)


@module.route('/v2/templates/<int:template_id>.<string:extension>', methods=['PUT', 'PATCH'])
@oauth.require_oauth()
def application_update(oauth_request, template_id, extension):

  Template_ = Template()
  Template_.current_user = oauth_request.user
  updated_template = Template_.template_update(template_id, request)

  arguments = {
    'the_content': updated_template,
    'extension': extension
  }

  return Template_.endpoint_response(**arguments)


@module.route('/v2/templates/<int:template_id>.<string:extension>', methods=['DELETE'])
@oauth.require_oauth()
def template_delete(oauth_request, template_id, extension):

  Template_ = Template()
  Template_.current_user = oauth_request.user
  Template_.template_delete(template_id)

  return status_.status_204(), 204

