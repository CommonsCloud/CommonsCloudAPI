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


class Template(db.Model):
  
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(60))
  help = db.Column(db.String(255))
  storage = db.Column(db.String(255))
  is_public = db.Column(db.Boolean)
  crowd_sourcing = db.Column(db.Boolean)
  moderate = db.Column(db.Boolean)
  is_listed = db.Column(db.Boolean)
  created = db.Column(db.DateTime)
  status = db.Column(db.Boolean)
  # fields = db.relationship("Field", secondary=template_fields, backref=db.backref('templates'))
  # statistics = db.relationship("Statistic", backref=db.backref('statistics'))

  def __init__(self, name, storage, owner, description="", publicly_viewable="", crowd_sourcing="", moderate="", applications=None):
    self.name = name
    self.description = description
    self.storage = storage
    self.owner = owner
    self.publicly_viewable = publicly_viewable
    self.crowd_sourcing = crowd_sourcing
    self.moderate = moderate
    self.created = datetime.utcnow()
    self.applications = applications
    self.is_listed = True
    self.status = True

