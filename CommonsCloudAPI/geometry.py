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
from geoalchemy2 import Geometry
from geoalchemy2.functions import GenericFunction


"""
ST_GeomFromGeoJSON

This Class extends the existing Geoalchemy2 functionality by adding an existing
PostGIS method to the Geoalchemy2 package.

  @see http://postgis.net/docs/ST_GeomFromGeoJSON.html
  @see http://geoalchemy-2.readthedocs.org/en/latest/spatial_functions.html
      #geoalchemy2.functions.GenericFunction

"""
class ST_GeomFromGeoJSON(GenericFunction):
    name = 'ST_GeomFromGeoJSON'
    type = Geometry