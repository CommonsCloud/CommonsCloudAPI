
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
Import Commons Cloud Dependencies
"""
from CommonsCloudAPI.models.base import CommonsModel

from CommonsCloudAPI.extensions import db
from CommonsCloudAPI.extensions import logger
from CommonsCloudAPI.extensions import sanitize
from CommonsCloudAPI.extensions import status as status_



"""
Define our individual models
"""
class Activity(db.Model, CommonsModel):

    __public__ = ['id', 'name', 'description', 'result', 'created', 'updated', 'status', 'template_id']
    __tablename__ = 'activity'
    __table_args__ = {
        'extend_existing': True
    }

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    result = db.Column(db.Text)
    created = db.Column(db.DateTime)
    updated = db.Column(db.DateTime)
    status = db.Column(db.String(24))
    notify = db.Column(db.Text)
    template_id = db.Column(db.Integer, db.ForeignKey('template.id'))

    def __init__(self, name="", description="", result="", created=datetime.now(), updated=datetime.now(), status=True, notify=[], template_id=""):
        self.name = name
        self.description = description
        self.result = result
        self.created = created
        self.updated = updated
        self.status = status
        self.notify = notify
        self.template_id = template_id

    def activity_get(self, activity_id):
      activity_ = Activity.query.get(activity_id)
      return activity_

    def activity_create(self, request_object):

      if not request_object.data:
        logger.error('No data was submitted with the activity_create request')
        return status_.status_400('You didn\'t include any `data` with your request.'), 400

      """
      Prepare the content of the request_object to use in creating an Activity
      """
      activity = json.loads(request_object.data)

      new_activity = {
        'name': sanitize.sanitize_string(statistic_content.get('name', '')),
        'description': sanitize.sanitize_string(statistic_content.get('description', '')),
        'result': sanitize.sanitize_string(statistic_content.get('result', '')),
        'status': 'pending',
        'template_id': sanitize.sanitize_integer(activity.get('template_id', ''))
      }

      activity_ = Activity(**new_activity)

      db.session.add(activity_)
      db.session.commit()

      return activity_

    def activity_update(self, activity_id, request_object):

      if not request_object.data:
        logger.error('No data was submitted with the activity_create request')
        return status_.status_400('You didn\'t include any `data` with your request.'), 400

      activity_ = self.activity_get(activity_id)

      """
      Prepare the content of the request_object to use in creating an Activity
      """
      activity = json.loads(request_object.data)

      if hasattr(activity_, 'name'):
        activity_.name = sanitize.sanitize_string(activity.get('name', activity_.name))

      if hasattr(activity_, 'description'):
        activity_.description = sanitize.sanitize_string(activity.get('description', activity_.description))

      if hasattr(activity_, 'result'):
        activity_.result = sanitize.sanitize_string(activity.get('result', activity_.result))

      if hasattr(activity_, 'template_id'):
        activity_.template_id = sanitize.sanitize_integer(activity.get('template_id', activity_.template_id))

      if hasattr(activity_, 'status'):
        activity_.status = sanitize.sanitize_boolean(activity.get('status', activity_.status))

      if hasattr(activity_, 'updated'):
        activity_.updated = activity.get('updated', activity_.updated)

      db.session.commit()

      return activity_

    def activity_delete(self, request_object):
      pass

