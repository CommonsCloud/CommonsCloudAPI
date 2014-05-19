from functools import wraps
from flask import abort
from flask_oauthlib.utils import extract_params
from flask.ext.oauthlib.provider import OAuth2Provider
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
