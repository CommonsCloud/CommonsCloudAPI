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

from flask.ext.security import current_user

from flask.ext.principal import identity_loaded, Permission, RoleNeed, UserNeed


ApplicationNeed = namedtuple('application', ['method', 'value'])


ViewApplicationNeed = partial(ApplicationNeed, 'view')
class ViewApplicationPermission(Permission):
    def __init__(self, application_id):
        need = ViewApplicationNeed(unicode(application_id))
        super(ViewApplicationPermission, self).__init__(need)


EditApplicationNeed = partial(ApplicationNeed, 'edit')
class EditApplicationPermission(Permission):
    def __init__(self, application_id):
        need = EditApplicationNeed(unicode(application_id))
        super(EditApplicationPermission, self).__init__(need)


DeleteApplicationNeed = partial(ApplicationNeed, 'delete')
class DeleteApplicationPermission(Permission):
    def __init__(self, post_id):
        need = DeleteApplicationNeed(unicode(application_id))
        super(DeleteApplicationPermission, self).__init__(need)


@identity_loaded.connect_via(current_app)
def on_identity_loaded(sender, identity):
    # Set the identity user object
    identity.user = current_user

    # Add the UserNeed to the identity
    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(current_user.id))

    # Assuming the User model has a list of roles, update the
    # identity with the roles that the user provides
    if hasattr(current_user, 'roles'):
        for role in current_user.roles:
            identity.provides.add(RoleNeed(role.name))

    # Assuming the User model has a list of posts the user
    # has authored, add the needs to the identity
    if hasattr(current_user, 'applications'):
        for application in current_user.applications:
          print 'application.view', application.view
          if application.view:
            identity.provides.add(ViewApplicationNeed(unicode(application.application)))
          print 'application.edit', application.edit
          if application.edit:
            identity.provides.add(EditApplicationNeed(unicode(application.application)))
          print 'application.delete', application.delete
          if application.delete:
            identity.provides.add(DeleteApplicationNeed(unicode(application.application)))


