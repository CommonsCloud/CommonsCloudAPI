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

import logging


"""
Import Flask Dependencies
"""
from flask.ext.security import Security
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail
from flask.ext.oauthlib.provider import OAuth2Provider
from flask.ext.principal import Principal

from CommonsCloudAPI.utilities.sanitize import CommonsSanitize
from CommonsCloudAPI.utilities.statuses import CommonsStatus


"""
Flask Dependencies 
"""
db = SQLAlchemy()
security = Security()
mail = Mail()
oauth = OAuth2Provider()
principal = Principal()
status = CommonsStatus()
sanitize = CommonsSanitize()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)