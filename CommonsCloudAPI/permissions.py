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
from flask.ext.security import current_user

from flask.ext.principal import identity_loaded, Permission, RoleNeed, UserNeed


"""
Setup some basic routes to get our application started, even if all
we're showing folks is a 404, 500, or the home page.
"""
def load_identities(app):

  from application.permissions import ViewApplicationNeed, EditApplicationNeed, DeleteApplicationNeed

  @identity_loaded.connect_via(app)
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
          if application.view:
            identity.provides.add(ViewApplicationNeed(application.application_id))
          if application.edit:
            identity.provides.add(EditApplicationNeed(application.application_id))
          if application.delete:
            identity.provides.add(DeleteApplicationNeed(application.application_id))  
