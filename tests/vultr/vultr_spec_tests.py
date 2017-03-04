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
from .scenario_file import load_cached_scenarios, dump_retrieved_scenarios, error_scenario_mismatch
from .supported_spec_calls import supported_calls
from .test_scenario import TestScenario


_response = requests.get('https://www.vultr.com/api/')
_soup = BeautifulSoup(_response.text, 'html.parser')
_blacklist_calls = ('cURL',)

_re_block = re.compile('/v1/(?P<block>[^/]+)/')
_blocks = set([_re_block.match(x).group('block') for x in supported_calls])

_re_row = '.*%s\s+%s\s.*'
_txt_api_key = 'API Key Required:'
_txt_http_method = 'Request Type:'
_txt_sample_request = 'Example Request:'
_txt_sample_response = 'Example Response:'
_txt_parameters = 'Parameters:'
_txt_no_parameters = 'No parameters.'
_txt_no_response = 'No response, check HTTP result code.'


class TestUpdatesInVultrSpec(unittest.TestCase):
    """
    These tests check if the api defined in https://vultr.com/api and the
    version cached are in sync
    """

    def test_spec_availability(self):
        self.assertEqual(200, _response.status_code)

    def test_api_calls_defined_and_cached_in_sync(self):
        calls_found = [x.text for x in self._find_reported_calls()]

        # check that all calls retrieved match existing calls
        for call in calls_found:
            self.assertIn(call, supported_calls, 'New calls added to api')

        # check that no API call gets dropped
        for call in supported_calls:
            self.assertIn(call, calls_found)

    def test_if_new_scenarios_are_defined(self):
        scenarios = ruamel.yaml.dump(self._parse_scenarios())
        cached_scenarios = load_cached_scenarios()
        try:
            self.assertEqual(cached_scenarios, scenarios, error_scenario_mismatch)
        except:
            dump_retrieved_scenarios(scenarios)
            raise

    def _find_reported_calls(self):
        return [x for x in _soup.find_all('h3')
                if x.text not in _blacklist_calls]

    def _parse_table(self, scenario, table):
        txt = table.get_text()
        match = re.search(_re_row % (_txt_api_key, 'Yes'), txt)
        if match:
            scenario.api_key = 'EXAMPLE'
        else:
            scenario.api_key = ''
        match = re.search(_re_row % (_txt_http_method, 'GET'), txt)
        if match:
            scenario.http_method = 'GET'
        else:
            match = re.search(_re_row % (_txt_http_method, 'POST'), txt)
            if match:
                scenario.http_method = 'POST'
            else:
                raise ValueError('Can not find HTTP Method: %s' % txt)

    def _parse_code_blocks(self, scenario, code_blocks):
        for code_block in code_blocks:
            key = code_block.find_all('h4', limit=1)[0].text
            value = code_block.find_all('code', limit=1)[0].text
            if key == _txt_sample_request:
                scenario.request = value
            elif key == _txt_sample_response:
                scenario.response = value.replace(_txt_no_response, '')
            elif key == _txt_parameters:
                scenario.doc_params = value.replace(_txt_no_parameters, '')
            else:
                raise ValueError('%s: item not expected' % key)

    def _parse_scenarios(self):
        scenarios = OrderedDict()
        for api_call in self._find_reported_calls():
            scenario = TestScenario(api_call.text)
            self._parse_table(scenario, api_call.parent.table)
            code_blocks = api_call.parent.find_all('div', class_='code')
            self._parse_code_blocks(scenario, code_blocks)
            scenarios[api_call.text] = scenario
        return scenarios
