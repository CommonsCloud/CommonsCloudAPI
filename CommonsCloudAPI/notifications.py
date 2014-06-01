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

from flask import current_app
from flask import render_template

from CommonsCloudAPI.extensions import db
from CommonsCloudAPI.extensions import logger

from flask.ext.mail import Message


"""
This defines our basic Role model, we have to have this becasue of the
Flask-Security module. If you remove it Flask-Security gets fussy.
"""
class Notification(db.Model):

  __tablename__ = 'notification'
  __table_args__ = {
    'extend_existing': True
  }

  id = db.Column(db.Integer, primary_key=True)
  label = db.Column(db.String(255))
  signal = db.Column(db.String(255))
  conditions = db.relationship('Condition', backref=db.backref("condition", cascade="all,delete"))
  actions = db.relationship('Action', backref=db.backref("action", cascade="all,delete"))


class Condition(db.Model):

  __tablename__ = 'condition'
  __table_args__ = {
    'extend_existing': True
  }

  id = db.Column(db.Integer, primary_key=True)
  label = db.Column(db.String(255))
  name = db.Column(db.String(255))
  operator = db.Column(db.String(255))
  value = db.Column(db.String(255))
  notification = db.Column(db.Integer, db.ForeignKey('notification.id'))


class Action(db.Model):

  __tablename__ = 'action'
  __table_args__ = {
    'extend_existing': True
  }

  id = db.Column(db.Integer, primary_key=True)
  label = db.Column(db.String(255))
  action = db.Column(db.String(255)) # send_notification_email, etc. An actual python method would be preferrable
  options = db.Column(db.Text)
  notification = db.Column(db.Integer, db.ForeignKey('notification.id'))


def execute_notification(signal_type, app, **data):

  # 1. Get a list of Notifications that match the `signal_type`

  # 2. Loop over Notifications 

  # 3. Get all conditions that match this Notification

  # 4. Loop over conditions and execute each

  # 5. If ALL return true, then get all Actions matching this Notification

    # 6. Loop over Actions and execute each

  # 7. Else just exit


  # if hasattr(d) data.storage != 'type_2c1bd72acccf416aada3a6824731acc9':
  #   logger.debug('No notification present for this condition')
  #   return {}

  # logger.debug('Notification Executed from %s, with %s containing data %s', signal_type, app, dir(data))

  # # @todo
  # #
  # # 1. Look through the Notification table's `trigger` column for the
  # #    `signal_type` that we've identified above
  # #
  # # 2. Once Notifications have been found ensure they meet the `condition`
  # #    requirements

  # options = {
  #   "subject": "Your report was submitted",
  #   "recipient": "Joshua Powell <joshua@viableindustries.com>",
  #   "sender": "WaterReporter <report@waterreporter.org>",
  #   "template": 'waterreporter_citizen',
  #   "data": data
  # }

  # send_notification_email(**options)

  return {}

def condition_storage_type(required_value, **data):

  if hasattr(data, storage):

    if required_value in data.storage:
      return True

  return False



"""
Send an email notification

subject (str)
recipients (list)
sender (str) "FirstName LastName <email@address.com>"
template (str) Defines the html/txt template's to be used
context (kwargs) Dictionary of data or anything else you need passed along

"""
def send_notification_email(subject, recipients, sender, template, **context):
    """Send an email via the Flask-Mail extension.

    :param subject: Email subject
    :param recipient: Email recipient
    :param template: The name of the email template
    :param context: The context to render the template with
    """
    msg = Message(subject,
                  sender=sender,
                  recipients=[recipients])

    # setattr(context, feature_details, 'grr')

    ctx = ('notifications', template)
    msg.body = render_template('%s/%s.txt' % ctx, **context)
    msg.html = render_template('%s/%s.html' % ctx, **context)

    mail = current_app.extensions.get('mail')
    mail.send(msg)



