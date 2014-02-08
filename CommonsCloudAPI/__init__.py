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
from flask import Flask


"""
Import Application Dependencies
"""
from .extensions import db
from .extensions import mail
from .extensions import security
from .extensions import oauth2

from .errors import load_errorhandlers

from .models import user_datastore

from .utilities import load_blueprints
from .utilities import load_configuration


"""
Setup our base Flask application, retaining it as our application
object for use throughout the application
"""
def create_application(name = __name__, env = 'testing'):
    
    app = Flask(__name__, static_path = '/static')

    # Load our default configuration
    load_configuration(app, env)
    
    # Initialize our database and create tables
    db.init_app(app)
    db.app = app
    db.create_all()
        
    # Setup Mail
    mail.init_app(app)
    
    # Setup Flask Security 
    security.init_app(app, user_datastore)

    # Setup OAuth2 Provider
    oauth2.init_app(app)

    # Load our application's blueprints
    load_blueprints(app)
    
    # Load default application routes/paths
    load_errorhandlers(app)

    return app