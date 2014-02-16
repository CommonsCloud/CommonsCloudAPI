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
Import System/Python Dependencies
"""
import os
import unittest

from CommonsCloudAPI import create_application


"""
Make sure that we can fire up the application, connect to the database,
create all the necessary database tables, and run basic app loading functionality
without any problems.
"""
class CommonsTestCase(unittest.TestCase):

    def setUp(self):
      self.app = create_application(__name__, env='testing')


if __name__ == '__main__':
    unittest.main()