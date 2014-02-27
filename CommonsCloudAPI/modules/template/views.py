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
from flask import redirect
from flask import request
from flask import url_for

from flask.ext.security import current_user


"""
Import Application Dependencies
"""
from CommonsCloudAPI.extensions import oauth
from CommonsCloudAPI.extensions import status as status_

from CommonsCloudAPI.utilities.format_csv import CSV
from CommonsCloudAPI.utilities.format_json import JSON


"""
Import Module Dependencies
"""
from . import module

from CommonsCloudAPI.models.template import Template

from .permissions import permission_required


@module.route('/template/', methods=['GET'])
# @oauth.require_oauth()
def template_list():

  Template_ = Template()
  templates_ = Template_.template_list()

  arguments = {
    'the_content': templates_,
    'list_name': 'templates'
  }

  return Template_.endpoint_response(**arguments)


"""
CREATE

Everyone that has a user account can add new applications, however
in the future we should figure out what the repercussions of that are.
"""
@module.route('/template/', methods=['POST'])
# @oauth.require_oauth()
def template_post():

  Template_ = Template()
  new_template = Template_.template_create(request)

  return Template_.endpoint_response(new_template, code=201)


"""
GET/VIEW

User attempting to access this endpoint must have the `view`
permission associated with them in the `user_templates` table
"""
@module.route('/template/<int:template_id>/', methods=['GET'])
# @oauth.require_oauth()
@permission_required('can_view')
def template_get(template_id):

  Template_ = Template()
  this_template = Template_.template_get(template_id)

  return Template_.endpoint_response(this_template)


"""
PUT/PATCH

User attempting to access this endpoint must have the `edit`
permission associated with them in the `user_templates` table
"""
@module.route('/template/<int:template_id>/', methods=['PUT', 'PATCH'])
# @oauth.require_oauth()
@permission_required('can_edit')
def application_update(template_id):

  Template_ = Template()
  updated_template = Template_.template_update(template_id, request)

  return Template_.endpoint_response(updated_template)


"""
DELETE

User attempting to access this endpoint must have the `delete`
permission associated with them in the `user_applications` table
"""
@module.route('/template/<int:template_id>/', methods=['DELETE'])
# @oauth.require_oauth()
@permission_required('can_delete')
def template_delete(template_id):

  Template().template_delete(template_id)

  return status_.status_204(), 204