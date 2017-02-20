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

import requests_mock
import unittest
import vps.vultr.key
from invoke import Context
from vps.tool.salt import salt_roster


_server_list = '''{
"576965": {
    "SUBID": "576965",
    "os": "CentOS 6 x64",
    "main_ip": "123.123.123.123",
    "vcpu_count": "2",
    "location": "New Jersey",
    "DCID": "1",
    "default_password": "nreqnusibni",
    "date_created": "2013-12-19 14:45:41",
    "power_status": "running",
    "server_state": "ok",
    "VPSPLANID": "28",
    "label": "my new server",
    "internal_ip": "10.99.0.10",
    "tag": "mytag",
    "OSID": "127",
    "APPID": "0"
    }
}'''


_roster_response = {
    'my new server': {
        'host': '123.123.123.123',
        'user': 'root'
    }
}


class TestSalt(unittest.TestCase):

    def _task_context(self):
        ctx = Context()
        ctx.config.run.echo = False
        return ctx

    def test_no_key(self):
        vps.vultr.key._api_key = ''
        ctx = self._task_context()
        self.assertFalse(salt_roster(ctx))

    def test_with_1_server(self):
        vps.vultr.key._api_key = 'EXAMPLE'
        ctx = self._task_context()
        with requests_mock.mock() as m:

            def _callback_query(request, context):
                self.assertEqual('/v1/server/list', request.path)
                return _server_list

            def _callback_error(request, context):
                self.assertFalse('This should never be called')

            m.get(requests_mock.ANY, text=_callback_query)
            m.post(requests_mock.ANY, text=_callback_error)
            m.delete(requests_mock.ANY, text=_callback_error)
            m.put(requests_mock.ANY, text=_callback_error)
            m.head(requests_mock.ANY, text=_callback_error)
            m.options(requests_mock.ANY, text=_callback_error)
            m.patch(requests_mock.ANY, text=_callback_error)

            self.assertEqual(_roster_response, salt_roster(ctx))
