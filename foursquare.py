import logging
import urllib

from tornado import httpclient
from tornado import escape
from tornado.httputil import url_concat

class FoursquareMixin(object):
    """Foursquare API using Oauth2"""

    _OAUTH_ACCESS_TOKEN_URL = "https://foursquare.com/oauth2/access_token"
    _OAUTH_AUTHORIZE_URL    = "https://foursquare.com/oauth2/authorize"
    _OAUTH_AUTHENTICATE_URL = "https://foursquare.com/oauth2/authenticate"
    _OAUTH_NO_CALLBACKS = False

    _BASE_URL = "https://api.foursquare.com/v2"

    @property
    def httpclient_instance(self):
        return httpclient.AsyncHTTPClient()

    def get_authenticated_user(self, redirect_uri, client_id, client_secret, code, callback):
        """
        Handles the login for the Foursquare user, returning a user object.

        Example usage::

          class FoursquareLoginHandler(LoginHandler, FoursquareMixin):
              @tornado.web.asynchronous
              def get(self):
                  if self.get_argument("code", False):
                      self.get_authenticated_user(
                          redirect_uri='/auth/foursquare/connect',
                          client_id=self.settings["foursquare_client_id"],
                          client_secret=self.settings["foursquare_client_secret"],
                          code=self.get_argument("code"),
                          callback=self.async_callback(self._on_login)
                      )
                      return

                  self.authorize_redirect(
                      redirect_uri='/auth/foursquare/connect',
                      client_id=self.settings["foursquare_api_key"]
                  )

              def _on_login(self, user):
                  logging.error(user)
                  self.finish()
        """
        args = {
            "redirect_uri": redirect_uri,
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
        }

        self.httpclient_instance.fetch(
            self._oauth_request_token_url(**args),
            self.async_callback(self._on_access_token, redirect_uri, client_id, client_secret, callback)
        )


    def authorize_redirect(self, redirect_uri=None, client_id=None,
                           client_secret=None, extra_params=None ):
        """Redirects the user to obtain OAuth authorization for this service.

        Some providers require that you register a Callback
        URL with your application. You should call this method to log the
        user in, and then call get_authenticated_user() in the handler
        you registered as your Callback URL to complete the authorization
        process.
        """
        args = {
          "redirect_uri": redirect_uri,
          "client_id": client_id,
          "response_type": "code"
        }
        if extra_params: args.update(extra_params)
        self.redirect(url_concat(self._OAUTH_AUTHENTICATE_URL, args))       # Why _OAUTH_AUTHORIZE_URL fails?


    def _oauth_request_token_url(self, redirect_uri= None, client_id = None, client_secret=None, code=None, extra_params=None):
        url = self._OAUTH_ACCESS_TOKEN_URL
        args = dict(
            redirect_uri=redirect_uri,
            code=code,
            client_id=client_id,
            client_secret=client_secret,
            grant_type="authorization_code"
            )
        if extra_params: args.update(extra_params)
        return url_concat(url, args)


    def _on_access_token(self, redirect_uri, client_id, client_secret, callback, response):
        if response.error:
            logging.warning('Foursquare auth error: %s' % str(response))
            callback(None)
            return

        session = escape.json_decode(response.body)

        self.foursquare_request(
            path="/users/self",
            callback=self.async_callback(self._on_get_user_info, callback, session),
            access_token=session["access_token"]
        )


    def _on_get_user_info(self, callback, session, user):
        if user is None:
            callback(None)
            return

        user.update({
            'first_name': user.get('firstName'),
            'last_name': user.get('lastName'),
            'home_city': user.get('homeCity'),
            'access_token': session['access_token']
        })
        callback(user)


    def foursquare_request(self, path, callback, access_token=None, post_args=None, **args):
        """
        If the request is a POST, post_args should be provided. Query
        string arguments should be given as keyword arguments.

        See: https://developer.foursquare.com/docs/
        """
        url = self.__class__._BASE_URL + path

        all_args = {}
        if access_token:
            all_args["access_token"] = access_token
            all_args["oauth_token"] = access_token
            all_args.update(args)

        if all_args: url += "?" + urllib.urlencode(all_args)

        callback = self.async_callback(self._on_foursquare_request, callback)
        if post_args is not None:
            self.httpclient_instance.fetch(url, method="POST", body=urllib.urlencode(post_args), callback=callback)
        else:
            self.httpclient_instance.fetch(url, callback=callback)


    def _on_foursquare_request(self, callback, response):
        if response.error:
            logging.warning("Error response %s fetching %s", response.error, response.request.url)
            callback(None)
            return
        callback(escape.json_decode(response.body))
