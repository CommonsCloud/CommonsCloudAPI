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
Import Python Dependencies
"""
from datetime import datetime
from datetime import timedelta


"""
Import Flask Dependencies
"""
from flask import jsonify


"""
Import CommonsCloudAPI Dependencies
"""
from . import FormatContent

from CommonsCloudAPI.extensions import db


"""
A class for formatting objects in Java Script Object Notation or JSON

@requires ForamtContent

@method create

"""
class JSON(FormatContent):

  """
  Creates a JSON file based on user requested content

  @requires
      from flask import jsonify

  @param (object) self
      The object we are acting on behalf of

  @return (method) jsonify
  	  A jsonified object ready for displayin the browser as JSON

  """
  def create(self):

    today = datetime.utcnow()
    expires =  today + timedelta(+30)

    content = {}

    for property_ in self.the_content:
      content[property_] = self.the_content[property_]

    response = jsonify({
      "response": content,
      "properties": self.extras
    })

    """
    Make sure we're caching the responses for 30 days to speed things up,
    then setting modification and expiration dates appropriately
    """
    # response.headers.add('Last-Modified', today)
    # response.headers.add('Expires', expires)
    # response.headers.add('Pragma', 'max-age=2592000')
    # response.headers.add('Cache-Control', 'max-age=2592000')

    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Accept,Content-Type,X-Requested-With,accept,Origin,Access-Control-Request-Method,Access-Control-Request-Headers,Authorization')
    response.headers.add('Access-Control-Allow-Credentials', True)
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, OPTIONS, DELETE')

    response.headers.add('Pragma', 'no-cache')
    response.headers.add('Cache-Control', 'no-cache')

    return response
