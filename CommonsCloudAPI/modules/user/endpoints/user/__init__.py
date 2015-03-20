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

from flask import json
from flask import request


"""
Import CommonsCloudAPI Dependencies
"""
from CommonsCloudAPI.extensions import logger

from CommonsCloudAPI.permissions import verify_authorization
from CommonsCloudAPI.permissions import verify_roles

from flask.ext.security import current_user
from flask.ext.security.confirmable import generate_confirmation_link
from flask.ext.security.utils import send_mail, config_value, url_for_security
from flask.ext.security.recoverable import generate_reset_password_token

"""
Import Data Model

We're importing in this manner so that we can dynamically load these as
Flask-Restless endpoints within our CommonsCloudAPI.create_application method

"""
from CommonsCloudAPI.models.pod import Pod
from CommonsCloudAPI.models.user import User as Model

from CommonsCloudAPI.extensions import db


"""
"""
class Seed(Pod):

  """
  Preprocessors
  """
  def preprocessor_get_many(**kw):
    logger.debug('`User` preprocessor_get_many')
    authorization = verify_authorization()
    role = verify_roles(authorization, ['admin'])

  def preprocessor_get_single(**kw):
    logger.debug('`User` preprocessor_get_single')
    authorization = verify_authorization()
    role = verify_roles(authorization, ['admin'])

  def preprocessor_put_single(data=None, **kw):
    logger.debug('`User` preprocessor_put_single')
    authorization = verify_authorization()
    role = verify_roles(authorization, ['admin'])

  def preprocessor_put_many(**kw):
    logger.debug('`User` preprocessor_put_many')
    authorization = abort(403)

  def preprocessor_patch_single(data=None, **kw):
    logger.debug('`User` preprocessor_patch_single')
    authorization = verify_authorization()
    role = verify_roles(authorization, ['admin'])

  def preprocessor_patch_many(**kw):
    logger.debug('`User` preprocessor_patch_many')
    authorization = abort(403)

  def preprocessor_post(data=None, **kw):
    logger.debug('`User` preprocessor_post')
    authorization = verify_authorization()
    role = verify_roles(authorization, ['admin'])

  def preprocessor_delete(**kw):
    logger.debug('`User` preprocessor_delete')
    authorization = verify_authorization()
    role = verify_roles(authorization, ['admin'])


  """
  Postprocessors
  """
  def user_postprocessor_get_single(result=None, **kw):
    logger.debug('`User` user_postprocessor_get_single')

    """
    The `User` list object here is useless, so just get rid of it, prior to
    displaying the permission results to the `User`
    """
    for index, feature in enumerate(result.get('objects')):
      del result.get('objects')[index]['users']

  def user_postprocessor_post(result=None, **kw):
    logger.debug('`User` user_postprocessor_post')
    authorization = verify_authorization()
    role = verify_roles(authorization, ['admin'])

    """
    HACK: We really shouldn't be doing this, however, it's quicker and
          more straight forward than converting the <dict> to enable
          dot sytnax that is compatible with Flask-Security

    """
    user = db.session.query(Model).get(result['id'])

    """
    Sends the reset password instructions email for the specified user.
    
    :param user: The user to send the instructions to
    
    """
    token = generate_reset_password_token(user)
    reset_link = url_for_security('reset_password', token=token, _external=True)

    send_mail('A account has been added for you', user.email,
              'welcome', user=user, confirmation_link=reset_link)

    """
    Cache the user's Gravatar image within our database table
    """
    modified_user = db.session.query(Model).get(result['id'])
    gravatar_url = modified_user.user_picture(modified_user.email)

    modified_user.picture = gravatar_url

    db.session.add(modified_user)
    db.session.commit()

  def user_postprocessor_patch_single(result=None, **kw):

    """
    Cache the user's Gravatar image within our database table
    """
    modified_user = db.session.query(Model).get(result['id'])
    gravatar_url = modified_user.user_picture(modified_user.email)

    modified_user.picture = gravatar_url

    db.session.add(modified_user)
    db.session.commit()

  def user_postprocessor_put_single(result=None, **kw):

    """
    Cache the user's Gravatar image within our database table
    """
    modified_user = db.session.query(Model).get(result['id'])
    gravatar_url = modified_user.user_picture(modified_user.email)

    modified_user.picture = gravatar_url

    db.session.add(modified_user)
    db.session.commit()

  """
  Flask-Restless Endpoint Arguments

  Flask-Restless gives us access to a variety of different arguments so developers
  can customize our endpoint. Within the API we have pre-defined arguments so that
  our system acts as we need it to. These pre-defined arguments can be found in the
  Parent `Pod` data model in the `CommonsCloudAPI/models/pod.py` file defined in that
  model as the `__arguments__` dictionary.

  Here in our individual Models we can update these preset arguments by defining a
  new dictionary defining our keyword arguments and then passing them to an update
  function on the Parent Pod.__arguments__ dictionary.

  Updating these arguments within this `endpoint` file only affects `this` endpoint
  file. For instance if you have a `name` field that you `exclude_columns` and then
  you have a `name` field in another model, these settings won't affect the other
  model, leaving the other models `name` field displayed.

  @see https://flask-restless.readthedocs.org/en/latest/customizing.html
     For more informaction on the keywords available to custom the model

  @see https://docs.python.org/2/library/stdtypes.html#dict.update
     For more information on the correct way to `update` a Parent dictionary
  """
  __model_arguments__ = {
    "exclude_columns": [
      'password'
    ],
    'preprocessors': {
      'GET_SINGLE': [preprocessor_get_single],
      'GET_MANY': [preprocessor_get_many],
      'PUT_SINGLE': [preprocessor_put_single],
      'PUT_MANY': [preprocessor_put_many],
      'PATCH_SINGLE': [preprocessor_patch_single],
      'PATCH_MANY': [preprocessor_patch_many],
      'POST': [preprocessor_post],
      'DELETE': [preprocessor_delete]
    },
    'postprocessors': {
      'GET_SINGLE': [user_postprocessor_get_single],
      'POST': [user_postprocessor_post],
      'PATCH_SINGLE': [user_postprocessor_patch_single],
      'PUT_SINGLE': [user_postprocessor_put_single]
    }
  }

  Pod.__arguments__.update(**__model_arguments__)


