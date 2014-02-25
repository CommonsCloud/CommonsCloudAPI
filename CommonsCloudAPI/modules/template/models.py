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
Import Application Dependencies
"""
from CommonsCloudAPI.extensions import db


"""
Template

A template within CommonsCloudAPI is backbone of the system, allowing for
organizations to collection data, a template defines the data model within
the system.

@param (object) db.Model
    The model is the Base we use to define our database structure
"""
class Template(db.Model):
  
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(60))
  help = db.Column(db.String(255))
  storage = db.Column(db.String(255))
  is_public = db.Column(db.Boolean)
  is_crowdsourced = db.Column(db.Boolean)
  is_moderated = db.Column(db.Boolean)
  is_listed = db.Column(db.Boolean)
  created = db.Column(db.DateTime)
  status = db.Column(db.Boolean)
  # fields = db.relationship("Field", secondary=template_fields, backref=db.backref('templates'))
  # statistics = db.relationship("Statistic", backref=db.backref('statistics'))

  def __init__(self, name="", help="", storage="", is_public="", is_crowdsourced="", is_moderated="", is_listed="", created=datetime.utcnow(), status=True):
    self.name = name
    self.help = help
    self.storage = storage
    self.is_public = is_public
    self.is_crowdsourced = is_crowdsourced
    self.is_moderated = is_moderated
    self.is_listed = is_listed
    self.created = created
    self.status = status


    