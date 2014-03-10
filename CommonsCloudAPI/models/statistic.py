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
    templates = db.relationship('TemplateStatistics', backref=db.backref('template'))
    field = db.relationship('StatisticField', backref=db.backref('field'))

    def __init__(self, name="", units="", function="SUM", created=datetime.now(), status=True, templates=[], field=[]):
        self.name = name
        self.units = units
        self.function = function
        self.created = created
        self.status = status
        self.templates = templates
        self.field = field
