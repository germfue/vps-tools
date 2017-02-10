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

from clint.textui import puts, indent
from invoke import task, Collection
from vps.vultr.tasks import collection as vultr_collection


vultr_api = """account.info
app.list
backup.list
dns.create_domain
dns.create_record
dns.delete_domain
dns.delete_record
dns.list
dns.records
dns.update_record
iso.list
os.list
plans.list
regions.availability
regions.list
server.ipv4.create
server.ipv4.destroy
server.ipv4.list
server.ipv4.reverse_default
server.ipv4.reverse_set
server.ipv6.list_ipv6
server.ipv6.reverse_delete_ipv6
server.ipv6.reverse_list_ipv6
server.ipv6.reverse_set_ipv6
server.bandwidth
server.create
server.destroy
server.get_user_data
server.halt
server.label_set
server.list
server.neighbors
server.os_change
server.os_change_list
server.reboot
server.reinstall
server.restore_backup
server.restore_snapshot
server.set_user_data
server.start
server.upgrade_plan
server.upgrade_plan_list
snapshot.create
snapshot.destroy
snapshot.list
sshkey.create
sshkey.destroy
sshkey.list
sshkey.update
startupscript.create
startupscript.destroy
startupscript.list
startupscript.update
"""


def _group_api_calls(calls):
    api_items = {}
    for api_call in calls:
        obj, new_method = api_call.rsplit('.', 1)
        methods = api_items.get(obj, [])
        if not methods:
            api_items[obj] = methods
        methods.append(new_method)
    return api_items


def _compare_apis(spec, impl):
    comp = {}
    for obj, methods in spec.items():
        comp[obj] = len(impl.get(obj, []))/len(methods)
    return comp


def _display(api, comp):
    puts(api)
    with indent(4):
        for obj, percentage in comp.items():
            puts('%s: %0.2f' % (obj, percentage))


@task(name='status')
def tool_status(ctx):
    """
    Temporal subcommand to track of how much is left for a full featured vultr
    """
    spec = _group_api_calls(vultr_api.splitlines())
    impl = _group_api_calls(vultr_collection.task_names.keys())
    comp = _compare_apis(spec, impl)
    _display('vultr', comp)


collection = Collection()
collection.add_task(tool_status)
