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
import json

from datetime import datetime


"""
Import Flask Dependencies
"""
from flask import abort
from flask import request


"""
Import Commons Cloud Dependencies
"""
from CommonsCloudAPI.models.base import CommonsModel

from CommonsCloudAPI.extensions import db
from CommonsCloudAPI.extensions import sanitize
from CommonsCloudAPI.extensions import status as status_


class UserApplications(db.Model, CommonsModel):

  __tablename__ = 'user_applications'
  __table_args__ = {
    'extend_existing': True
  }

  user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), primary_key=True)
  application_id = db.Column(db.Integer(), db.ForeignKey('application.id'), primary_key=True)
  view = db.Column(db.Boolean())
  edit = db.Column(db.Boolean())
  delete = db.Column(db.Boolean())
  applications = db.relationship('Application', backref=db.backref("user_applications", cascade="all,delete"))


"""
Define our individual models
"""
class Application(db.Model, CommonsModel):

  __public__ = ['id', 'name', 'description', 'url', 'created', 'status']

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
  templates = db.relationship('ApplicationTemplates', backref=db.backref('application'))


  def __init__(self, name="", url="", description=None, created=datetime.utcnow(), status=True, templates=[], current_user_={}):
    self.name = name
    self.description = description
    self.url = url
    self.created = created
    self.status = status
    self.templates = templates
    self.current_user = current_user_


  """
  Create a new application in the CommonsCloudAPI

  @param (object) self

  @param (dictionary) application_content
      The content that is being submitted by the user
  """
  def application_create(self, request_object):

    """
    Make sure we can use the request data as json
    """
    application_content = json.loads(request_object.data)

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

    self.set_user_application_permissions(application_, permission, self.current_user)

    return application_


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

    if not hasattr(application_, 'id'):
      return abort(404)

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

    if not hasattr(self.current_user, 'id'):
      return abort(401)

    for application in self.current_user.applications:
      applications_.append(application.application_id)

    return applications_


  """
  Create a new application in the CommonsCloudAPI

  @param (object) self

  @param (dictionary) application_content
      The content that is being submitted by the user
  """
  def application_update(self, application_id, request_object):

    """
    Part 1: Load the application we wish to make changes to
    """
    application_ = Application.query.get(application_id)
    application_content = json.loads(request_object.data)


    """
    Part 2: Update the fields that we have data for
    """
    if hasattr(application_, 'name'):
      application_.name = sanitize.sanitize_string(application_content.get('name', application_.name))

    if hasattr(application_, 'description'):
      application_.description = sanitize.sanitize_string(application_content.get('description', application_.description))

    if hasattr(application_, 'url'):
      application_.url = sanitize.sanitize_string(application_content.get('url', application_.url))


    db.session.commit()

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
  def application_delete(self, application_id):

    application_ = Application.query.get(application_id)
    db.session.delete(application_)
    db.session.commit()



# class Person(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.Unicode, unique=True)
#     birth_date = db.Column(db.Date)
#     computers = db.relationship('Computer',
#                                 backref=db.backref('owner',
#                                                    lazy='dynamic'))

# class Computer(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.Unicode, unique=True)
#     vendor = db.Column(db.Unicode)
#     owner_id = db.Column(db.Integer, db.ForeignKey('person.id'))
#     purchase_time = db.Column(db.DateTime)
