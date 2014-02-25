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

from CommonsCloudAPI.utilities.format_csv import CSV
from CommonsCloudAPI.utilities.format_json import JSON


"""
Import Module Dependencies
"""
from . import module

from .models import Template


@module.route('/template/', methods=['GET'])
# @oauth.require_oauth()
def template_list(self):

  templates_ = Template().template_list()

  """
  If the user is properly authenticated, then proceed to see if they
  have requests a type of content we serve
  """
  if request.headers['Content-Type'] == 'application/json' or \
      (hasattr(request.args, 'format') and request.args['format'] == 'json'):

    this_data = JSON(templates_, serialize=True, list_name='templates')
    return this_data.create(), 200

  elif request.headers['Content-Type'] == 'text/csv' or \
      (hasattr(request.args, 'format') and request.args['format'] == 'csv'):

    this_data = CSV(templates_, serialize=True)
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
@module.route('/template/', methods=['POST'])
# @oauth.require_oauth()
def template_post():

  Template_ = Template()
  new_template = Template_.template_create(request)

  url_arguments = {
    'template_id': new_template.id,
    'format': 'json',
    '_external': True
  }

  return redirect(url_for('template.template_get', **url_arguments)), 201


"""
GET/VIEW

User attempting to access this endpoint must have the `view`
permission associated with them in the `user_templates` table
"""
@module.route('/template/<int:template_id>/', methods=['GET'])
# @oauth.require_oauth()
# @permission_required('can_view')
def template_get(template_id):

  this_template = Template().template_get(template_id)

  """
  If the user is properly authenticated, then proceed to see if they
  have requests a type of content we serve
  """
  if request.headers['Content-Type'] == 'application/json' or \
      (hasattr(request.args, 'format') and request.args['format'] == 'json'):

    this_data = JSON(this_template, serialize=True)
    return this_data.create(), 200

  elif request.headers['Content-Type'] == 'text/csv' or \
      (hasattr(request.args, 'format') and request.args['format'] == 'csv'):

    this_data = CSV(this_template, serialize=True)
    return this_data.create(), 200

  """
  If the user hasn't requested a specific content type then we should
  tell them that, by directing them to an "Unsupported Media Type"
  """
  return status_.status_415(), 415
