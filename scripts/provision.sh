#!/bin/bash

vps_dir=$HOME/Projects/vps-tools
if [ ! -d $vps_dir ]
then
    echo "$vps_dir: missing directory"
    exit -1
fi
cd $vps_dir

activate_script=$vps_dir/bin/activate
if [ ! -e $activate_script ]
then
    echo "$activate_script: missing file"
    exit -1
fi
source $activate_script

api_key_script=$HOME/.vps/api_key
if [ ! -e $api_key_script ]
then
    echo "$api_key_script: missing file"
    exit -1
fi
source $HOME/.vps/api_key

echo "Install latest version of the application"
echo ""
python setup.py build install

echo "Provision server"
echo ""
vps provision.vultr

echo "Wait to get the server ready..."
echo ""
sleep 90

echo "Load server keys in known_hosts file"
echo ""
ssh-keyscan -t ecdsa `vps ssh.list` >> $HOME/.ssh/known_hosts

echo "Create roster file"
echo ""
vps salt.roster > $HOME/Projects/salt-etc/etc/salt/roster

echo "Enjoy your server"
