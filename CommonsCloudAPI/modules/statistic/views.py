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


@module.route('/template/<int:template_id>/statistics/', methods=['GET'])
# @oauth.require_oauth()
def statistic_list(template_id):

  Statistic_ = Statistic()

  statistics_ = Statistic_.statistic_list()

  arguments = {
    'the_content': statistics_,
    'list_name': 'statistics'
  }

  return Statistic_.endpoint_response(**arguments)