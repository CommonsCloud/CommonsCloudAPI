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

from CommonsCloudAPI.models.statistic import Statistic

from . import module


@module.route('/v2/templates/<int:template_id>/statistics.<string:extension>', methods=['OPTIONS'])
def statistic_preflight(template_id, extension):
  return status_.status_200(), 200


@module.route('/v2/templates/<int:template_id>/statistics/<int:statistic_id>.<string:extension>', methods=['OPTIONS'])
def statistic_single_preflight(template_id, statistic_id, extension):
  return status_.status_200(), 200


@module.route('/v2/templates/<int:template_id>/statistics.<string:extension>', methods=['GET'])
@oauth.require_oauth()
def statistic_list(oauth_request, template_id, extension):

  Statistic_ = Statistic()
  Statistic_.current_user = oauth_request.user
  statistic_list = Statistic_.statistic_list(template_id)

  if type(statistic_list) is tuple:
    return statistic_list

  arguments = {
    'the_content': statistic_list,
    'list_name': 'statistics',
    'extension': extension
  }

  return Statistic_.endpoint_response(**arguments)

@module.route('/v2/templates/<int:template_id>/statistics/<int:statistic_id>.<string:extension>', methods=['GET'])
@oauth.require_oauth()
def statistic_get(oauth_request, template_id, statistic_id, extension):

  Statistic_ = Statistic()
  Statistic_.current_user = oauth_request.user
  statistic_get = Statistic_.statistic_get(template_id, statistic_id)

  if type(statistic_get) is tuple:
    return statistic_get

  arguments = {
    'the_content': statistic_get,
    'extension': extension
  }

  return Statistic_.endpoint_response(**arguments)


@module.route('/v2/templates/<int:template_id>/statistics.<string:extension>', methods=['POST'])
@oauth.require_oauth()
def statistic_post(oauth_request, template_id, extension):

  Statistic_ = Statistic()
  Statistic_.current_user = oauth_request.user
  new_statistic = Statistic_.statistic_create(template_id, request)

  if type(new_statistic) is tuple:
    return new_statistic

  arguments = {
    'the_content': new_statistic,
    'extension': extension
  }

  return Statistic_.endpoint_response(**arguments)


@module.route('/v2/templates/<int:template_id>/statistics/<int:statistic_id>.<string:extension>', methods=['PUT', 'PATCH'])
@oauth.require_oauth()
def statistic_update(oauth_request, template_id, statistic_id, extension):

  Statistic_ = Statistic()
  Statistic_.current_user = oauth_request.user
  updated_statistic = Statistic_.statistic_update(template_id, statistic_id, request)

  if type(updated_statistic) is tuple:
    return updated_statistic

  arguments = {
    'the_content': updated_statistic,
    'extension': extension,
    'code': 200
  }

  print 'returned'

  return Statistic_.endpoint_response(**arguments)


@module.route('/v2/templates/<int:template_id>/statistics/<int:statistic_id>.<string:extension>', methods=['DELETE'])
@oauth.require_oauth()
def statistic_delete(oauth_request, template_id, statistic_id, extension):

  Statistic_ = Statistic()
  Statistic_.current_user = oauth_request.user
  deleted_statistic = Statistic_.statistic_delete(template_id, statistic_id)

  if type(deleted_statistic) is tuple:
    return deleted_statistic

  return status_.status_204(), 204

