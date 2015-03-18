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
Import Flask Dependencies
"""
from flask import abort


"""
Import CommonsCloudAPI Dependencies
"""
from CommonsCloudAPI.extensions import logger

from CommonsCloudAPI.permissions import verify_authorization
from CommonsCloudAPI.permissions import verify_roles

from CommonsCloudAPI.utilities import create_storage


"""
Import Data Model

We're importing in this manner so that we can dynamically load these as
Flask-Restless endpoints within our CommonsCloudAPI.create_application method

"""
from CommonsCloudAPI.models.pod import Pod
from CommonsCloudAPI.models.template import Template as Model


"""
"""
class Seed(Pod):

  """
  Preprocessors
  """
  def preprocessor_get_many(**kwargs):
    logger.debug('`Template` preprocessor_get_many')

    """
    A giant list of `Template` objects is not useful outside of `Application`
    context, therefore, this endpoint has been disabled. If the developer
    wishes to access a list of `Template` objects specific to their
    `Application` they will need to use the following endpoint:

        `application/<int:application_id>/templates`

    """
    authorization = abort(404, 'The endpoint you are looking for is incorrect, please try your request again using the `application/<int:application_id>/templates` endpoint')

  def preprocessor_get_single(**kwargs):
    logger.debug('`Template` preprocessor_get_single')
    authorization = verify_authorization()
    role = verify_roles(authorization, ['admin'])

  def preprocessor_put_single(data=None, **kwargs):
    logger.debug('`Template` preprocessor_put_single')
    authorization = verify_authorization()
    role = verify_roles(authorization, ['admin'])

  def preprocessor_put_many(**kwargs):
    logger.debug('`Template` preprocessor_put_many')
    authorization = abort(403)

  def preprocessor_patch_single(data=None, **kwargs):
    logger.debug('`Template` preprocessor_patch_single')
    authorization = verify_authorization()
    role = verify_roles(authorization, ['admin'])

  def preprocessor_patch_many(**kwargs):
    logger.debug('`Template` preprocessor_patch_many')
    authorization = abort(403)

  def preprocessor_post(data=None, **kwargs):
    logger.debug('`Template` preprocessor_post')
    authorization = verify_authorization()
    role = verify_roles(authorization, ['admin'])

    """
    A `name` field is required to create an `Application`
    """
    if not data.get('name'):
      abort(400, **{
        'description': 'You must include a `name` for your field to be created'
      })

    if not data.get('application'):
      abort(400, **{
        'description': 'You must include an `application` array with at least \
          one fully qualified `application` object'
      })

    """
    All Templates must have a storage mechanism and it must be attached to the
    CommonsCloud in the same way that these endpoints are create. So, we must
    create a table on the fly and associate that table with the Template we've
    just created.
    """
    data['storage'] = create_storage()

  def preprocessor_delete(**kwargs):
    logger.debug('`Template` preprocessor_delete')
    authorization = verify_authorization()
    role = verify_roles(authorization, ['admin'])


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
    }
  }

  Pod.__arguments__.update(**__model_arguments__)

