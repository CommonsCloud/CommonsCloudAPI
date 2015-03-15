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
Import System Dependencies
"""
from functools import wraps


"""
Import Flask Dependencies
"""
from flask import abort

from flask_oauthlib.utils import extract_params

from flask.ext.oauthlib.provider import OAuth2Provider


"""
Commons Cloud Core API OAuth 2.0 provider

These are utility functions that allow us to check for OAuth requirements on
our own terms. They make it possible to check if a POST is crowdsourced or if
a GET is being done on a Public repository.

  @decorator oauth_or_public
  @decorator oauth_or_crowdsourced

"""
class CommonsOAuth2Provider(OAuth2Provider):

    def oauth_or_public(self, *scopes):
        def wrapper(f):
            @wraps(f)
            def decorated(*args, **kwargs):

              for func in self._before_request_funcs:
                  func()

              server = self.server
              uri, http_method, body, headers = extract_params()
              valid, req = server.verify_request(
                  uri, http_method, body, headers, scopes
              )

              for func in self._after_request_funcs:
                  valid, req = func(valid, req)

              if not kwargs.get('is_public', False):
                if not valid:
                  return abort(403)

              return f(*((req,) + args), **kwargs)
            return decorated
        return wrapper    

    def oauth_or_crowdsourced(self, *scopes):
        def wrapper(f):
            @wraps(f)
            def decorated(*args, **kwargs):

              for func in self._before_request_funcs:
                  func()

              server = self.server
              uri, http_method, body, headers = extract_params()
              valid, req = server.verify_request(
                  uri, http_method, body, headers, scopes
              )

              for func in self._after_request_funcs:
                  valid, req = func(valid, req)

              if not kwargs.get('is_crowdsourced', False):
                if not valid:
                  return abort(403)

              return f(*((req,) + args), **kwargs)
            return decorated
        return wrapper    
