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

import os.path
import ruamel.yaml
from invoke import task, Collection
from vps.vultr.os import os_list
from vps.vultr.plans import plans_list
from vps.vultr.regions import regions_list
from vps.vultr.server import server_create
from .config import require_config


class _VultrProvision(object):

    cfg_path = os.path.join('.vps', 'vultr')

    def __init__(self, ctx):
        self.ctx = ctx

    def _read_cfg(self):
        path = os.path.join(os.path.expanduser('~'), _VultrProvision.cfg_path)
        with open(path, 'r') as f:
            return f.read()

    def _get_id(self, cfg, label, dyn_label, query):
        id = cfg.pop(label, None)
        if not id:
            criteria = cfg.pop(dyn_label)
            value = query(self.ctx, criteria)
            if len(value) > 1:
                msg = 'Criteria for %s(%s) returned multiple values' % (dyn_label, str(criteria))
                raise ValueError(msg)
            elif len(value) == 0:
                msg = 'Criteria for %s(%s) did not return any value' % (dyn_label, str(criteria))
                raise ValueError(msg)
            # careful, ids coming from vultr API are uppercase
            id = value[0][label.upper()]
        else:
            # just in case, removing from dict alternative config
            cfg.pop(dyn_label, None)
        return id

    def run(self):
        txt_cfg = self._read_cfg()
        cfg = ruamel.yaml.load(txt_cfg, ruamel.yaml.RoundTripLoader)
        if cfg:
            for label in cfg:
                vm_cfg = cfg[label]
                dcid = self._get_id(vm_cfg, 'dcid', 'region', regions_list)
                planid = self._get_id(vm_cfg, 'vpsplanid', 'plan', plans_list)
                osid = self._get_id(vm_cfg, 'osid', 'os', os_list)
                # we need to add the label to the params dict
                cfg[label]['label'] = label
                server_create(self.ctx, dcid, planid, osid, **cfg[label])


@task(name='vultr',
      help={})
@require_config(_VultrProvision.cfg_path)
def provision_vultr(ctx):
    """
    Provision Vultr servers based on ~/.vps/vultr
    """
    return _VultrProvision(ctx).run()


provision_coll = Collection()
provision_coll.add_task(provision_vultr)
