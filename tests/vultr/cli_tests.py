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

import json
import requests_mock
import ruamel.yaml
import unittest
import vps.vultr.key
from invoke import Context
from vps.vultr.tasks import collection


def _to_subcommand(api_call):
    return api_call.replace('/v1/', '').replace('/', '.')


def _test_case(name, scenario):
    class TestCLI(unittest.TestCase):

        def __init__(self, name):
            self.name = name
            (self.module, self.method) = name.split('.')
            super(TestCLI, self).__init__(name)

        def __getattribute__(self, name):
            if name in collection.task_names.keys():
                return getattr(self, 'runTest')
            else:
                return super(TestCLI, self).__getattribute__(name)

        def check_response(self, result):
            if not result:
                self.assertEqual(scenario.response, '')
            else:
                expected_response = json.loads(scenario.response)
                if self.name.endswith('.list'):
                    # .list methods change how the results are provided,
                    # returning a list of values, instead of a dict
                    values = list(expected_response.values())
                    self.assertEqual(values, result)
                else:
                    self.assertEqual(expected_response, result)

        def runTest(self):
            req = scenario.parse_request()
            task = collection.collections[self.module].tasks[self.method]
            with requests_mock.mock() as m:
                # TODO check that request is as expected
                op = getattr(m, scenario.http_method.lower())
                op(req.url, text=scenario.response)
                ctx = Context()
                ctx.config.run.echo = False
                if scenario.api_key:
                    self._test_with_key(task, ctx, req.params)
                    self._test_key_not_present(task, ctx, req.params)
                else:
                    self._test_without_key(task, ctx, req.params)

        def _test_with_key(self, task, ctx, params):
            vps.vultr.key._api_key = 'EXAMPLE'
            result = task(ctx, **params)
            self.check_response(result)

        def _test_without_key(self, task, ctx, params):
            vps.vultr.key._api_key = None
            result = task(ctx, **params)
            self.check_response(result)

        def _test_key_not_present(self, task, ctx, params):
            vps.vultr.key._api_key = None
            result = task(ctx, **params)
            self.assertIsNone(result)

    return TestCLI(name)


def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    with open('cases.yaml', 'r') as f:
        scenarios = ruamel.yaml.load(f.read(), Loader=ruamel.yaml.Loader)
        for api_call in scenarios:
            subcommand = _to_subcommand(api_call)
            if subcommand in collection.task_names.keys():
                scenario = scenarios[api_call]
                test_case = _test_case(subcommand, scenario)
                suite.addTest(test_case)
    return suite
