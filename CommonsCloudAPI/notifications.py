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

import json

from flask import abort
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
  application = db.Column(db.Integer, db.ForeignKey('application.id'))
  conditions = db.relationship('Condition', backref=db.backref('notification'), cascade="all,delete")
  actions = db.relationship('Action', backref=db.backref('notification'), cascade="all,delete")


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
  notification_id = db.Column(db.Integer, db.ForeignKey('notification.id'))

"""
Actions are what actually happens after Notifications are triggered and all
Conditions have been met.

One kind of weird part of the Actions is that we can really pre-define all of
the possibilities for specific options that need to be attached to an Action in
order to fully execute it. Below is an example of the options for the 
`send_email` Action.

Example: Uses a static email recipient

  options = {
    "send_email": {
      "sender": "WaterReporter <reporter@waterreporter.org>",
      "recipients": {
        "type": "static",
        "value": "administrator@commonscloud.org"
      },
      "subject": "A report was submitted",
      "data": data,
      "template": "commoncloud_default",
    }
  }

Example: Uses a dyanmic email list collected from another table in the database
and uses a specific field, sending an email to all email addresses found

  options = {
    "send_email": {
      "sender": "WaterReporter <reporter@waterreporter.org>",
      "recipients": {
        "type": "dynamic",
        "value": "",
        "from_storage": "type_fa0ce31fe87a45c8836e0188c3674ff3",
        "field": "email",
        "conditions": ""
      },
      "subject": "Your report was submitted",
      "data": data,
      "template": "waterreporter_citizen",
    }
  }

Example: Much like the previous one, this example filters down the list of
email address based on a condition, in this case a predefined option called
geometry_intersects. This will use the acting storage type `data.storage`'s
geometry field (i.e., type_2c1bd72acccf416aada3a6824731acc9.geometry) and
check to see if it intersects with the options.send_email.recipients.from_storage
value's geometry field (i.e., type_fa0ce31fe87a45c8836e0188c3674ff3.geometry)

  options = {
    "send_email": {
      "sender": "WaterReporter <reporter@waterreporter.org>",
      "recipients": {
        "type": "dynamic",
        "value": "",
        "from_storage": "type_fa0ce31fe87a45c8836e0188c3674ff3",
        "field": "email",
        "conditions": "geometry_intersects"
      },
      "subject": "Your report was submitted",
      "data": data,
      "template": "waterreporter_citizen"
    }
  }

"""
class Action(db.Model):

  __tablename__ = 'action'
  __table_args__ = {
    'extend_existing': True
  }

  id = db.Column(db.Integer, primary_key=True)
  label = db.Column(db.String(255))
  action = db.Column(db.String(255)) # send_notification_email, etc. An actual python method would be preferrable
  options = db.Column(db.Text)
  notification_id = db.Column(db.Integer, db.ForeignKey('notification.id'))


def execute_notification(signal_type, app, **data):

  # 1. Get a list of Notifications that match the `signal_type`
  # logger.debug('data %s', dir(data))
  notifications = Notification.query.all()

  # 2. Loop over Notifications 
  for notification in notifications:
    # logger.debug('Notification %s %s', notification.id, notification.label)

    # 3. Get all conditions that match this Notification
    # logger.debug('Conditions %s', notification.conditions)

    # 4. Loop over conditions and execute each
    should_execute_actions = execute_conditions(notification.conditions, **data)
    # logger.debug('Should we execute the actions? %s', 
    #     str(should_execute_actions))

    # 5. If ALL return true, then get all Actions matching this Notification
    if should_execute_actions:

      # logger.debug('Actions %s', notification.actions)

      # 6. Loop over Actions and execute each
      execute_actions(notification.actions, **data)

  # 7. Else just exit
  return {}


def execute_conditions(conditions, **data):

  result_list = []

  for condition in conditions:
    # logger.debug('Condition %s', condition.label)

    if 'storage' in condition.name:
      # logger.debug('Condition for Storage Type is executing now')
      result_list.append(condition_storage_type(condition.value, **data))
  
  # logger.debug('Condition Results %s', result_list)

  for result in result_list:
    if not result:
      return False

  return True


def condition_storage_type(required_value, **data):

  # logger.debug('condition_storage_type > %s should match %s', 
  #     required_value, data.get('storage', None))

  if required_value in data.get('storage', None):
    return True

  return False


def execute_actions(actions, **data):

  for action in actions:
    # logger.debug('Action <%s> %s', action.action, action.label)

    if 'send_email' in action.action:

      # logger.debug('Executing Action > send_email')
      defaults = json.loads(action.options)
      send_email = defaults.get('send_email', None)
      recipients = send_email.get('recipients', None)

      if 'dynamic' in recipients.get('type', None) and \
            recipients.get('from_storage', None):
          feature = data.get('feature', None)
          recipients_list = fetch_dynamic_recipients(feature, **recipients)

          if recipients_list is None:
            recipient_data = []
            recipients_emailaddresses = []
          else:
            recipient_data = recipients_list.get('recipients', None)
            # logger.debug('XXXXX recipient_data %s', recipient_data)

            recipients_emailaddresses = recipients_list.get('email_addresses', ['error@commonscloud.org'])
            # logger.debug('XXXXX email_addresses %s', recipients_emailaddresses)
          

          copy = recipients.get('copy', False)
          if copy:
            this_field = copy.get('field', None)
            user_email = getattr(feature, this_field, 'error@commonscloud.org')
            copy_sender = [user_email]
            copy_template = copy.get('template', None)
            copy_subject = copy.get('subject', None)
      else:
        recipients_emailaddresses = [recipients.get('value', ['error@commonscloud.org'])]
        recipient_data = []
        copy_sender = None
        copy_template = None
        copy_subject = None


      options = {
        "subject": send_email.get('subject', None),
        "recipients_emailaddresses": recipients_emailaddresses,
        "sender": send_email.get('sender', None),
        "template": send_email.get('template', None),
        "data": data,
        "recipient_data": recipient_data,
        "copy": {
          "email_address": copy_sender,
          "template": copy_template,
          "subject": copy_subject
        }
      }

      send_notification_email(**options)


def fetch_dynamic_recipients(feature, **options):

  from CommonsCloudAPI.models.feature import Feature

  if 'geometry_intersects' in options.get('conditions', None):

    # logger.debug('Geometry %s', feature.geometry)

    if feature.geometry is None:
      return

    Feature_ = Feature()
    intersection_options = {
      "storage_": options.get('from_storage', None),
      "geometry": feature.geometry
    }
    features = Feature_.feature_get_intersection(**intersection_options)

    # logger.debug('features from get intersects %s', features)

  """
  Create the recipients list
  """
  email_addresses = []

  if features:
    field = options.get('field', None)
    # logger.debug('features %s', dir(features))
    for feature in features:
      # logger.debug('Adding recipient %s', getattr(feature, field))
      email_addresses.append(getattr(feature, field))


  if not len(email_addresses):
    email_addresses.append('error@commonscloud.org')


  # logger.debug('email_addresses %s, %s', len(email_addresses), email_addresses)


  # logger.debug('Dynamic recipient list %s', email_addresses)
  
  return {
    "recipients": features,
    "email_addresses": email_addresses
  }


"""
Send an email notification

subject (str)
recipients_emailaddresses (list)
sender (str) "FirstName LastName <email@address.com>"
template (str) Defines the html/txt template's to be used
context (kwargs) Dictionary of data or anything else you need passed along

"""
def send_notification_email(subject, recipients_emailaddresses, sender, template, copy, **context):
    """Send an email via the Flask-Mail extension.

    :param subject: Email subject
    :param recipient: Email recipient
    :param template: The name of the email template
    :param context: The context to render the template with
    """
    msg = Message(subject, sender=sender, recipients=recipients_emailaddresses)

    ctx = ('notifications', template)
    msg.body = render_template('%s/%s.txt' % ctx, **context)
    msg.html = render_template('%s/%s.html' % ctx, **context)

    mail = current_app.extensions.get('mail')
    mail.send(msg)

    if copy.get('email_address', None):
      copy_msg = Message(copy.get('subject', None), sender=sender, recipients=copy.get('email_address', None))
      copy_ctx = ('notifications', copy.get('template', None))
      copy_msg.body = render_template('%s/%s.txt' % copy_ctx, **context)
      copy_msg.html = render_template('%s/%s.html' % copy_ctx, **context)

      copy_mail = current_app.extensions.get('mail')
      copy_mail.send(copy_msg)
