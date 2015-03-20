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
from collections import namedtuple
from functools import partial


"""
Import Flask Dependencies
"""
from flask import current_app

from flask.ext.login import current_user

from flask.ext.principal import identity_loaded
from flask.ext.principal import Permission
from flask.ext.principal import RoleNeed
from flask.ext.principal import UserNeed


"""
Import CommonsCloud Dependencies
"""
from CommonsCloudAPI.extensions import principal

ApplicationNeed = namedtuple('application', ['method', 'value'])

ReadApplicationNeed = partial(ApplicationNeed, 'read')
class ReadApplicationPermission(Permission):
  def __init__(self, application_id):
      need = ReadApplicationNeed(unicode(application_id))
      super(ReadApplicationPermission, self).__init__(need)

WriteApplicationNeed = partial(ApplicationNeed, 'write')
class WriteApplicationPermission(Permission):
  def __init__(self, application_id):
      need = WriteApplicationNeed(unicode(application_id))
      super(WriteApplicationPermission, self).__init__(need)


AdminApplicationNeed = partial(ApplicationNeed, 'admin')
class AdminApplicationPermission(Permission):
  def __init__(self, application_id):
      need = AdminApplicationNeed(unicode(application_id))
      super(AdminApplicationPermission, self).__init__(need)

