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
from .extensions import oauth

from .errors import load_errorhandlers

from .permissions import load_identities

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
            
    # Setup Mail
    mail.init_app(app)
    
    # Setup OAuth2 Provider
    oauth.init_app(app)

    # Load our application's blueprints
    load_blueprints(app)

    """
    Setup Flask Security 
    
    We cannot load the security information until after our blueprints
    have been loaded into our application.
    """
    from user.models import user_datastore
    security.init_app(app, user_datastore)
    
    # Initialize our database and create tables
    db.init_app(app)
    db.app = app
    db.create_all()

    # Load default application routes/paths
    load_errorhandlers(app)
    load_identities(app)

    if not app.debug:
        import logging
        logger = logging.getLogger('myapp')
        hdlr = logging.FileHandler('/Users/joshuaisaacpowell/Code/CommonsCloudAPI/error.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr) 
        logger.setLevel(logging.INFO)

    return app
