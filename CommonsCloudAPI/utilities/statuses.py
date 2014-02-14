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


"""
A Base Class for centralizing the information regarding HTTP messages to the
end user, to give them a better idea of what's going on

@variable (string) return_type

@method status_401
@method status_415

"""
class Status():

  """
  Define our default variables

  @param (object) self
      The object we are acting on behalf of

  @param (string) return_type
      The type of content we'd like to return to the user

  """
  def __init__(self):

    self.return_type = 'json'

  """
  401 Unauthorized

  @see
      http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.2

  @param (object) self
      The object we are acting on behalf of

  @return (method) jsonify || (dict) message
      Either a jsonfied dictionary or just the dictionary

  """
  def status_401(self):

    message = {
      'error': '401 Unauthorized',
      'status_code': '401',
      'message': 'The request requires user authentication.'
    }

    return jsonify(message) if self.return_type == 'json' else message


  """
  415 Unsupported Media Type

  @see
      http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.16

  @param (object) self
      The object we are acting on behalf of

  @return (method) jsonify || (dict) message
      Either a jsonfied dictionary or just the dictionary

  """
  def status_415(self):

    message = {
      'error': '415 Unsupported Media Type',
      'status_code': '415',
      'message': 'The server is refusing to service the request because the entity of the request is in a format not supported by the requested resource for the requested method.'
    }

    return jsonify(message) if self.return_type == 'json' else message


