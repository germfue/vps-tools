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
import tempfile
import unittest
import vps.vultr.key
from ast import literal_eval
from invoke import Context
from urllib.parse import parse_qs
from vps.vultr.startupscript import startupscript_create, startupscript_update


_script_name = 'test script'
_startupscript = '''#!/bin/bash
echo "hello world" > /root/hello'''
_scriptid = '5'
_response = '{ \"SCRIPTID\": %s }' % _scriptid


class TestStartupscript(unittest.TestCase):

    def test_create_script_with_file_path(self):
        with tempfile.NamedTemporaryFile(mode='w') as f:
            f.write(_startupscript)
            f.seek(0)
            self._test_mocked_script_function('create', f.name)

    def test_update_script_with_file_path(self):
        with tempfile.NamedTemporaryFile(mode='w') as f:
            f.write(_startupscript)
            f.seek(0)
            self._test_mocked_script_function('update', f.name)

    def _task_context(self):
        ctx = Context()
        ctx.config.run.echo = False
        return ctx

    def _test_mocked_script_function(self, op, script_path):
        vps.vultr.key._api_key = 'EXAMPLE'
        ctx = self._task_context()
        with requests_mock.mock() as m:

            def _callback_create(request, context):
                self.assertEqual('/v1/startupscript/' + op, request.path)
                qs = parse_qs(request.text)
                self.assertEqual(_script_name, qs.pop('name')[0])
                self.assertEqual(_startupscript, qs.pop('script')[0])
                if op == 'update':
                    self.assertEqual(_scriptid, qs.pop('SCRIPTID')[0])
                self.assertFalse(qs)
                return _response

            def _callback_error(request, context):
                self.assertFalse('This should never be called')

            m.post(requests_mock.ANY, text=_callback_create)
            m.get(requests_mock.ANY, text=_callback_error)
            m.delete(requests_mock.ANY, text=_callback_error)
            m.put(requests_mock.ANY, text=_callback_error)
            m.head(requests_mock.ANY, text=_callback_error)
            m.options(requests_mock.ANY, text=_callback_error)
            m.patch(requests_mock.ANY, text=_callback_error)

            self.assertIn(op, ['create', 'update'])
            if op == 'create':
                result = startupscript_create(ctx,
                                              name=_script_name,
                                              script=script_path
                                              )
            elif op == 'update':
                result = startupscript_update(ctx,
                                              _scriptid,
                                              name=_script_name,
                                              script=script_path
                                              )
            self.assertEqual(literal_eval(_response), result)
