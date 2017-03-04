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
from clint.textui import puts, columns
from clint.textui.cols import console_width


def get_headers(dl):
    headers = set()
    for d in dl:
        for key in d.keys():
            headers.add(key)
    headers = list(headers)
    headers.sort()
    return headers


def column_size(headers, dl):
    csize = {}
    for header in headers:
        # initialize to the length of the key (header)
        length = len(header)
        for d in dl:
            item_length = len(str(d.get(header, '')))
            if item_length > length:
                length = item_length
        csize[header] = length
    return csize


def _trim(value, length):
    value = str(value)
    if len(value) > length:
        value = value[0:length]
        value = value[0:-3] + '...'
    return value


def display_yaml(a_dict):
    puts(ruamel.yaml.dump(a_dict, Dumper=ruamel.yaml.RoundTripDumper))


def display(dl):
    """
    Displays a list of dicts (dl) that contain same keys
    """
    headers = get_headers(dl)
    csize = column_size(headers, dl)
    cons_width = console_width({})
    values = csize.values()
    content_width = sum(values)
    if content_width > cons_width:
        # if content is bigger than console, switch to yaml format
        output = {}
        for d in dl:
            key = d.get('label') or d.get('SUBID') or d.get('SCRIPTID')
            output[key] = d
        puts(ruamel.yaml.dump(output, Dumper=ruamel.yaml.RoundTripDumper))
    else:
        # otherwise, print a table
        row = [[header, csize.get(header, '')] for header in headers]
        puts(columns(*row))
        for d in dl:
            row = [[_trim(d.get(h, ''), csize[h]), csize[h]] for h in headers]
            puts(columns(*row))
