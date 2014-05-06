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
from flask.ext.testing import TestCase


"""
Import Application Dependencies
"""
from CommonsCloudAPI import create_application

from CommonsCloudAPI.extensions import db


"""
Make sure that we can fire up the application, connect to the database,
create all the necessary database tables, and run basic app loading functionality
without any problems.
"""
class CommonsTest(TestCase):

  def create_app(self):
    app = create_application(__name__, env='testing')
    app.config['TESTING'] = True
    return app

  def setUp(self):
    self.app = self.create_app()
    db.create_all()

  # def tearDown(self):
  #   db.session.remove()
  #   db.drop_all()

