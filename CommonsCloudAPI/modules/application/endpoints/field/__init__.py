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
from flask import json
from flask import request


"""
Import CommonsCloudAPI Dependencies
"""
from CommonsCloudAPI.extensions import logger
from CommonsCloudAPI.extensions import status as status_

from CommonsCloudAPI.permissions import verify_authorization
from CommonsCloudAPI.permissions import verify_roles

from CommonsCloudAPI.utilities import create_storage_field


"""
Import Data Model

We're importing in this manner so that we can dynamically load these as
Flask-Restless endpoints within our CommonsCloudAPI.create_application method

"""
from CommonsCloudAPI.models.pod import Pod
from CommonsCloudAPI.models.field import Field as Model
from CommonsCloudAPI.models.template import Template

from CommonsCloudAPI.extensions import db


"""
"""
class Seed(Pod):

  """
  Preprocessors
  """
  def preprocessor_get_many(**kw):
    logger.debug('`Application` preprocessor_get_many')
    authorization = verify_authorization()
    role = verify_roles(authorization, ['admin'])

  def preprocessor_get_single(**kw):
    logger.debug('`Application` preprocessor_get_single')
    authorization = verify_authorization()
    role = verify_roles(authorization, ['admin'])

  def preprocessor_put_single(data=None, **kw):
    logger.debug('`Application` preprocessor_put_single')
    authorization = verify_authorization()
    role = verify_roles(authorization, ['admin'])

  def preprocessor_put_many(**kw):
    logger.debug('`Application` preprocessor_put_many')
    authorization = abort(403)

  def preprocessor_patch_single(data=None, **kw):
    logger.debug('`Application` preprocessor_patch_single')
    authorization = verify_authorization()
    role = verify_roles(authorization, ['admin'])

  def preprocessor_patch_many(**kw):
    logger.debug('`Application` preprocessor_patch_many')
    authorization = abort(403)

  def preprocessor_post(data=None, **kw):
    logger.debug('`Application` preprocessor_post')
    authorization = verify_authorization()
    role = verify_roles(authorization, ['admin'])

    """
    Check to ensure we have a `name` field and a `template` at minimum
    so that we aren't orphaning fields or creating unnecessary database
    errors because there's no `name` to name the database column
    """
    if not data.get('name'):
      abort(400, **{
        'description': 'You must include a `name` for your field to be created'
      })
    
    if not data.get('data_type'):
      abort(400, **{
        'description': 'You must include a `data_type` for your field to be\
          created'
      })

    if not data.get('template'):
      abort(400, **{
        'description': 'You must include a `template` array with at least one\
          fully qualified `template` object'
      })
      

  def preprocessor_delete(**kw):
    logger.debug('`Application` preprocessor_delete')
    authorization = verify_authorization()
    role = verify_roles(authorization, ['admin'])


  """
  Postprocessors
  """
  def field_postprocessor_post(result=None, **kwargs):

    """
    Now that we have all of the pieces we need, we can create the column in the
    appropriate data base table.
    """
    field_response = create_storage_field(result)

    """
    Make sure that all this new information gets saved back to the Field object
    """
    updated_field = Model.query.get(result.get('id'))
    updated_field.association = field_response.get('association')
    db.session.commit()

    """
    Make sure the `assocaition` field is filled in prior to dislaying the
    Response back to the user
    """
    result['association'] = field_response.get('association')


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
    },
    'postprocessors': {
      'POST': [field_postprocessor_post]
    }
  }

  Pod.__arguments__.update(**__model_arguments__)


