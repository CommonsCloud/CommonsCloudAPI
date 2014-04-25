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

from CommonsCloudAPI.extensions import db
from CommonsCloudAPI.extensions import sanitize



"""
Define our individual models
"""
class Statistic(db.Model, CommonsModel):

    __public__ = ['id', 'name', 'units', 'function', 'created', 'status']
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
    def statistic_create(self, request_object):

        """
        Make sure we can use the request data as json
        """
        statistic_content = json.loads(request_object.data)


        if not statistic_content.get('field_id', ''):
            return abort(400, 'A Field ID is required to create a statistic')

        """
        Part 1: Add the new application to the database
        """
        new_statistic = {
          'name': sanitize.sanitize_string(statistic_content.get('name', '')),
          'units': sanitize.sanitize_string(statistic_content.get('units', '')),
          'function': sanitize.sanitize_string(statistic_content.get('function', '')),
          'field_id': statistic_content.get('field_id', '')
        }

        statistic_ = Statistic(**new_statistic)

        db.session.add(statistic_)
        db.session.commit()

        return statistic_


   def statistic_get(self, statistic_id):

    statistic_ = Statistic.query.get(statistic_id)

    if not hasattr(statistic_, 'id'):
      return abort(404)

    return statistic_



    def statistic_list(self, template_id):

        """
        Get a list of the applications the current user has access to
        and load their information from the database
        """
        statistic_id_list_ = self.statistic_id_list(template_id)
        statistics_ = Statistic.query.filter(Statistic.id.in_(statistic_id_list)).all()

        return statistics_


    """
    Update an existing statistic in the CommonsCloudAPI

    @param (object) self

    @param (dictionary) request_object
      The content that is being submitted by the user
    """
    def statistic_update(self, statistic_id, request_object):

        """
        Make sure we can use the request data as json
        """
        statistic_ = Statistic.query.get(statistic_id)
        statistic_content = json.loads(request_object.data)

        """
        Part 2: Update the fields that we have data for
        """
        if hasattr(statistic_, 'name'):
          statistic_.name = sanitize.sanitize_string(statistic_content.get('name', statistic_.name))

        if hasattr(statistic_, 'units'):
          statistic_.units = sanitize.sanitize_string(statistic_content.get('units', statistic_.units))

        if hasattr(statistic_, 'function'):
          statistic_.function = sanitize.sanitize_string(statistic_content.get('function', statistic_.function))

        if hasattr(statistic_, 'field_id'):
          statistic_.field_id = statistic_content.get('field_id', statistic_.field_id)

        if hasattr(statistic_, 'status'):
          statistic_.status = statistic_content.get('status', statistic_.status)


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
    def statistic_delete(self, statistic_id):

        statistic_ = Statistic.query.get(statistic_id)
        db.session.delete(statistic_)
        db.session.commit()

        return True


    def statistic_id_list(self, template_id):

        template_ = Template.query.get(template_id)

        fields_ = []

        for field_ in template_.fields:
            fields.append(field_.id)

        return fields_

