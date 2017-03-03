# -*- coding: utf-8 -*-

# Copyright (c) 2016, Germán Fuentes Capella <development@fuentescapella.com>
# BSD 3-Clause License
#
# Copyright (c) 2017, Germán Fuentes Capella
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import re


class ScenarioRequest(object):

    _req_pattern = ("curl\s",
                    "(-H\s'API-Key:\s(?P<api_key>EXAMPLE)'\s+){0,1}",
                    "(?P<url>https://api.vultr.com/v1/[a-z]+/[a-z]+)\s*"
                    )
    _re_request = re.compile(''.join(_req_pattern))

    def __init__(self, request):
        match = self._re_request.match(request)
        if match:
            self.url = match.group('url')
            self.api_key = match.group('api_key')
            self.params = {}
            if '--data' in request:
                elements = request.replace("'", "").split('--data')
                for el in elements[1:]:
                    (key, value) = el.split('=')
                    key = key.strip()
                    if key.startswith("$"):
                        # this is to avoid an error in the documentation:
                        # --data $'script=..'\n"
                        key = key[1:]
                    self.params[key] = value.strip()
        else:
            raise ValueError('%s: could not be matched' % request)

    def __str__(self):
        return '%s(%r)' % (self.__class__.__name__, self.url)


class Scenario(object):

    def __init__(self, api_call, api_key='', http_method='', request='',
                 response='', doc_params=''):
        self.api_call = api_call
        self.api_key = api_key
        self.http_method = http_method
        self.request = request
        self.response = response
        self.doc_params = doc_params

    def parse_request(self):
        return ScenarioRequest(self.request)

    def _get_doc_param_type(self, line):
        if "'yes' or 'no'" in line:
            return 'boolean'
        return line.split(' ', 2)[1]

    def parse_doc_params(self):
        return {line.split(' ', 1)[0]: self._get_doc_param_type(line) for line in self.doc_params.splitlines()}

    def invoke_subcommand(self):
        return self.api_call.replace('/v1/', '').replace('/', '.')

    def test_name(self):
        return 'test_%s' % self.api_call.replace('/v1/', '').replace('/', '_')

    def __repr__(self):
        return '%s(%r, %r, %r, %r, %r, %r)' % (self.__class__.__name__,
                                               self.api_call,
                                               self.api_key,
                                               self.http_method,
                                               self.request,
                                               self.response,
                                               self.doc_params
                                               )
