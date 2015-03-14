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
Import Commons Cloud Dependencies
"""
from CommonsCloudAPI.extensions import db


"""
This defines our basic Role model, we have to have this becasue of the
Flask-Security module. If you remove it Flask-Security gets fussy.
"""
class Organization(db.Model):

  """
  Name of the database table that holds `organization` data

  @see http://docs.sqlalchemy.org/en/rel_0_9/orm/extensions/declarative.html#table-configuration
  """
  __tablename__ = 'organization'
  __table_args__ = {
    'extend_existing': True
  }

  """
  Fields within the data model 
  """
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(255), unique=True)
  description = db.Column(db.String(255))