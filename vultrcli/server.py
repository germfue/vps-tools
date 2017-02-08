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
from invoke import task, Collection
from vultr import Vultr
from .display import display_subid
from .key import api_key
from .query import query


@task(name='list',
      help={
          'criteria': 'Filter queried data. Example usage: '+
          '"{\'XYZ\': \'???\'}"'
      })
def server_list(ctx, criteria=''):
    query(lambda x: Vultr(x).server.list(), criteria)


@task(name='create',
      help={
          'dcid': 'Location to create this server in. See regions.list',
          'vpsplanid': 'Plan to use when creating this server. See plans.list',
          'osid': 'Operating system to use. See os.list',
          'ipxe_chain_url': '(optional) If you have selected the \'custom\' '+
          'operating system, this can be set to chainload the specified URL '+
          'on bootup, via iPXE',
          'isoid': '(optional) If you have selected the \'custom\' operating '+
          'system, this is the ID of a specific ISO to mount during the '+
          'deployment',
          'scriptid': '(optional) If you have not selected a \'custom\' '+
          'operating system, this can be the scriptid of a startup script to '+
          'execute on boot.  See startupscript.list',
          'snapshotid': '(optional) If you have selected the \'snapshot\' '+
          'operating system, this should be the snapshotid (see '+
          'snapshot.list) to restore for the initial installation',
          'enable_ipv6': '(optional) \'yes\' or \'no\'. If yes, an IPv6 '+
          'subnet will be assigned to the machine (where available)',
          'enable_private_network': '(optional) \'yes\' or \'no\'. If yes, '+
          'private networking support will be added to the new server.',
          'label': '(optional) This is a text label that will be shown in the '+
          'control panel',
          'sshkeyid': '(optional) List of SSH keys to apply to this server on '+
          'install (only valid for Linux/FreeBSD). See sshkey.list. Seperate '+
          'keys with commas',
          'auto_backups': '(optional) \'yes\' or \'no\'. If yes, automatic '+
          'backups will be enabled for this server (these have an extra '+
          'charge associated with them)',
          'appid': '(optional) If launching an application (OSID 186), this '+
          'is the appid to launch. See app.list',
          'userdata': '(optional) Base64 encoded cloud-init user-data',
          'notify_activate': '(optional, default \'yes\') \'yes\' or \'no\'. '+
          'If yes, an activation email will be sent when the server is ready',
          'ddos_protection':  '(optional, default \'no\') \'yes\' or \'no\'. '+
          'If yes, DDOS protection will be enabled on the subscription (there '+
          'is an additional charge for this)',
          'reserved_ip_v4': '(optional) IP address of the floating IP to use '+
          'as the main IP of this server',
          'hostname': '(optional) The hostname to assign to this server',
          'tag': '(optional) The tag to assign to this server',
      })
def server_create(ctx, dcid, vpsplanid, osid, ipxe_chain_url='',
                  isoid='', scriptid=0, snapshotid=0, enable_ipv6=False,
                  enable_private_network=False, label='', sshkeyid=0,
                  auto_backups=False, appid=0, userdata='',
                  notify_activate=True, ddos_protection=False,
                  reserved_ip_v4='', hostname='', tag=''):
    params = {}
    if ipxe_chain_url:
        params['ipxe_chain_url'] = ipxe_chain_url
    if scriptid:
        params['scriptid'] = scriptid
    if snapshotid:
        params['snapshotid'] = snapshotid
    if enable_ipv6:
        params['enable_ipv6'] = enable_ipv6
    if enable_private_network:
        params['enable_private_network'] = enable_private_network
    if label:
        params['label'] = label
    if sshkeyid:
        params['sshkeyid'] = sshkeyid
    if auto_backups:
        params['auto_backups'] = auto_backups
    if appid:
        params['appid'] = appid
    if userdata:
        params['userdata'] = userdata
    if not notify_activate:
        params['notify_activate'] = notify_activate
    if ddos_protection:
        params['ddos_protection'] = ddos_protection
    if reserved_ip_v4:
        params['reserved_ip_v4'] = reserved_ip_v4
    if hostname:
        params['hostname'] = hostname
    if tag:
        params['tag'] = tag
    vultr = Vultr(api_key)
    response = vultr.server.create(dcid, vpsplanid, osid, params or None)
    display_subid(response)


server_coll = Collection()
server_coll.add_task(server_list)
server_coll.add_task(server_create)
