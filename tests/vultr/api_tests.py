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
import requests
import ruamel.yaml
import unittest
from bs4 import BeautifulSoup
from collections import OrderedDict


_response = requests.get('https://www.vultr.com/api/')
_soup = BeautifulSoup(_response.text, 'html.parser')
_blacklist_calls = ('cURL',)
_api_calls = """/v1/account/info
/v1/app/list
/v1/auth/info
/v1/backup/list
/v1/block/attach
/v1/block/create
/v1/block/delete
/v1/block/detach
/v1/block/label_set
/v1/block/list
/v1/block/resize
/v1/dns/create_domain
/v1/dns/create_record
/v1/dns/delete_domain
/v1/dns/delete_record
/v1/dns/list
/v1/dns/records
/v1/dns/update_record
/v1/iso/list
/v1/os/list
/v1/plans/list
/v1/plans/list_vc2
/v1/plans/list_vdc2
/v1/regions/availability
/v1/regions/list
/v1/reservedip/attach
/v1/reservedip/convert
/v1/reservedip/create
/v1/reservedip/destroy
/v1/reservedip/detach
/v1/reservedip/list
/v1/server/app_change
/v1/server/app_change_list
/v1/server/backup_disable
/v1/server/backup_enable
/v1/server/backup_get_schedule
/v1/server/backup_set_schedule
/v1/server/bandwidth
/v1/server/create
/v1/server/create_ipv4
/v1/server/destroy
/v1/server/destroy_ipv4
/v1/server/get_app_info
/v1/server/get_user_data
/v1/server/halt
/v1/server/iso_attach
/v1/server/iso_detach
/v1/server/iso_status
/v1/server/label_set
/v1/server/list
/v1/server/list_ipv4
/v1/server/list_ipv6
/v1/server/neighbors
/v1/server/os_change
/v1/server/os_change_list
/v1/server/reboot
/v1/server/reinstall
/v1/server/restore_backup
/v1/server/restore_snapshot
/v1/server/reverse_default_ipv4
/v1/server/reverse_delete_ipv6
/v1/server/reverse_list_ipv6
/v1/server/reverse_set_ipv4
/v1/server/reverse_set_ipv6
/v1/server/set_user_data
/v1/server/start
/v1/server/upgrade_plan
/v1/server/upgrade_plan_list
/v1/snapshot/create
/v1/snapshot/destroy
/v1/snapshot/list
/v1/sshkey/create
/v1/sshkey/destroy
/v1/sshkey/list
/v1/sshkey/update
/v1/startupscript/create
/v1/startupscript/destroy
/v1/startupscript/list
/v1/startupscript/update
/v1/user/create
/v1/user/delete
/v1/user/list
/v1/user/update
""".splitlines()

_re_block = re.compile('/v1/(?P<block>[^/]+)/')
_blocks = set([_re_block.match(x).group('block') for x in _api_calls])

_re_meta = re.compile('.*\n([a-zA-Z ]+:\s{1,2}[a-zA-Z]*)\s.*')
_meta_api_key = 'API Key Required:'
_meta_http_method = 'Request Type:'
_sample_request = 'Example Request:'
_sample_response = 'Example Response:'
_parameters = 'Parameters:'
_no_parameters = 'No parameters.'


class TestAPI(unittest.TestCase):
    """
    These tests check that we are using the right version of the API, as well
    as preparing the expected inputs and outputs for the specific operation
    tests
    """

    def _find_api_calls(self):
        return [x for x in _soup.find_all('h3')
                if x.text not in _blacklist_calls]

    def test_response(self):
        self.assertEqual(200, _response.status_code)

    def test_api_call_definition(self):
        calls_found = [x.text for x in self._find_api_calls()]

        # check that all calls retrieved match existing calls
        for call in calls_found:
            self.assertIn(call, _api_calls)

        # check that no API call gets dropped
        for call in _api_calls:
            self.assertIn(call, calls_found)

    def _parse_metadata(self, scenario, table):
        for meta in _re_meta.findall(table.get_text()):
            if meta.startswith(_meta_api_key):
                value = meta.replace(_meta_api_key, '').strip()
                scenario['API_KEY'] = value
            if meta.startswith(_meta_http_method):
                value = meta.replace(_meta_http_method, '').strip()
                scenario['HTTP_METHOD'] = value

    def _parse_samples(self, scenario, code_blocks):
        for code_block in code_blocks:
            key = code_block.find_all('h4', limit=1)[0].text
            value = code_block.find_all('code', limit=1)[0].text
            if key == _sample_request:
                scenario['REQUEST'] = value
            elif key == _sample_response:
                scenario['RESPONSE'] = value
            elif key == _parameters:
                if value == _no_parameters:
                    value = ''
                scenario['PARAMETERS'] = value
            else:
                raise ValueError('%s: item not expected' % key)

    def _load_scenarios(self):
        with open('cases.yaml', 'r') as f:
            return f.read()

    def _parse_scenarios(self):
        scenarios = OrderedDict()
        for api_call in self._find_api_calls():
            scenario = OrderedDict()
            self._parse_metadata(scenario, api_call.parent.table)
            code_blocks = api_call.parent.find_all('div', class_='code')
            self._parse_samples(scenario, code_blocks)
            scenarios[api_call.text] = scenario
        return scenarios

    def test_scenarios(self):
        scenarios = ruamel.yaml.dump(self._parse_scenarios(),
                                     Dumper=ruamel.yaml.RoundTripDumper)
        scenarios_in_use = self._load_scenarios()
        try:
            error_msg = "execute 'diff cases.yaml cases_new.yaml' for details"
            self.assertEqual(scenarios_in_use, scenarios, error_msg)
        except:
            with open('cases_new.yaml', 'w') as f:
                f.write(scenarios)
            raise
