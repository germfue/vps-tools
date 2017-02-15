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

from glob import glob
from setuptools import setup
from vps.version import __version__


# find all __init__.py files under vps/*, take folder path and convert it
# to pckg syntax (vps/vultr -> vps.vultr)
pcks_init = glob('vps/**/__init__.py', recursive=True)
pckgs = [p.rsplit('/', 1)[0].replace('/', '.') for p in pcks_init]

long_description = """
Tools to manage your VPS (Virtual Private Server)
"""

setup(
    name="vps-tools",
    version=__version__,
    author="Germán Fuentes Capella",
    author_email="development@fuentescapella.com",
    description="VPS Tools",
    license="BSD",
    keywords="vps vultr cli",
    url="https://github.com/germfue/vps-tools.git",
    install_requires=[
        'invoke',
        'vultr',
        'clint',
        'ruamel.yaml',
    ],
    tests_require=[
        'beautifulsoup4',
        'requests',
        'requests-mock',
    ],
    packages=pckgs,
    test_suite='tests',
    long_description=long_description,
    entry_points={
        'console_scripts': [
            'vps = vps.program:vps.run',
            'vps-status = vps.program:status.run',
            'vultr = vps.program:vultr.run',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: BSD License",
        "Environment :: Console",
    ],
)
