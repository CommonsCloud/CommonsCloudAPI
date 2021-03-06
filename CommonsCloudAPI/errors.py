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
Import Flask dependencies
"""

from werkzeug.exceptions import BadRequestKeyError

from flask import render_template

from CommonsCloudAPI.extensions import logger
from CommonsCloudAPI.extensions import status as status_

from oauthlib.oauth2 import InvalidScopeError


"""
Setup some basic routes to get our application started, even if all
we're showing folks is a 404, 500, or the home page.
"""
def load_errorhandlers(app):

  """
  If a user would happen to arrive at a deadend within the system, we should at least give
  them a little feedback. These should get better over time, but for now we can at least make
  it look like they aren't completely leaving the system and lost with default server error pages.
  """
  @app.errorhandler(400)
  def internal_error(error):
    logger.error('Error 400, %s', error)
    logger.exception(error)
    return status_.status_400(), 400

  @app.errorhandler(401)
  def internal_error(error):
    logger.error('Error 401, %s', error)
    logger.exception(error)
    return status_.status_401(), 401

  @app.errorhandler(403)
  def internal_error(error):
    logger.error('Error 403, %s', error)
    logger.exception(error)
    return status_.status_403(), 403

  @app.errorhandler(404)
  def internal_error(error):
    logger.error('Error 404, %s', error)
    logger.exception(error)
    return status_.status_404(), 404

  @app.errorhandler(405)
  def internal_error(error):
    logger.error('Error 405, %s', error)
    logger.exception(error)
    return status_.status_405(), 405

  @app.errorhandler(BadRequestKeyError)
  def internal_error(error):
    logger.error('BadRequestKeyError, %s', error)
    logger.exception(error)
    return status_.status_400(), 400

  @app.errorhandler(InvalidScopeError)
  def internal_error(error):
    logger.error('InvalidScopeError, %s', error)
    logger.exception(error)
    return status_.status_500('Your OAuth Scopes don\'t match the ones specified for your application'), 500

  @app.errorhandler(500)
  @app.errorhandler(Exception)
  def internal_error(error):
    logger.error('Error 500, %s', error)
    logger.exception(error)
    return status_.status_500(error), 500
  
