# -*- coding: utf-8 -*-

# Copyright 2012 Didip Kerabat
#
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

import twitter
from tornado import httpclient, escape

class Twitter(twitter.Twitter):
    """
    Extension of twitter.Twitter to use tornado.httpclient().
    Requirement:
        - twitter egg. See: http://mike.verdone.ca/twitter/

    Why?
        I want to perform Twitter request outside Tornado's request life-cycle.
        Thus, the mixin is kind of useless.
        But at the same time, I don't want blocking library.
    """
    def _http_protocol(self):
        return "https" if self.secure else "http"


    def _http_method_from_kwargs(self, kwargs):
        method = kwargs.pop('_method', "GET")
        for action in twitter.twitter_globals.POST_ACTIONS:
            if re.search("%s(/\d+)?$" % action, uri):
                method = "POST"
        return method, kwargs


    def _http_callback_from_kwargs(self, kwargs):
        callback = kwargs.pop('_callback', None)
        return callback, kwargs


    def _http_request_path_from_kwargs(self, kwargs):
        # If this part matches a keyword argument, use the
        # supplied value otherwise, just use the part.
        uri = '/'.join([
            str(kwargs.pop(uripart, uripart))
            for uripart in self.uriparts
        ])

        # If an id kwarg is present and there is no id to fill in in
        # the list of uriparts, assume the id goes at the end.
        id = kwargs.pop('id', None)
        if id: uri += "/%s" %(id)

        return uri, kwargs


    def __call__(self, **kwargs):
        protocol         = self._http_protocol()
        method, kwargs   = self._http_method_from_kwargs(kwargs)
        callback, kwargs = self._http_callback_from_kwargs(kwargs)
        uri, kwargs      = self._http_request_path_from_kwargs(kwargs)

        url = "%s://%s/%s" %(protocol, self.domain, uri)
        if self.format:
            url += ".%s" %(self.format)

        headers = self.auth.generate_headers() if self.auth else {}

        arg_data = self.auth.encode_params(url, method, kwargs)
        if method == 'GET':
            url += '?' + arg_data
            body = None
        else:
            body = arg_data.encode('utf8')

        return self._handle_response(url, headers, method=method, body=body, callback=callback)


    def _handle_response(self, url, headers, method="GET", body=None, callback=None):
        http = httpclient.AsyncHTTPClient()
        if req.method == "POST":
            http.fetch(url, headers=headers, method=method, body=body, callback=self._on_twitter_request(callback))
        else:
            http.fetch(url, headers=req.headers, callback=self._on_twitter_request(callback))


    def _on_twitter_request(self, callback):
        if not callback: callback = lambda x: x

        def call_me_later(response):
            if response.error:
                logging.warning("Error response %s fetching %s", response.error, response.request.url)
                callback(None)
                return

            if self.format == "json":
                callback(escape.json_decode(response.body))
            else:
                callback(response.body)
        return call_me_later

