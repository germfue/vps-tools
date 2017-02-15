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
from .key import api_key, require_key
from .query import query


@task(name='list',
      help={
          'criteria': 'Filter queried data. Example usage: ' +
          '"{\'name\': \'test\'}"'
      })
@require_key
def startupscript_list(ctx, criteria=''):
    """
    List all startup scripts on the current account.
    Scripts of type "boot" are executed by the server's operating system on
    the first boot.
    Scripts of type "pxe" are executed by iPXE when the server itself starts up
    """
    return query(ctx, lambda x: Vultr(x).startupscript.list(), criteria)


@task(name='create',
      help={
          'name': 'Name of the newly created startup script',
          'script': 'Startup script contents',
          'script_type': 'boot|pxe Type of startup script. Default is \'boot\'',
      })
@require_key
def startupscript_create(ctx, name, script, script_type='boot'):
    """
    Create a startup script
    """
    vultr = Vultr(api_key)
    response = vultr.startupscript.create(name, script, {'type': script_type})
    if ctx.config.run.echo:
        display_yaml(response)
    return response


@task(name='destroy',
      help={
          'scriptid': 'Unique identifier for this startup script',
      })
@require_key
def startupscript_destroy(ctx, scriptid):
    """
    Remove a startup script
    """
    vultr = Vultr(api_key)
    vultr.startupscript.destroy(scriptid)


@task(name='update',
      help={
          'scriptid': 'scriptid of script to update',
          'name': '(optional) New name for the startup script',
          'script': '(optional) New startup script contents',
      })
@require_key
def startupscript_update(ctx, scriptid, name='', script=''):
    """
    Update an existing startup script
    """
    vultr = Vultr(api_key)
    params = {}
    if name:
        params['name'] = name
    if script:
        params['script'] = script
    vultr.startupscript.update(scriptid, params)


startupscript_coll = Collection()
startupscript_coll.add_task(startupscript_create)
startupscript_coll.add_task(startupscript_destroy)
startupscript_coll.add_task(startupscript_list)
startupscript_coll.add_task(startupscript_update)
