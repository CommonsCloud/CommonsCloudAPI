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
Import CommonsCloudAPI Dependencies
"""
from CommonsCloudAPI.extensions import db


"""
Telephone Model

The `telephone` model defines user-agnostic `telephone` for lookup in their own table.
Each `telephone` can belong to multiple other resources within the API.

@arg (object) db.Model
   This model is subclassed from the Flask-SQLAlchemy db.Model provided by using
   the Flask-SQLAlchemy package. db.Model is actually just a Declarative Base that
   is pre-defined when you use Flask-SQLAlchemy.

@arg (object) BaseModel
   This model is subclassed from the BaseModel available as a CommonsCloudAPI model
   that allows the sharing of methods across classes.

@see http://docs.sqlalchemy.org/en/rel_0_9/orm/extensions/declarative.html#sqlalchemy.ext.declarative.declarative_base
   For more information on using Declarative Base

@see https://pythonhosted.org/Flask-SQLAlchemy/models.html
   For more information about declaring models within Flask-SQLAlchemy

"""
class Telephone(db.Model):


  """
  Name of the database table that holds `telephone` data

  @see http://docs.sqlalchemy.org/en/rel_0_9/orm/extensions/declarative.html#table-configuration
  """
  __tablename__ = 'telephone'
  __table_args_ = {
    'extend_existing': True
  }


  """
  Fields within the data model 
  """
  id = db.Column(db.Integer, primary_key=True)
  number = db.Column(db.Integer)
  category = db.Column(db.String(255))

