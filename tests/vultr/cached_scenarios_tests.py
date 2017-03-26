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

import inspect
import json
import requests_mock
import ruamel.yaml
import unittest
import vps.vultr.key
from invoke import Context
from urllib.parse import parse_qs
from vps.console import puts
from vps.vultr.tasks import collection
from .scenario_file import load_cached_scenarios


class _TestCachedScenarios(object):
    """
    This class can't inherit from TestCase as it gets automatically loaded
    by setup tools. It defines though all test cases for the cached scenarios
    """

    def __init__(self, test_name, task, scenario):
        self.task = task
        self.scenario = scenario
        super(_TestCachedScenarios, self).__init__(test_name)

    def runAllSpecifiedParams(self):
        self._runTest(self._test_all_specified_params)

    def runTestCriteria(self):
        self._runTest(self._test_criteria)

    def runTestWithKey(self):
        self._runTest(self._test_with_key)

    def runTestWithoutMandatoryKey(self):
        self._runTest(self._test_key_not_present)

    def runTestWithoutKey(self):
        self._runTest(self._test_without_key)

    def runTestParamsDocumentation(self):
        # check that all parameters in the help have documentation
        for k, v in self.task.help.items():
            self.assertTrue(v, '%s misses documentation'%k)
        # check that there are as many items in the help as in the function
        # definition
        self.assertEqual(len(self.task.help),
                         # ctx is not included in get_arguments
                         len(self.task.get_arguments())
                         )


    def _runTest(self, f):
        req = self.scenario.parse_request()
        with requests_mock.mock() as m:
            op = getattr(m, self.scenario.http_method.lower())
            op(req.url, text=self._callback)
            ctx = self._task_context()
            # python api uses lower case. Vultr API uses upper case for ids
            python_params = {self._pythonize_id(k): v for k, v in req.params.items()}
            f(self.task, ctx, python_params)

    def _check_response(self, result):
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

    def _check_request(self, request, context):
        query = request.query
        if self.scenario.api_key:
            # requests_mock stores the headers in the query attribute,
            # lower case
            header = 'api_key=%s' % self.scenario.api_key.lower()
            self.assertIn(header, query)
        scenario_req = self.scenario.parse_request()
        doc_params = self.scenario.parse_doc_params().keys()
        if scenario_req.params or doc_params:
            scenario_params = dict(scenario_req.params)
            for mockedreq_param, mockedreq_value in parse_qs(request.text).items():
                # parse_qs will return a list of values
                self.assertEqual(1, len(mockedreq_value))
                mockedreq_value = mockedreq_value[0]
                # check that the key exists in the documented parameters
                self.assertIn(mockedreq_param, doc_params)
                # check that the values stored are the same
                if mockedreq_param in scenario_params:
                    self.assertEqual(mockedreq_value,
                                     scenario_params.pop(mockedreq_param),
                                     'value for %s mismatch' % mockedreq_param
                                     )
            self.assertFalse(scenario_params)

    def _test_with_key(self, task, ctx, python_params):
        vps.vultr.key._api_key = 'EXAMPLE'
        result = task(ctx, **python_params)
        self._check_response(result)

    def _test_without_key(self, task, ctx, python_params):
        vps.vultr.key._api_key = None
        result = task(ctx, **python_params)
        self._check_response(result)

    def _test_key_not_present(self, task, ctx, python_params):
        vps.vultr.key._api_key = None
        result = task(ctx, **python_params)
        self.assertIsNone(result)

    def _test_criteria(self, task, ctx, python_params):
        self._set_key()
        result = task(ctx, **python_params)
        # test that a valid filter works
        for k, v in result[0].items():
            if v:
                python_params['criteria'] = str({k: v})
                filtered = task(ctx, **python_params)
                for a_dict in filtered:
                    self.assertEqual(v, a_dict.get(k, ''))
                break
        else:
            self.assertFalse('No value found in reponse!')
        # test that an invalid filter returns nothing
        python_params['criteria'] = str({'fake key': 'fake value'})
        filtered = task(ctx, **python_params)
        self.assertFalse(filtered)

    def _test_all_specified_params(self, task, ctx, python_params):
        self._set_key()
        default_values = {
                'string': 'abc',
                'integer': 1,
                'boolean': 'yes'
                }
        for paramid, param_type in self.scenario.parse_doc_params().items():
            paramid = self._pythonize_id(paramid)
            if paramid not in python_params:
                python_params[paramid] = default_values[param_type]
        try:
            result = task(ctx, **python_params)
            self.assertIsNotNone(result)
        except TypeError as err:
            # this will happen if new parameters are added to the API, but not
            # supported in the vps interface
            if 'unexpected keyword argument' in str(err):
                puts('Please add missing parameters')
                puts(self.scenario.doc_params)
            raise err

    def _callback(self, request, context):
        self._check_request(request, context)
        return self.scenario.response

    def _task_context(self):
        ctx = Context()
        ctx.config.run.echo = False
        return ctx

    def _set_key(self):
        if self.scenario.api_key:
            vps.vultr.key._api_key = 'EXAMPLE'
        else:
            vps.vultr.key._api_key = None

    def _pythonize_id(self, _id):
        translation = {'type': '_type'}
        return translation.get(_id, _id.lower())


def _get_task(subcommand):
    (module, method) = subcommand.split('.')
    return collection.collections[module].tasks[method]


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

    class TestCachedScenarios(_TestCachedScenarios, unittest.TestCase, metaclass=_Meta):
        def __init__(self):
            super(TestCachedScenarios, self).__init__(test_name,
                                                      task,
                                                      scenario
                                                      )
    return TestCachedScenarios()


def load_tests(loader, standard_tests, pattern):
    suite = unittest.TestSuite()
    scenarios = ruamel.yaml.load(load_cached_scenarios(), Loader=ruamel.yaml.Loader)
    for api_call, scenario in scenarios.items():
        subcommand = scenario.invoke_subcommand()
        if subcommand in collection.task_names.keys():
            task = _get_task(subcommand)
            base_test_name = scenario.test_name()
            test = _load_test_case('%s_all_specified_params' % base_test_name,
                                   task,
                                   scenario,
                                   lambda x: x.runAllSpecifiedParams()
                                   )
            suite.addTest(test)
            test = _load_test_case('%s_params_documentation' % base_test_name,
                                   task,
                                   scenario,
                                   lambda x: x.runTestParamsDocumentation()
                                   )
            suite.addTest(test)
            if _supports_criteria(task):
                test = _load_test_case('%s_with_criteria' % base_test_name,
                                       task,
                                       scenario,
                                       lambda x: x.runTestCriteria()
                                       )
                suite.addTest(test)
            if scenario.api_key:
                test = _load_test_case('%s_with_key' % base_test_name,
                                       task,
                                       scenario,
                                       lambda x: x.runTestWithKey()
                                       )
                suite.addTest(test)

                test_name = '%s_without_mandatory_key' % base_test_name
                test = _load_test_case(test_name,
                                       task,
                                       scenario,
                                       lambda x: x.runTestWithoutMandatoryKey()
                                       )
                suite.addTest(test)
            else:
                test = _load_test_case('%s_without_key' % base_test_name,
                                       task,
                                       scenario,
                                       lambda x: x.runTestWithoutKey()
                                       )
                suite.addTest(test)
    return suite
