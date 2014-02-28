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


@module.route('/template/<int:template_id>/field/', methods=['POST'])
# @oauth.require_oauth()
def field_post(template_id):

  Field_ = Field()
  new_field = Field_.field_create(request, template_id)

  return Field_.endpoint_response(new_field, code=201)
