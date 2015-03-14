
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


"""
Import Commons Cloud Dependencies
"""
from CommonsCloudAPI.models.base import CommonsModel
from CommonsCloudAPI.models.template import Template
from CommonsCloudAPI.models.field import Field

from CommonsCloudAPI.extensions import db
from CommonsCloudAPI.extensions import logger
from CommonsCloudAPI.extensions import sanitize
from CommonsCloudAPI.extensions import status as status_



"""
Define our individual models
"""
class Statistic(db.Model, CommonsModel):

    __public__ = {'default': ['id', 'name', 'units', 'function', 'created', 'status', 'field_id']}
    __tablename__ = 'statistic'
    __table_args__ = {
        'extend_existing': True
    }

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    units = db.Column(db.String(24))
    function = db.Column(db.String(24))
    created = db.Column(db.DateTime)
    status = db.Column(db.Boolean)
    field_id = db.Column(db.Integer, db.ForeignKey('field.id'))

    def __init__(self, name="", units="", function="SUM", created=datetime.now(), status=True, field_id=""):
        self.name = name
        self.units = units
        self.function = function
        self.created = created
        self.status = status
        self.field_id = field_id


    """
    Create a new statistic in the CommonsCloudAPI

    @param (object) self

    @param (dictionary) request_object
      The content that is being submitted by the user
    """
    def statistic_create(self, template_id, request_object):

        """
        Make sure that some data was submitted before proceeding
        """
        if not request_object.data:
          logger.error('User %d new Statistic request failed because they didn\'t submit any `data` with their request', \
              self.current_user.id)
          return status_.status_400('You didn\'t include any `data` with your request.'), 400

        """
        Make sure we can use the request data as json
        """
        statistic_content = json.loads(request_object.data)

        field_id = sanitize.sanitize_integer(statistic_content.get('field_id', ''))

        explicitly_allowed_fields_ = self.explicitly_allowed_fields()
        template_fields_ = self.template_field_list(template_id)
        if not field_id in explicitly_allowed_fields_ or \
              not field_id in template_fields_:
          logger.error('User %d new Statistic request failed because they are\'t allowed to modify the associated field', \
              self.current_user.id)
          return status_.status_400('You are\'t allowed to modify the field you\'re trying to add a statistic to'), 400

        new_statistic = {
          'name': sanitize.sanitize_string(statistic_content.get('name', '')),
          'units': sanitize.sanitize_string(statistic_content.get('units', '')),
          'function': sanitize.sanitize_string(statistic_content.get('function', '')),
          'field_id': field_id
        }

        statistic_ = Statistic(**new_statistic)

        db.session.add(statistic_)
        db.session.commit()

        return statistic_


    def statistic_get(self, template_id, statistic_id):

        explicitly_allowed_templates_ = self.explicitly_allowed_templates('is_admin')
        if not template_id in explicitly_allowed_templates_:
          logger.error('User %d view Statistic request failed because they are\'t allowed to admin the template', \
              self.current_user.id)
          return status_.status_401('You are\'t allowed to view this statistic'), 401

        statistic_ = Statistic.query.get(statistic_id)

        return statistic_



    def statistic_list(self, template_id):

        explicitly_allowed_fields_ = self.explicitly_allowed_fields()
        template_fields_ = self.template_field_list(template_id)

        field_id_list_ = set(explicitly_allowed_fields_) & set(template_fields_)

        statistics_ = Statistic.query.filter(Statistic.field_id.in_(field_id_list_)).all()

        return statistics_

    """
    Update an existing statistic in the CommonsCloudAPI

    @param (object) self

    @param (dictionary) request_object
      The content that is being submitted by the user
    """
    def statistic_update(self, template_id, statistic_id, request_object):

        explicitly_allowed_templates_ = self.explicitly_allowed_templates()
        if not template_id in explicitly_allowed_templates_:
          logger.error('User %d update Statistic request failed because they are\'t allowed to modify the associated Template', \
              self.current_user.id)
          return status_.status_401('You are\'t allowed to modify the Template you\'re trying to add a statistic to'), 401

        """
        Make sure that some data was submitted before proceeding
        """
        if not request_object.data:
          logger.error('User %d update Statistic request failed because they didn\'t submit any `data` with their request', \
              self.current_user.id)
          return status_.status_400('You didn\'t include any `data` with your request.'), 400

        """
        Make sure we can use the request data as json
        """
        statistic_ = Statistic.query.get(statistic_id)

        if not statistic_.id:
          logger.error('User %d Statistic request failed because Statistic does\'t exist', \
              self.current_user.id)
          return status_.status_404('The Statistic you\'re looking for doesn\'t exist'), 404

        statistic_content = json.loads(request_object.data)

        if hasattr(statistic_, 'name'):
          statistic_.name = sanitize.sanitize_string(statistic_content.get('name', statistic_.name))

        if hasattr(statistic_, 'units'):
          statistic_.units = sanitize.sanitize_string(statistic_content.get('units', statistic_.units))

        if hasattr(statistic_, 'function'):
          statistic_.function = sanitize.sanitize_string(statistic_content.get('function', statistic_.function))

        if hasattr(statistic_, 'field_id'):
          statistic_.field_id = sanitize.sanitize_integer(statistic_content.get('field_id', statistic_.field_id))

        if hasattr(statistic_, 'status'):
          statistic_.status = sanitize.sanitize_boolean(statistic_content.get('status', statistic_.status))

        db.session.commit()

        return statistic_



    """
    Delete an existing Statistic from the CommonsCloudAPI

    @param (object) self

    @param (int) statistic_id
        The unique ID of the Statistic to be retrieved from the system

    @return (bool)
        A boolean to indicate if the deletion was succesful

    """
    def statistic_delete(self, template_id, statistic_id):

        explicitly_allowed_templates_ = self.explicitly_allowed_templates()
        if not template_id in explicitly_allowed_templates_:
          logger.error('User %d delete Statistic request failed because they are\'t allowed to modify the associated Template', \
              self.current_user.id)
          return status_.status_401('You are\'t allowed to modify the Template you\'re trying to add a statistic to'), 401

        statistic_ = Statistic.query.get(statistic_id)

        if not statistic_.id:
          logger.error('User %d delete Statistic request failed because Statistic does\'t exist', \
              self.current_user.id)
          return status_.status_404('The Statistic you\'re looking for doesn\'t exist'), 404

        db.session.delete(statistic_)
        db.session.commit()

        return True


    """
    Get a list of template ids from the current user and convert
    them into a list of numbers so that our SQLAlchemy query can
    understand what's going on
    """
    def explicitly_allowed_templates(self, permission_type='read'):

        templates_ = []

        if not hasattr(self.current_user, 'id'):
          logger.warning('User did\'t submit their information %s', \
              self.current_user)
          return status_.status_401('You need to be logged in to access applications'), 401

        for template in self.current_user.templates:
          if permission_type and getattr(template, permission_type):
            templates_.append(template.template_id)

        return templates_


    """
    Get a list of template ids from the current user and convert
    them into a list of numbers so that our SQLAlchemy query can
    understand what's going on
    """
    def explicitly_allowed_fields(self, permission_type='write'):

        fields_ = []

        if not hasattr(self.current_user, 'id'):
          logger.warning('User did\'t submit their information %s', \
              self.current_user)
          return status_.status_401('You need to be logged in to access applications'), 401

        for field in self.current_user.fields:
          if permission_type and getattr(field, permission_type):
            fields_.append(field.field_id)

        return fields_

    def template_field_list(self, template_id):

        template_ = Template.query.get(template_id)

        fields_ = []

        for field_ in template_.fields:
            fields_.append(field_.id)

        return fields_


