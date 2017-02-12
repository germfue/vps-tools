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

import unittest
from vps.console import get_headers, column_size


class TestDisplay(unittest.TestCase):

    def test_headers(self):
        h = [
            {'h0': 0,
             'h1': 1,
             },
            {'h0': 0,
             'h1': 1,
             },
        ]
        self.assertEqual(get_headers(h), ['h0', 'h1'])

    def test_bad_headers(self):
        h = [
            {'h0': 0,
             'h1': 1,
             },
            {'h0': 0,
             'h1': 1,
             'h2': 2,
             },
        ]
        with self.assertRaises(KeyError):
            get_headers(h)

    def test_column_size(self):
        matrix = [
            {'k0': 'text0',
             'k1': '1',
             },
            {'k0': 'txt',
             'k1': '',
             },
        ]
        csize = column_size(matrix[0].keys(), matrix)
        self.assertEqual(csize['k0'], 5)
        self.assertEqual(csize['k1'], 2)

    def test_column_size_with_boolean(self):
        matrix = [{'k0': False}]
        csize = column_size(matrix[0].keys(), matrix)
        self.assertEqual(csize['k0'], 5)
