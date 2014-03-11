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

from flask.ext.security import current_user


"""
Import Commons Cloud Dependencies
"""
from CommonsCloudAPI.models.base import CommonsModel

from CommonsCloudAPI.extensions import db
from CommonsCloudAPI.extensions import sanitize
from CommonsCloudAPI.extensions import status as status_

from CommonsCloudAPI.models.field import Field


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


    """
    Delete an existing Statistic from the CommonsCloudAPI

    @param (object) self

    @param (int) statistic_id
        The unique ID of the Field to be retrieved from the system

    @return (bool)
        A boolean to indicate if the deletion was succesful

    """
    def statistic_delete(self, statistic_id):

        statistic_ = Statistic.query.get(statistic_id)
        db.session.delete(statistic_)
        db.session.commit()

        return True