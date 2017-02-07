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

from __future__ import print_function
from enum import Enum
from invoke import task
from vultr import Vultr
from .annotations import allowed_args, mandatory_args
from .display import display_doc
from .query import query


class Param(Enum):
    criteria = 1
    dcid = 2
    vpsplanid = 3
    osid = 4
    params = 5

    def __str__(self):
        return self.name


@allowed_args(Param.criteria)
def _server_list(kwargs):
    query(lambda x: Vultr(x).server.list(), kwargs[Param.criteria])


@mandatory_args(Param.dcid, Param.vpsplanid, Param.osid, Param.params)
def _server_create(kwargs):
    print('server create')


doc = """
Subcommand:

  server    Server provisioning

Actions:

  list      List all active or pending virtual machines on the current account
            Parameter:
            criteria    Filter the result of the server list
                        Optional
                        Example:
                        $ vultr server list --criteria "{'family': 'ubuntu'}"
"""


@task
def server(ctx, action, criteria='', dcid=None, vpsplanid=None, osid=None,
           params=None):
    """
    Server provisioning
    """

    kwargs = {
        Param.criteria: criteria,
        Param.dcid: dcid,
        Param.vpsplanid: vpsplanid,
        Param.osid: osid,
        Param.params: params
    }
    try:
        if action == 'list':
            _server_list(kwargs)
        elif action == 'create':
            _server_create(kwargs)
        else:
            display_doc(doc)
    except ValueError as e:
        display_doc(doc, e)
