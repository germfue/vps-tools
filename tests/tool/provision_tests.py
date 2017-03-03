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

import os.path
import requests_mock
import unittest
import vps.vultr.key
from invoke import Context
from unittest.mock import patch
from urllib.parse import parse_qs
from vps.tool.provision import provision_vultr, _VultrProvision


class use_once(object):
    def __init__(self, mock, return_value, *args):
        self.mock = mock
        self.return_value = return_value
        self.args = args

    def __enter__(self):
        self.mock.return_value = self.return_value

    def __exit__(self, exc_type, exc_value, traceback):
        if not exc_type:
            self.mock.assert_called_once_with(*self.args)
        return False


class _MockedVP(_VultrProvision):
    def __init__(self, ctx, cfg):
        self.cfg = cfg
        super(_MockedVP, self).__init__(ctx)

    def _read_cfg(self):
        return self.cfg


_label = 'vmlabel'
_dcid = '1'
_vpsplanid = '1'
_osid = '127'
_region_name = 'New Jersey'
_plan_name = 'Starter'
_os_name = 'CentOS 6 x64'
_script_id = '123'
_os_response = '''{
"127": {
    "OSID": "127",
    "name": "CentOS 6 x64",
    "arch": "x64",
    "family": "centos",
    "windows": false
},
"148": {
    "OSID": "148",
    "name": "Ubuntu 12.04 i386",
    "arch": "i386",
    "family": "ubuntu",
    "windows": false
    }
}'''
_plan_response = '''{
"1": {
    "VPSPLANID": "1",
    "name": "Starter",
    "vcpu_count": "1",
    "ram": "512",
    "disk": "20",
    "bandwidth": "1",
    "price_per_month":"5.00",
    "windows": false,
    "plan_type": "SSD",
    "available_locations": [1,2,3]
    },
"2": {
    "VPSPLANID": "2",
    "name": "Basic",
    "vcpu_count": "1",
    "ram": "1024",
    "disk": "30",
    "bandwidth": "2",
    "price_per_month": "8.00",
    "windows": false,
    "plan_type": "SATA",
    "available_locations": [ ],
    "deprecated": true
    }
}'''
_region_response = '''{
"1": {
    "DCID": "1",
    "name": "New Jersey",
    "country": "US",
    "continent": "North America",
    "state": "NJ",
    "ddos_protection": true,
    "block_storage": true,
    "regioncode": "EWR"
    },
"2": {
    "DCID": "2",
    "name": "Chicago",
    "country": "US",
    "continent": "North America",
    "state": "IL",
    "ddos_protection": false,
    "block_storage": false,
    "regioncode": "ORD"
    }
}'''
_cfg_ids = """
%s:
    dcid: %s
    vpsplanid: %s
    osid: %s
""" % (_label, _dcid, _vpsplanid, _osid)
_cfg_region = """
%s:
    region:
        name: %s
    vpsplanid: %s
    osid: %s
""" % (_label, _region_name, _vpsplanid, _osid)
_cfg_plan = """
%s:
    dcid: %s
    plan:
        name: %s
    osid: %s
""" % (_label, _dcid, _plan_name, _osid)
_cfg_os = """
%s:
    dcid: %s
    vpsplanid: %s
    os:
        name: %s
""" % (_label, _dcid, _vpsplanid, _os_name)
_cfg_no_match = """
%s:
    dcid: %s
    vpsplanid: %s
    os:
        name: %s
""" % (_label, _dcid, _vpsplanid, 'fake os')
_cfg_multiple_match = """
%s:
    dcid: %s
    plan:
        vcpu_count: "1"
    osid: %s
""" % (_label, _dcid, _osid)
_cfg_script_id = """
%s:
    dcid: %s
    vpsplanid: %s
    osid: %s
    scriptid: %s
""" % (_label, _dcid, _vpsplanid, _osid, _script_id)


class TestProvision(unittest.TestCase):

    def _task_context(self):
        ctx = Context()
        ctx.config.run.echo = False
        return ctx

    @patch('vps.tool.config.os')
    def test_no_config(self, mock_os):
        path = os.path.join(os.path.expanduser('~'), _VultrProvision.cfg_path)
        with use_once(mock_os.path.exists, False, path):
            ctx = self._task_context()
            self.assertIsNone(provision_vultr(ctx))

    def test_empty_config(self):
        ctx = self._task_context()
        self.assertIsNone(_MockedVP(ctx, '').run())

    def test_no_key(self):
        vps.vultr.key._api_key = ''
        ctx = self._task_context()
        self.assertIsNone(_MockedVP(ctx, _cfg_ids).run())

    def _test_mocked_query(self, cfg, url_path, response):
        vps.vultr.key._api_key = 'EXAMPLE'
        ctx = self._task_context()
        with requests_mock.mock() as m:

            def _callback_query(request, context):
                self.assertEqual(url_path, request.path)
                return response

            def _callback_create(request, context):
                self.assertEqual('/v1/server/create', request.path)
                qs = parse_qs(request.text)
                self.assertEqual(_dcid, qs.pop('DCID')[0])
                self.assertEqual(_label, qs.pop('label')[0])
                self.assertEqual(_vpsplanid, qs.pop('VPSPLANID')[0])
                self.assertEqual(_osid, qs.pop('OSID')[0])
                if 'scriptid' in cfg:
                    self.assertEqual(_script_id, qs.pop('SCRIPTID')[0])

                self.assertFalse(qs)

            m.get(requests_mock.ANY, text=_callback_query)
            m.post(requests_mock.ANY, text=_callback_create)

            self.assertIsNone(_MockedVP(ctx, cfg).run())

    def test_basic_ids(self):
        self._test_mocked_query(_cfg_ids,
                                'no query',
                                'no response'
                                )

    def test_region(self):
        self._test_mocked_query(_cfg_region,
                                '/v1/regions/list',
                                _region_response
                                )

    def test_plan(self):
        self._test_mocked_query(_cfg_plan,
                                '/v1/plans/list',
                                _plan_response
                                )

    def test_os(self):
        self._test_mocked_query(_cfg_os,
                                '/v1/os/list',
                                _os_response
                                )

    def test_no_match(self):
        with self.assertRaises(ValueError):
            try:
                self._test_mocked_query(_cfg_no_match,
                                        '/v1/os/list',
                                        _os_response
                                        )
            except ValueError as e:
                self.assertIn('not return any value', str(e))
                raise

    def test_multiple_match(self):
        with self.assertRaises(ValueError):
            try:
                self._test_mocked_query(_cfg_multiple_match,
                                        '/v1/plans/list',
                                        _plan_response
                                        )
            except ValueError as e:
                self.assertIn('multiple', str(e))
                raise

    def test_script_id(self):
        self._test_mocked_query(_cfg_script_id,
                                'no query',
                                'no response'
                                )
