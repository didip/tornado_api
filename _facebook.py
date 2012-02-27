# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import urllib

from tornado import httpclient
from tornado import escape
from tornado.httputil import url_concat

class FacebookGraphMixin(object):
    """Facebook authentication using the new Graph API and OAuth2."""

    _OAUTH_ACCESS_TOKEN_URL = "https://graph.facebook.com/oauth/access_token"
    _OAUTH_AUTHORIZE_URL    = "https://graph.facebook.com/oauth/authorize"

    _BASE_URL = "https://graph.facebook.com"

    @property
    def httpclient_instance(self):
        return httpclient.AsyncHTTPClient()


    def authorize_redirect(self, redirect_uri=None, client_id=None, **kwargs):
        """Redirects the user to obtain OAuth authorization for this service.

        Some providers require that you register a Callback
        URL with your application. You should call this method to log the
        user in, and then call get_authenticated_user() in the handler
        you registered as your Callback URL to complete the authorization
        process.
        """
        args = {
          "redirect_uri": redirect_uri,
          "client_id": client_id
        }
        if kwargs: args.update(kwargs)
        self.redirect(url_concat(self._OAUTH_AUTHORIZE_URL, args))


    def get_authenticated_user(self, redirect_uri, client_id, client_secret, code, callback):
        """Handles the login for the Facebook user, returning a user object. Example usage::

          class FacebookGraphLoginHandler(LoginHandler, tornado.auth.FacebookGraphMixin):
              @tornado.web.asynchronous
              def get(self):
                  if self.get_argument("code", False):
                      self.get_authenticated_user(
                          redirect_uri='/auth/facebookgraph/',
                          client_id=self.settings["facebook_api_key"],
                          client_secret=self.settings["facebook_secret"],
                          code=self.get_argument("code"),
                          callback=self.async_callback(self._on_login)
                      )
                      return
                  self.authorize_redirect(
                      redirect_uri='/auth/facebookgraph/',
                      client_id=self.settings["facebook_api_key"],
                      scope="read_stream,offline_access"
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
            url_concat(self._OAUTH_ACCESS_TOKEN_URL, args),
            self.async_callback(self._on_access_token, redirect_uri, client_id, client_secret, callback)
        )


    def _on_access_token(self, redirect_uri, client_id, client_secret, callback, response):
        if response.error:
            logging.warning('Facebook auth error: %s' % str(response))
            callback(None)
            return

        args = escape.parse_qs_bytes(escape.native_str(response.body))
        session = {
            "access_token": args["access_token"][-1],
            "expires": args.get("expires")
        }

        self.facebook_request(
            path="/me",
            callback=self.async_callback(self._on_get_user_info, callback, session),
            access_token=session["access_token"]
        )


    def _on_get_user_info(self, callback, session, user):
        if user is None:
            callback(None)
            return

        user.update({"access_token": session.get("access_token"), "session_expires": session.get("expires")})
        callback(user)


    def facebook_request(self, path, callback, access_token=None, post_args=None, **args):
        """Fetches the given relative API path, e.g., "/btaylor/picture"

        If the request is a POST, post_args should be provided. Query
        string arguments should be given as keyword arguments.

        An introduction to the Facebook Graph API can be found at
        http://developers.facebook.com/docs/api

        Many methods require an OAuth access token which you can obtain
        through authorize_redirect() and get_authenticated_user(). The
        user returned through that process includes an 'access_token'
        attribute that can be used to make authenticated requests via
        this method. Example usage::

            class MainHandler(tornado.web.RequestHandler, tornado.auth.FacebookGraphMixin):
                @tornado.web.authenticated
                @tornado.web.asynchronous
                def get(self):
                    self.facebook_request(
                        "/me/feed",
                        post_args={"message": "I am posting from my Tornado application!"},
                        access_token=self.current_user["access_token"],
                        callback=self.async_callback(self._on_post))

                def _on_post(self, new_entry):
                    if not new_entry:
                        # Call failed; perhaps missing permission?
                        self.authorize_redirect()
                        return
                    self.finish("Posted a message!")

        """
        url = self.__class__._BASE_URL + path

        all_args = {}
        if access_token:
            all_args["access_token"] = access_token
            all_args.update(args)

        if all_args: url += "?" + urllib.urlencode(all_args)

        callback = self.async_callback(self._on_facebook_request, callback)
        if post_args is not None:
            self.httpclient_instance.fetch(url, method="POST", body=urllib.urlencode(post_args), callback=callback)
        else:
            self.httpclient_instance.fetch(url, callback=callback)


    def _on_facebook_request(self, callback, response):
        if response.error:
            logging.warning("Error response %s fetching %s", response.error, response.request.url)
            callback(None)
            return
        callback(escape.json_decode(response.body))
