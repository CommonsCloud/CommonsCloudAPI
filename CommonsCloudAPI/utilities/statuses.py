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


"""
A Base Class for centralizing the information regarding HTTP messages to the
end user, to give them a better idea of what's going on

@see RFC 2616
    http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html

@variable (string) return_type

@method status_401
@method status_415

"""
class CommonsStatus():

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
  200 OK

  @param (object) self
      The object we are acting on behalf of

  @return (method) jsonify || (dict) message
      Either a jsonfied dictionary or just the dictionary

  """
  def status_200(self):

    message = {
      'status': '200 OK',
      'code': '200',
      'message': 'Looking good McFly'
    }

    response = jsonify(message)

    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Authorization, Accept, Content-Type, X-Requested-With, Origin, Access-Control-Request-Method, Access-Control-Request-Headers')
    response.headers.add('Access-Control-Allow-Credentials', True)
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE, OPTIONS')

    response.headers.add('Pragma', 'no-cache')
    response.headers.add('Cache-Control', 'no-cache')

    return response


  """
  204 No Content

  @see
      http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.2

  @param (object) self
      The object we are acting on behalf of

  @return (method) jsonify || (dict) message
      Either a jsonfied dictionary or just the dictionary

  """
  def status_204(self):

    message = {
      'status': '204 No Content',
      'code': '204',
      'message': 'This content no longer exists'
    }

    response = jsonify(message)

    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Authorization, Accept, Content-Type, X-Requested-With, Origin, Access-Control-Request-Method, Access-Control-Request-Headers')
    response.headers.add('Access-Control-Allow-Credentials', True)
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE, OPTIONS')

    response.headers.add('Pragma', 'no-cache')
    response.headers.add('Cache-Control', 'no-cache')

    return response

  """
  303 See Other

  @see
      http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.3.4

  @param (object) self
      The object we are acting on behalf of

  @return (method) jsonify || (dict) message
      Either a jsonfied dictionary or just the dictionary

  """
  def status_303(self):

    message = {
      'status': '303 See Other',
      'code': '303',
      'message': 'Please check the API documentation, as there is a different way you need to request your desired data.'
    }

    return jsonify(message) if self.return_type == 'json' else message


  """
  400 Bad Request

  @see
      http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.2

  @param (object) self
      The object we are acting on behalf of

  @return (method) jsonify || (dict) message
      Either a jsonfied dictionary or just the dictionary

  """
  def status_400(self, system_message=""):

    message = {
      'status': '400 Bad Request',
      'code': '400',
      'message': 'The request could not be understood by the server due to malformed syntax. You SHOULD NOT repeat the request without modifications.',
      'details': 'Chances are you forgot to include one of the required variables needed to create a new resource.',
      'error': str(system_message)
    }

    return jsonify(message) if self.return_type == 'json' else message


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
      'status': '401 Unauthorized',
      'code': '401',
      'message': 'The request requires user authentication.',
      'details': 'You probably just need to login or authenticate via OAuth before accessing this endpoint. Otherwise you do not have permission to access this resource.'
    }

    response = jsonify(message)

    response.headers.add('Access-Control-Allow-Origin', 'http://127.0.0.1:9000')
    response.headers.add('Access-Control-Allow-Credentials', 'true')

    return response


  """
  403 Not Authorized

  @see
      http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.5

  @param (object) self
      The object we are acting on behalf of

  @return (method) jsonify || (dict) message
      Either a jsonfied dictionary or just the dictionary

  """
  def status_403(self):

    message = {
      'status': '403 Forbidden',
      'code': '403',
      'message': 'The server has not found anything matching the Request-URI.',
      'details': 'You probably entered the URL wrong or perhaps what you were looking for has been removed.'
    }

    response = jsonify(message)

    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Authorization, Accept, Content-Type, X-Requested-With, Origin, Access-Control-Request-Method, Access-Control-Request-Headers')
    response.headers.add('Access-Control-Allow-Credentials', True)
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE OPTIONS')

    response.headers.add('Pragma', 'no-cache')
    response.headers.add('Cache-Control', 'no-cache')

    return response


  """
  404 Not Found

  @see
      http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.5

  @param (object) self
      The object we are acting on behalf of

  @return (method) jsonify || (dict) message
      Either a jsonfied dictionary or just the dictionary

  """
  def status_404(self):

    message = {
      'status': '404 Not Found',
      'code': '404',
      'message': 'The server has not found anything matching the Request-URI.',
      'details': 'You probably entered the URL wrong or perhaps what you were looking for has been removed.'
    }

    return jsonify(message) if self.return_type == 'json' else message


  """
  405 Method Not Allowed

  @see
      http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.5

  @param (object) self
      The object we are acting on behalf of

  @return (method) jsonify || (dict) message
      Either a jsonfied dictionary or just the dictionary

  """
  def status_405(self):

    message = {
      'status': '405 Method Not Allowed',
      'code': '405',
      'message': 'The method is not allowed for the requested URL.',
      'details': 'Check the documentation to ensure the method you\'re attempting to use is one of GET, POST, PATCH, or DELETE'
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
  def status_415(self, system_message=""):

    message = {
      'status': '415 Unsupported Media Type',
      'code': '415',
      'message': 'The server is refusing to service the request because the entity of the request is in a format not supported by the requested resource for the requested method.',
      'error': str(system_message).replace('"', "")
    }

    return jsonify(message) if self.return_type == 'json' else message


  """
  500 Internal Server Error

  @see
      http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.5.1

  @param (object) self
      The object we are acting on behalf of

  @return (method) jsonify || (dict) message
      Either a jsonfied dictionary or just the dictionary

  """
  def status_500(self, system_message=""):

    message = {
      'status': '500 Internal Server Error',
      'code': '500',
      'message': 'The server has not found anything matching the Request-URI.',
      'details': 'You need to check the system, application, and proxy logs.',
      'error': str(system_message).replace('"', "")
    }

    return jsonify(message) if self.return_type == 'json' else message

