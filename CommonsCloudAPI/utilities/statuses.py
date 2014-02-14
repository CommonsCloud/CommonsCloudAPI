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
from flask import current_app
from flask import jsonify

class Status():

  def __init__(self):

    self.return_type = 'json'

  def status_401(self):

    message = {
      'error': '401 Unauthorized',
      'status_code': '401',
      'message': 'The request requires user authentication.'
    }

    return jsonify(message) if return_type == 'json' else message


  def status_415(self):

    message = {
      'error': '415 Unsupported Media Type',
      'status_code': '415',
      'message': 'The server is refusing to service the request because the entity of the request is in a format not supported by the requested resource for the requested method.'
    }

    return jsonify(message) if return_type == 'json' else message


