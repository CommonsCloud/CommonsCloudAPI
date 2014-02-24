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


"""
Import Application Module Dependencies
"""
from .permissions import check_permissions


# application_templates = db.Table('application_templates',
#     db.Column('application', db.Integer, db.ForeignKey('application.id')),
#     db.Column('template', db.Integer, db.ForeignKey('template.id')),
#     extend_existing = True
# )

class UserApplications(db.Model):

  __tablename__ = 'user_applications'
  __table_args__ = {
    'extend_existing': True
  }

  user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), primary_key=True)
  application_id = db.Column(db.Integer(), db.ForeignKey('application.id'), primary_key=True)
  view = db.Column(db.Boolean())
  edit = db.Column(db.Boolean())
  delete = db.Column(db.Boolean())
  applications = db.relationship('Application', backref='user_apps')


"""
Define our individual models
"""
class Application(db.Model):

  __tablename__ = 'application'
  __table_args__ = {
    'extend_existing': True
  }

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(60))
  description = db.Column(db.String(255))
  url = db.Column(db.String(255))
  created = db.Column(db.DateTime)
  status = db.Column(db.Boolean)
  # templates = db.relationship("Template", secondary=application_templates, backref=db.backref('applications'))

  def __init__(self, name="", url="", description=None, created=datetime.utcnow(), status=True, templates=[]):
    self.name = name
    self.description = description
    self.url = url
    self.created = created
    self.status = status
    # self.templates = templates


  """
  Create a new application in the CommonsCloudAPI

  @param (object) self

  @param (dictionary) application_content
      The content that is being submitted by the user
  """
  def application_create(self, application_content):


    """
    Part 1: Add the new application to the database
    """
    new_application = {
      'name': sanitize.sanitize_string(application_content.get('name', '')),
      'description': sanitize.sanitize_string(application_content.get('description', '')),
      'url': application_content.get('url', '')
    }

    application_ = Application(**new_application)

    db.session.add(application_)
    db.session.commit()


    """
    Part 2: Tell the system what user should have permission to
    access the newly created application
    """
    permission = {
      'view': True,
      'edit': True,
      'delete': True
    }

    self.set_user_application_permissions(application_, permission, current_user)

    return application_


  """
  Associate a user with a specific application

  @param (object) self

  @param (object) application
      A fully qualified Application object to act on

  @param (dict) permission
      A dictionary containing boolean values for the `view`, `edit`, and `delete` properties

      Example: 

        permission = {
          'view': True,
          'edit': True,
          'delete': True
        }

  @param (object) user
      A fully qualified User object that we can act on

  @return (object) new_permission
      The permission object that was saved to the database

  """
  def set_user_application_permissions(self, application, permission, user):

    """
    Start a new Permission object
    """
    new_permission = UserApplications(**permission)

    """
    Set the ID of the Application to act upon
    """
    new_permission.application_id = application.id

    """
    Add the new permissions defined with the user defined
    """
    user.applications.append(new_permission)
    db.session.commit()

    return new_permission


  """
  Get an existing Applications from the CommonsCloudAPI

  @param (object) self

  @param (int) application_id
      The unique ID of the Application to be retrieved from the system

  @return (object) application_
      A fully qualified Application object

  """
  def application_get(self, application_id):

    application_ = Application.query.get(application_id)

    return application_


  """
  Get a list of existing Applications from the CommonsCloudAPI

  @param (object) self

  @return (list) applications
      A list of applications and their given permissions for the current user

  """
  def application_list(self):

    """
    Get a list of the applications the current user has access to
    and load their information from the database
    """
    application_id_list_ = self._application_id_list()
    applications_ = Application.query.filter(Application.id.in_(application_id_list_)).all()

    return applications_


  """
  Get a list of application ids from the current user and convert
  them into a list of numbers so that our SQLAlchemy query can
  understand what's going on

  @param (object) self

  @return (list) applications_
      A list of applciations the current user has access to
  """
  def _application_id_list(self):

    applications_ = []

    for application in current_user.applications:
      applications_.append(application.application_id)

    return applications_






