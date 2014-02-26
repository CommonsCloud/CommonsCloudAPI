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

from CommonsCloudAPI.extensions import status as status_

from CommonsCloudAPI.utilities.format_csv import CSV
from CommonsCloudAPI.utilities.format_json import JSON



def application_response(application_object, list_name=''):

  """
  If the user is properly authenticated, then proceed to see if they
  have requests a type of content we serve
  """
  if request.headers['Content-Type'] == 'application/json' or \
      (hasattr(request.args, 'format') and request.args['format'] == 'json'):

    this_data = JSON(application_object, serialize=True, list_name=list_name)
    return this_data.create(), 200

  elif request.headers['Content-Type'] == 'text/csv' or \
      (hasattr(request.args, 'format') and request.args['format'] == 'csv'):

    this_data = CSV(application_object, serialize=True)
    return this_data.create(), 200

  """
  If the user hasn't requested a specific content type then we should
  tell them that, by directing them to an "Unsupported Media Type"
  """
  return status_.status_415(), 415
