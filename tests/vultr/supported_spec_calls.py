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

supported_calls = """/v1/account/info
/v1/app/list
/v1/auth/info
/v1/backup/list
/v1/block/attach
/v1/block/create
/v1/block/delete
/v1/block/detach
/v1/block/label_set
/v1/block/list
/v1/block/resize
/v1/dns/create_domain
/v1/dns/create_record
/v1/dns/delete_domain
/v1/dns/delete_record
/v1/dns/list
/v1/dns/records
/v1/dns/update_record
/v1/iso/list
/v1/os/list
/v1/plans/list
/v1/plans/list_vc2
/v1/plans/list_vdc2
/v1/regions/availability
/v1/regions/list
/v1/reservedip/attach
/v1/reservedip/convert
/v1/reservedip/create
/v1/reservedip/destroy
/v1/reservedip/detach
/v1/reservedip/list
/v1/server/app_change
/v1/server/app_change_list
/v1/server/backup_disable
/v1/server/backup_enable
/v1/server/backup_get_schedule
/v1/server/backup_set_schedule
/v1/server/bandwidth
/v1/server/create
/v1/server/create_ipv4
/v1/server/destroy
/v1/server/destroy_ipv4
/v1/server/get_app_info
/v1/server/get_user_data
/v1/server/halt
/v1/server/iso_attach
/v1/server/iso_detach
/v1/server/iso_status
/v1/server/label_set
/v1/server/list
/v1/server/list_ipv4
/v1/server/list_ipv6
/v1/server/neighbors
/v1/server/os_change
/v1/server/os_change_list
/v1/server/reboot
/v1/server/reinstall
/v1/server/restore_backup
/v1/server/restore_snapshot
/v1/server/reverse_default_ipv4
/v1/server/reverse_delete_ipv6
/v1/server/reverse_list_ipv6
/v1/server/reverse_set_ipv4
/v1/server/reverse_set_ipv6
/v1/server/set_user_data
/v1/server/start
/v1/server/upgrade_plan
/v1/server/upgrade_plan_list
/v1/snapshot/create
/v1/snapshot/destroy
/v1/snapshot/list
/v1/sshkey/create
/v1/sshkey/destroy
/v1/sshkey/list
/v1/sshkey/update
/v1/startupscript/create
/v1/startupscript/destroy
/v1/startupscript/list
/v1/startupscript/update
/v1/user/create
/v1/user/delete
/v1/user/list
/v1/user/update
/v1/firewall/group_create
/v1/firewall/group_delete
/v1/firewall/group_list
/v1/firewall/group_set_description
/v1/firewall/rule_create
/v1/firewall/rule_delete
/v1/firewall/rule_list
/v1/server/firewall_group_set
/v1/iso/create_from_url
/v1/server/private_network_enable
/v1/server/tag_set""".splitlines()
