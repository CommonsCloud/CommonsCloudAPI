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


class UserTemplates(db.Model):

  __tablename__ = 'user_templates'
  __table_args__ = {
    'extend_existing': True
  }

  user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), primary_key=True)
  template_id = db.Column(db.Integer(), db.ForeignKey('template.id'), primary_key=True)
  view = db.Column(db.Boolean())
  edit = db.Column(db.Boolean())
  delete = db.Column(db.Boolean())
  templates = db.relationship('Template', backref=db.backref("user_templates", cascade="all,delete"))


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

  def __init__(self, name="", help="", storage="", is_public=True, is_crowdsourced=False, is_moderated=True, is_listed=True, created=datetime.utcnow(), status=True):
    self.name = name
    self.help = help
    self.storage = storage
    self.is_public = is_public
    self.is_crowdsourced = is_crowdsourced
    self.is_moderated = is_moderated
    self.is_listed = is_listed
    self.created = created
    self.status = status


  """
  Create a new Template in the CommonsCloudAPI

  @param (object) self

  @param (dictionary) application_content
      The content that is being submitted by the user
  """
  def template_create(self, request_object):

    """
    Make sure we can use the request data as json
    """
    content_ = json.loads(request_object.data)

    """
    Part 1: Add the new application to the database
    """
    new_template = {
      'name': sanitize.sanitize_string(content_.get('name', ''))
    }

    template_ = Template(**new_template)

    db.session.add(template_)
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

    self.set_user_template_permissions(template_, permission, current_user)

    return template_


  """
  Get an existing Templates from the CommonsCloudAPI

  @param (object) self

  @param (int) template_id
      The unique ID of the Template to be retrieved from the system

  @return (object) template_
      A fully qualified Template object

  """
  def template_get(self, template_id):

    template_ = Template.query.get(template_id)

    return template_


  """
  Associate a user with a specific template

  @param (object) self

  @param (object) template
      A fully qualified Template object to act on

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
  def set_user_template_permissions(self, template, permission, user):

    """
    Start a new Permission object
    """
    new_permission = UserTemplates(**permission)

    """
    Set the ID of the Template to act upon
    """
    new_permission.template_id = template.id

    """
    Add the new permissions defined with the user defined
    """
    user.templates.append(new_permission)
    db.session.commit()

    return new_permission
