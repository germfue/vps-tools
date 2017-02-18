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


class _Test(object):

    def __init__(self, test_name, task, scenario):
        self.task = task
        self.scenario = scenario
        super(_Test, self).__init__(test_name)

    def check_response(self, result):
        scenario = self.scenario
        if not result:
            self.assertEqual(scenario.response, '')
        else:
            expected_response = json.loads(scenario.response)
            if scenario.invoke_subcommand().endswith('.list'):
                # .list methods change how the results are provided,
                # returning a list of values, instead of a dict
                values = list(expected_response.values())
                self.assertEqual(values, result)
            else:
                self.assertEqual(expected_response, result)

    def _get_context(self):
        ctx = Context()
        ctx.config.run.echo = False
        return ctx

    def runTestCriteria(self):
        self._runTest(self._test_criteria)

    def runTestWithKey(self):
        self._runTest(self._test_with_key)

    def runTestWithoutMandatoryKey(self):
        self._runTest(self._test_key_not_present)

    def runTestWithoutKey(self):
        self._runTest(self._test_without_key)

    def _runTest(self, f):
        req = self.scenario.parse_request()
        with requests_mock.mock() as m:
            # TODO check that request is as expected
            op = getattr(m, self.scenario.http_method.lower())
            op(req.url, text=self.scenario.response)
            ctx = self._get_context()
            f(self.task, ctx, req.params)

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

    def _test_criteria(self, task, ctx, params):
        vps.vultr.key._api_key = 'EXAMPLE'
        result = task(ctx, **params)
        # test that a valid filter works
        for k, v in result[0].items():
            if v:
                params['criteria'] = str({k: v})
                filtered = task(ctx, **params)
                for a_dict in filtered:
                    self.assertEqual(v, a_dict.get(k, ''))
                break
        else:
            self.assertFalse('No value found in reponse!')
        # test that an invalid filter returns nothing
        params['criteria'] = str({'fake key': 'fake value'})
        filtered = task(ctx, **params)
        self.assertFalse(filtered)


def _get_task(module, method):
    return collection.collections[module].tasks[method]


def _read_cases():
    with open('cases.yaml', 'r') as f:
        return f.read()


def _supports_criteria(task):
    param_names = [p.name for p in task.get_arguments()]
    return 'criteria' in param_names


def _load_test_case(test_name, task, scenario, f):
    class _Meta(type):
        """
        This Metaclass will set the right test name
        """
        def __new__(mcs, name, bases, d):
            d[test_name] = f
            return type.__new__(mcs, name, bases, d)

    class TestFromAPICases(_Test, unittest.TestCase, metaclass=_Meta):
        def __init__(self):
            super(TestFromAPICases, self).__init__(test_name,
                                                   task,
                                                   scenario
                                                   )
    return TestFromAPICases()


def load_tests(loader, standard_tests, pattern):
    suite = unittest.TestSuite()
    scenarios = ruamel.yaml.load(_read_cases(), Loader=ruamel.yaml.Loader)
    for api_call in scenarios:
        scenario = scenarios[api_call]
        subcommand = scenario.invoke_subcommand()
        if subcommand in collection.task_names.keys():
            (module, method) = subcommand.split('.')
            task = _get_task(module, method)
            base_test_name = scenario.test_name()
            if _supports_criteria(task):
                test = _load_test_case('%s_with_criteria' % base_test_name,
                                       task, scenario,
                                       lambda x: x.runTestCriteria()
                                       )
                suite.addTest(test)
            if scenario.api_key:
                test = _load_test_case('%s_with_key' % base_test_name,
                                       task, scenario,
                                       lambda x: x.runTestWithKey()
                                       )
                suite.addTest(test)

                test_name = '%s_without_mandatory_key' % base_test_name
                test = _load_test_case(test_name,
                                       task, scenario,
                                       lambda x: x.runTestWithoutMandatoryKey()
                                       )
                suite.addTest(test)
            else:
                test = _load_test_case('%s_without_key' % base_test_name,
                                       task, scenario,
                                       lambda x: x.runTestWithoutKey()
                                       )
                suite.addTest(test)
    return suite
