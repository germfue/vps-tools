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
from urllib.parse import parse_qs
from vps.tool.wipe import wipe_vultr


_server_list_response = '''{
"576965": {
    "SUBID": "576965",
    "os": "CentOS 6 x64",
    "ram": "4096 MB",
    "disk": "Virtual 60 GB",
    "main_ip": "123.123.123.123",
    "vcpu_count": "2",
    "location": "New Jersey",
    "DCID": "1",
    "default_password": "nreqnusibni",
    "date_created": "2013-12-19 14:45:41",
    "pending_charges": "46.67",
    "status": "active",
    "cost_per_month": "10.05",
    "current_bandwidth_gb": 131.512,
    "allowed_bandwidth_gb": "1000",
    "netmask_v4": "255.255.255.248",
    "gateway_v4": "123.123.123.1",
    "power_status": "running",
    "server_state": "ok",
    "VPSPLANID": "28",
    "v6_network": "2001:DB8:1000::",
    "v6_main_ip": "2001:DB8:1000::100",
    "v6_network_size": "64",
    "v6_networks": [{
        "v6_network": "2001:DB8:1000::",
        "v6_main_ip": "2001:DB8:1000::100",
        "v6_network_size": "64"}],
    "label": "my new server",
    "internal_ip": "10.99.0.10",
    "kvm_url": "https://my.vultr.com/subs/novnc/api.php?data=eawxFVZw2mXnhGUV",
    "auto_backups": "yes",
    "tag": "mytag",
    "OSID": "127",
    "APPID": "0"
    }
}'''


class TestWipe(unittest.TestCase):

    def _task_context(self):
        ctx = Context()
        ctx.config.run.echo = False
        return ctx

    def test_no_key(self):
        vps.vultr.key._api_key = ''
        ctx = self._task_context()
        self.assertFalse(wipe_vultr(ctx))

    def test_wipe(self):
        self._test_mocked_query('/v1/server/list',
                                _server_list_response
                                )

    def _test_mocked_query(self, url_path, response):
        vps.vultr.key._api_key = 'EXAMPLE'
        ctx = self._task_context()
        with requests_mock.mock() as m:

            def _callback_query(request, context):
                self.assertEqual(url_path, request.path)
                return response

            def _callback_destroy(request, context):
                self.assertEqual('/v1/server/destroy', request.path)
                qs = parse_qs(request.text)
                self.assertEqual('576965', qs.pop('SUBID')[0])
                self.assertFalse(qs)

            m.get(requests_mock.ANY, text=_callback_query)
            m.post(requests_mock.ANY, text=_callback_destroy)

            self.assertEqual('576965', wipe_vultr(ctx)['my new server'])
