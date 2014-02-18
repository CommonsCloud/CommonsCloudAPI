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
Import CommonsCloudAPI Dependencies
"""
from .format import FormatContent


"""
A class for formatting objects in Java Script Object Notation or JSON

@requires ForamtContent

@method create

"""
class JSON(FormatContent):

  """
  Define our default variables

  @param (object) self
      The object we are acting on behalf of

  @param (object) data
      The actual content we'll be converting

  @param (boolean) serialize
      A flag to identify whether or not the content needs to be serialized
      before it is processed by our formatting tasks
  """
  def __init__(self, data, serialize=False, exclude_fields=[]):
    self.the_content = data
    self.serialize = serialize
    self.exclude_fields = exclude_fields


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

    if type(self.the_content) is list and self.serialize is True:
      self.the_content = self.serialize_list()
    elif self.serialize is True:
      self.the_content = self.serialize_object()

    return_ = {
      "response": self.the_content
    }

    return jsonify(return_)
