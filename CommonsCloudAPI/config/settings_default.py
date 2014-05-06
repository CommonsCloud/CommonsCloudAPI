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
These configuration variables are not tied to a specific enviornment, we can
consider these the default variables. They can be overriden later on in this
configuration file by any of the other enviornments, these just give us a jump
start on the rest, and ensuring we're being as DRY as possible.
"""  

# Generic settings
DEBUG = False
SECRET_KEY = 'n@11%?-^j!v`oe7MPxM7sx41bqL=QDmfg+U5Ef6@.oYefGUu@`]&bAD5X&U7!B>G'

# Flask-Security
SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'
SECURITY_PASSWORD_SALT = 'd4i<879.Yj}HMPGmB^cLr2(3%&go8JD#b2yFEhT6QpA6Ke+{VaR+n3X4xaHdB734'

SECURITY_CONFIRMABLE = True
SECURITY_REGISTERABLE = True
SECURITY_RECOVERABLE = True
SECURITY_CHANGEABLE = True

SECURITY_CHANGE_URL = '/user/password'

SECURITY_LOGIN_USER_TEMPLATE = 'security/login.html'
SECURITY_RESET_PASSWORD_TEMPLATE = 'security/reset_password.html'
SECURITY_REGISTER_USER_TEMPLATE = 'security/register.html'
SECURITY_FORGOT_PASSWORD_TEMPLATE = 'security/password_forgot.html'

SECURITY_EMAIL_SENDER = 'CommonsCloud Support <support@commonscloud.org>'
SECURITY_EMAIL_SUBJECT_REGISTER = 'Welcome! CommonsCloud needs you to confirm your email address'
SECURITY_EMAIL_SUBJECT_CONFIRM = 'CommonsCloud needs you to confirm your email address'

# OAUTH 1
OAUTH1_PROVIDER_ENFORCE_SSL = True
OAUTH1_PROVIDER_KEY_LENGTH = (10, 100)

# File Attachments
FILE_ATTACHMENTS_ALLOWED_EXTENSIONS = set([
  'txt',
  'rtf'
  'doc',
  'docx',

  'csv',
  'xls',
  'xlsx',

  'pdf',

  'tiff',
  'png',
  'jpg',
  'jpeg',
  'gif'
])