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


@module.route('/v2/statistics.<string:extension>', methods=['POST'])
# @oauth.require_oauth()
def statistic_post(extension):

  Statistic_ = Statistic()
  new_statistic = Statistic_.statistic_create(request)

  arguments = {
    'the_content': new_statistic,
    'extension': extension,
    'code': 201
  }

  return Statistic_.endpoint_response(**arguments)


@module.route('/v2/statistics/<int:statistic_id>.<string:extension>', methods=['PUT', 'PATCH'])
# @oauth.require_oauth()
def statistic_update(statistic_id, extension):

  Statistic_ = Statistic()
  updated_statistic = Statistic_.statistic_update(statistic_id, request)

  arguments = {
    'the_content': updated_statistic,
    'extension': extension,
    'code': 200
  }

  return Statistic_.endpoint_response(**arguments)


@module.route('/v2/statistics/<int:statistic_id>.<string:extension>', methods=['DELETE'])
# @oauth.require_oauth()
def statistic_delete(statistic_id, extension):

  Statistic().statistic_delete(statistic_id)

  return status_.status_204(), 204