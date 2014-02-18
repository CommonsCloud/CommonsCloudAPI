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
Import Application Dependencies
"""
from CommonsCloudAPI.extensions import db
from CommonsCloudAPI.modules.user.models import User

from . import CommonsTest

"""
Make sure that we can fire up the application, connect to the database,
create all the necessary database tables, and run basic app loading functionality
without any problems.
"""
class UserTest(CommonsTest):

  # def test_user(self):

  #   app = self.app

    # user = User()
    # db.session.add(user)
    # db.session.commit()

    # assert user in db.session

    # response = self.client.get('/')

    # assert user in db.session

  def create_user(self):

    new_user_ = User(**{'email':'admin@commonscloud.org', 'password':'default'})

    db.session.add(new_user_)
    db.session.commit()

    return new_user_


  def login(self, username, password):
    return self.client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)

  def logout(self):
    return self.client.get('/logout', follow_redirects=True)

  def test_login_logout(self):

    print dir(db.session)
    print dir(db.session.registry.registry)
    print db.session.registry
    print db.session.registry.registry

    user = self.create_user()

    # rv = self.login('admin@commonscloud.org', 'default')
    # assert 'You were logged in' in rv.data
    # rv = self.logout()
    # assert 'You were logged out' in rv.data
    # rv = self.login('adminx', 'default')
    # assert 'Invalid username' in rv.data
    # rv = self.login('admin', 'defaultx')
    # assert 'Invalid password' in rv.data


