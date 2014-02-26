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
Import System/Python level dependencies
"""
import os
import sys


"""
Import Application specific dependencies
"""
from CommonsCloudAPI import create_application


"""
Start the application

Ensure that the virtual environment has been properly activated and if it
has been, then the application should be run, using the initialize_application
method provided so comply with the Application Factory pattern

"""
if __name__ == "__main__":
  if len(sys.argv) > 1 and sys.argv[1]:

    if sys.argv[1] == 'development':
      os.environ['DEBUG'] = 'true'

    CommonsCloudAPI = create_application(__name__, env=sys.argv[1])
    CommonsCloudAPI.run()
  else:
    CommonsCloudAPI = create_application(__name__)
    CommonsCloudAPI.run()
