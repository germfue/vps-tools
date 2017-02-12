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

import ruamel.yaml
import unittest
from vps.vultr.tasks import collection


def _to_subcommand(api_call):
    return api_call.replace('/v1/', '').replace('/', '.')


def _test_case(name, key, http_method, request, response, parameters):
    class TestCLI(unittest.TestCase):

        def __init__(self, name, key, http_method, request, response,
                     parameters):
            self.name = name
            self.key = key
            self.http_method = http_method
            self.request = request
            self.response = response
            self.parameters = parameters
            (self.module, self.method) = name.split('.')
            super(TestCLI, self).__init__(name)

        def __getattribute__(self, name):
            if name in collection.task_names.keys():
                return getattr(self, 'runTest')
            else:
                return super(TestCLI, self).__getattribute__(name)

        def runTest(self):
            # temporary, until first method is executed properly
            if self.name == 'os.list':
                # task = collection.collections[self.module].tasks[self.method]
                if self.key:
                    self._test_key_not_present()

        def _test_key_not_present(self):
            raise NotImplementedError('_test_key_not_present')

    return TestCLI(name, key, http_method, request, response, parameters)


def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    with open('cases.yaml', 'r') as f:
        scenarios = ruamel.yaml.load(f.read(), ruamel.yaml.RoundTripLoader)
        for api_call in scenarios:
            subcommand = _to_subcommand(api_call)
            if subcommand in collection.task_names.keys():
                scenario = scenarios[api_call]
                key = scenario['API_KEY']
                http_method = scenario['HTTP_METHOD']
                request = scenario['REQUEST']
                response = scenario['RESPONSE']
                params = scenario['PARAMETERS']
                test_case = _test_case(subcommand, key, http_method, request,
                                       response, params)
                suite.addTest(test_case)
    return suite
