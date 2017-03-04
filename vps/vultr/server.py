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

from invoke import task, Collection
from vultr import Vultr
from vps.console import display_yaml
from .params import param_dict
from .key import get_key, require_key
from .query import query


@task(name='list',
      help={
          'criteria': 'Filter queried data. Example usage: "{\'XYZ\': \'???\'}"',
          'subid': 'Unique identifier of a subscription. Only the subscription object will be returned',
          'tag': 'A tag string. Only subscription objects with this tag will be returned',
          'label': 'A text label string. Only subscription objects with this text label will be returned',
          'main_ip': 'An IPv4 address. Only the subscription matching this IPv4 address will be returned',
      })
@require_key
def server_list(ctx, subid=None, tag=None, label=None, main_ip=None, criteria=''):
    """
    List all active or pending virtual machines on the current account.
    The "status" field represents the status of the subscription and will be
    one of: pending | active | suspended | closed. If the status is "active",
    you can check "power_status" to determine if the VPS is powered on or not.
    When status is "active", you may also use "server_state" for a more detailed
    status of: none | locked | installingbooting | isomounting | ok.

    The API does not provide any way to determine if the initial installation
    has completed or not. The "v6_network", "v6_main_ip", and "v6_network_size"
    fields are deprecated in favor of "v6_networks".
    """
    params = param_dict(tag=tag, label=label, main_ip=main_ip)
    return query(ctx, lambda x: Vultr(x).server.list(subid=subid, params=params), criteria)


@task(name='create',
      help={
          'dcid': 'Location to create this server in. See regions.list',
          'vpsplanid': 'Plan to use when creating this server. See plans.list',
          'osid': 'Operating system to use. See os.list',
          'ipxe_chain_url': '(optional) If you have selected the \'custom\' ' +
          'operating system, this can be set to chainload the specified URL ' +
          'on bootup, via iPXE',
          'isoid': '(optional) If you have selected the \'custom\' operating ' +
          'system, this is the ID of a specific ISO to mount during the ' +
          'deployment',
          'scriptid': '(optional) If you have not selected a \'custom\' ' +
          'operating system, this can be the scriptid of a startup script to ' +
          'execute on boot.  See startupscript.list',
          'snapshotid': '(optional) If you have selected the \'snapshot\' ' +
          'operating system, this should be the snapshotid (see ' +
          'snapshot.list) to restore for the initial installation',
          'enable_ipv6': '(optional) \'yes\' or \'no\'. If yes, an IPv6 ' +
          'subnet will be assigned to the machine (where available)',
          'enable_private_network': '(optional) \'yes\' or \'no\'. If yes, ' +
          'private networking support will be added to the new server.',
          'label': '(optional) This is a text label that will be shown in ' +
          'the control panel',
          'sshkeyid': '(optional) List of SSH keys to apply to this server ' +
          'on install (only valid for Linux/FreeBSD). See sshkey.list. ' +
          'Seperate keys with commas',
          'auto_backups': '(optional) \'yes\' or \'no\'. If yes, automatic ' +
          'backups will be enabled for this server (these have an extra ' +
          'charge associated with them)',
          'appid': '(optional) If launching an application (OSID 186), this ' +
          'is the appid to launch. See app.list',
          'userdata': '(optional) Base64 encoded cloud-init user-data',
          'notify_activate': '(optional, default \'yes\') \'yes\' or \'no\'. ' +
          'If yes, an activation email will be sent when the server is ready',
          'ddos_protection':  '(optional, default \'no\') \'yes\' or \'no\'. ' +
          'If yes, DDOS protection will be enabled on the subscription (' +
          'there is an additional charge for this)',
          'reserved_ip_v4': '(optional) IP address of the floating IP to use ' +
          'as the main IP of this server',
          'hostname': '(optional) The hostname to assign to this server',
          'tag': '(optional) The tag to assign to this server',
          'firewallgroupid': 'The firewall group to assign to this server',
      })
@require_key
def server_create(ctx, dcid, vpsplanid, osid, ipxe_chain_url=None,
                  isoid=None, scriptid=None, snapshotid=None, enable_ipv6=None,
                  enable_private_network=None, label=None, sshkeyid=None,
                  auto_backups=None, appid=None, userdata=None,
                  notify_activate=None, ddos_protection=None,
                  reserved_ip_v4=None, hostname=None, tag=None,
                  firewallgroupid=None):
    """
    Create a new virtual machine
    You will start being billed for this immediately
    The response only contains the SUBID for the new machine
    """
    params = param_dict(ipxe_chain_url=ipxe_chain_url,
                        scriptid=scriptid,
                        snapshotid=snapshotid,
                        enable_ipv6=enable_ipv6,
                        enable_private_network=enable_private_network,
                        label=label,
                        sshkeyid=sshkeyid,
                        auto_backups=auto_backups,
                        appid=appid,
                        userdata=userdata,
                        notify_activate=notify_activate,
                        ddos_protection=ddos_protection,
                        reserved_ip_v4=reserved_ip_v4,
                        hostname=hostname,
                        tag=tag,
                        firewallgroupid=firewallgroupid,
                        )
    vultr = Vultr(get_key())
    response = vultr.server.create(dcid, vpsplanid, osid, params or None)
    if ctx.config.run.echo:
        display_yaml(response)
    return response


@task(name='destroy',
      help={
          'subid': 'Unique identifier for this subscription. These can be ' +
          'found using server.list',
      })
@require_key
def server_destroy(ctx, subid):
    """
    Destroy (delete) a virtual machine.
    All data will be permanently lost, and the IP address will be released.
    There is no going back from this call
    """
    vultr = Vultr(get_key())
    return vultr.server.destroy(subid)


server_coll = Collection()
server_coll.add_task(server_list)
server_coll.add_task(server_create)
server_coll.add_task(server_destroy)
