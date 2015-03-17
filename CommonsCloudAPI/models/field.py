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
Field Model

@arg (object) db.Model
   This model is subclassed from the Flask-SQLAlchemy db.Model provided by
   using the Flask-SQLAlchemy package. db.Model is actually just a Declarative
   Base that is pre-defined when you use Flask-SQLAlchemy.

@see http://docs.sqlalchemy.org/en/rel_0_9/orm/extensions/declarative.html\
      #sqlalchemy.ext.declarative.declarative_base
   For more information on using Declarative Base

@see https://pythonhosted.org/Flask-SQLAlchemy/models.html
   For more information about declaring models within Flask-SQLAlchemy

"""
class Field(db.Model):

  """
  Name of the database table that holds `field` data

  @see http://docs.sqlalchemy.org/en/rel_0_9/orm/extensions/declarative.html\
        #table-configuration
  """
  __tablename__ = 'field'
  __table_args_ = {
    'extend_existing': True
  }

  """
  Fields within the data model 
  """
  id = db.Column(db.Integer, primary_key=True)
  label = db.Column(db.String(100))
  name = db.Column(db.String(100))
  help = db.Column(db.String(255))
  data_type = db.Column(db.String(100))
  relationship = db.Column(db.String(255))
  association = db.Column(db.String(255))
  weight = db.Column(db.Integer)
  status = db.Column(db.Boolean)
  options = db.Column(db.Text)

  is_visible = db.Column(db.Boolean)
  is_public = db.Column(db.Boolean)
  is_listed = db.Column(db.Boolean)
  is_searchable = db.Column(db.Boolean)
  is_required = db.Column(db.Boolean)

  """
  Initialize the data model and let the system know how each field should be
  handled by default 
  """
  def __init__(self, label="", name="", help="", data_type="", relationship="",
                association="", is_public=True, is_visible=True, is_listed=True,
                is_searchable=False, is_required=False, weight=0, status=True,
                options=""):
      self.label = label
      self.name = name
      self.help = help
      self.data_type = data_type
      self.relationship = relationship
      self.association = association
      self.weight = weight
      self.status = status
      self.options = options

      self.is_visible = is_visible
      self.is_public = is_public
      self.is_listed = is_listed
      self.is_searchable = is_searchable
      self.is_required = is_required
