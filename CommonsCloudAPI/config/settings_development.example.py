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

DEBUG = True

SQLALCHEMY_DATABASE_URI = 'postgresql://127.0.0.1:5432/commonscloudapi_development'

FILE_ATTACHMENTS_DIRECTORY = '/path/to/upoads'

OAUTH1_PROVIDER_ENFORCE_SSL = False

# Flask-Mail
MAIL_SERVER = 'smtp.mandrillapp.com'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USERNAME = 'username'
MAIL_PASSWORD = 'password'
DEFAULT_MAIL_SENDER = 'support@commonscloud.org'