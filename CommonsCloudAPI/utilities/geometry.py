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


class ST_GeomFromGeoJSON(GenericFunction):
    name = 'ST_GeomFromGeoJSON'
