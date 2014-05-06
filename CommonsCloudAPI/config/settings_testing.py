#
# For CommonsCloud copyright information please see the License document included with
# this software package.
# 
# Licensing information can be found in the LICENSE document (the "License")
# included with this copy of the software and this file may not be used in any
# manner except in compliance with the License
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# 

"""
These environment variables are specific to the Testing enviornment which is currently
Drone.io. The primary thing here is to make sure we aren't setting any specific MongoDB
information, so that the continious integration testing suite can just use what it has.
"""

DEBUG = False

USE_RELOADER = False
  
SQLALCHEMY_DATABASE_URI = 'postgresql://127.0.0.1:5432/commonscloudapi_testing'
