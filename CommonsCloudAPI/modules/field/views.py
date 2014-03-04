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
from CommonsCloudAPI.models.field import Field

from .permissions import permission_required


"""
A list of templates that belongs to a specific application
"""
@module.route('/template/<int:template_id>/field/', methods=['GET'])
# @oauth.require_oauth()
def template_fields_get(template_id):

  Field_ = Field()
  these_fields = Field_.template_fields_get(template_id)

  if type(these_fields) is 'Response':
    return these_fields, these_fields.code

  arguments = {
    'the_content': these_fields,
    'list_name': 'fields'
  }

  return Field_.endpoint_response(**arguments)



@module.route('/template/<int:template_id>/field/', methods=['POST'])
# @oauth.require_oauth()
def field_post(template_id):

  Field_ = Field()
  new_field = Field_.field_create(request, template_id)

  return Field_.endpoint_response(new_field, code=201)


@module.route('/template/<int:template_id>/field/<int:field_id>/', methods=['DELETE'])
# @oauth.require_oauth()
@permission_required('can_delete')
def field_delete(template_id, field_id):

  Field().field_delete(template_id, field_id)

  return status_.status_204(), 204
