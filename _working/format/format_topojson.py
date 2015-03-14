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

from geojson import Feature
from geojson import FeatureCollection

from topojson import topojson

"""
Import CommonsCloudAPI Dependencies
"""
from . import FormatContent

from CommonsCloudAPI.extensions import db
from CommonsCloudAPI.extensions import logger


"""
A class for formatting objects in Java Script Object Notation or JSON

@requires ForamtContent

@method create

"""
class TopoJSON(FormatContent):

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

    expires_ = self.extras.get('expires', today + timedelta(+364))
    max_age_ = self.extras.get('max_age', 'max-age=2592000')
    last_modified_ = self.extras.get('last_modified', today)

    # logger.warning('self.the_content %s', self.the_content.keys())

    if 'features' in self.the_content.keys():

        features = []

        for feature in self.the_content['features']:

          properties = {}

          for property_ in feature:
            if property_ != 'geometry':
              properties[property_] = feature[property_]

          arguments = {
            'geometry': feature.get('geometry', None),
            'id': feature.get('id', None),
            'properties': properties
          }

          try:
            this_feature = Feature(**arguments)
          except Exception, e:
            logger.warning("Couldn't create object for GeoJSON %s > %s", feature.get('id', None), arguments)
            this_feature = None

          features.append(this_feature)

        arguments = {
          'properties': self.extras
        }

        response = jsonify(FeatureCollection(features, **arguments))
    else:

        properties = {}

        for property_ in self.the_content:
          if property_ != 'geometry':
            properties[property_] = self.the_content[property_]

        arguments = {
          'geometry': self.the_content.get('geometry', None),
          'id': self.the_content.get('id', None),
          'properties': properties
        }

        response = jsonify(Feature(**arguments))


    """
    Make sure we're caching the responses for 30 days to speed things up,
    then setting modification and expiration dates appropriately
    """
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Authorization, Accept, Content-Type, X-Requested-With, Origin, Access-Control-Request-Method, Access-Control-Request-Headers, Cache-Control, Expires, Set-Cookie')
    response.headers.add('Access-Control-Allow-Credentials', True)
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, OPTIONS, DELETE')

    response.headers.add('Last-Modified', last_modified_)
    response.headers.add('Expires', expires_)
    response.headers.add('Pragma', max_age_)
    response.headers.add('Cache-Control', max_age_)

    return response
