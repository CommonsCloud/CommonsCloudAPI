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


"""
Import Flask Dependencies
"""
from flask.ext.security import current_user


"""
Import Commons Cloud Dependencies
"""
from CommonsCloudAPI.extensions import db
from CommonsCloudAPI.extensions import sanitize

application_templates = db.Table('application_templates',
    db.Column('application', db.Integer, db.ForeignKey('application.id')),
    db.Column('template', db.Integer, db.ForeignKey('template.id'))
)

class UserApplications(db.Model):

  __tablename__ = 'user_applications'

  user = db.Column(db.Integer(), db.ForeignKey('user.id'), primary_key=True)
  application = db.Column(db.Integer(), db.ForeignKey('application.id'), primary_key=True)
  view = db.Column(db.Boolean())
  edit = db.Column(db.Boolean())
  delete = db.Column(db.Boolean())
  applications = db.relationship('Application', backref='user_apps')


"""
Define our individual models
"""
class Application(db.Model):

  __tablename__ = 'application'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(60))
  description = db.Column(db.String(255))
  owner = db.Column(db.Integer)
  created = db.Column(db.DateTime)
  status = db.Column(db.Boolean)
  templates = db.relationship("Template", secondary=application_templates, backref=db.backref('applications'))

  def __init__(self, name="", owner="", description=None, created=datetime.utcnow(), status=True, templates=[]):
    self.name = name
    self.description = description
    self.owner = owner
    self.created = created
    self.status = status
    self.templates = templates

  """
  Create a new application in the CommonsCloudAPI

  @param (object) self

  """
  def application_create(self, application_content):

    new_application = {
      'name': sanitize.sanitize_string(application_content.get('name', '')),
      'description': sanitize.sanitize_string(application_content.get('description', '')),
      'url': application_content.get('url', '')
    }

    application_ = Application(**new_application)

    db.session.add(application_)
    db.session.commit()

    permission = {
      'view': True,
      'edit': True,
      'delete': True
    }

    a = UserApplications(**permission)
    a.application = application_.id

    current_user.applications.append(a)

    db.session.commit()

    return application_


  """
  Get an existing Applications from the CommonsCloudAPI

  @param (object) self

  """
  def application_get(self, application_id):

    application_ = Application.query.get(application_id)
    return application_


  """
  Get a list of existing Applications from the CommonsCloudAPI

  @param (object) self

  """
  def application_list(self):

    current_user_applications_ = current_user.applications

    return current_user_applications_
