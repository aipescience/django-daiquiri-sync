import ConfigParser

import os
import subprocess
import tempfile

import yaml


class Ansible():

    def __init__(self, inventory_file):
        self.inventory_file = inventory_file

        # parse the ansible inventory file
        config = ConfigParser.RawConfigParser(allow_no_value=True)
        config.read(inventory_file)

        # set the list of host_groups
        self.host_groups = config.sections()

        # set the dict of hosts, seperated by host_group
        self.hosts = {}
        for host_group in self.host_groups:
            self.hosts[host_group] = [name for name, _ in config.items(host_group)]

        # initialize the plays dict, seperated by host_group
        self.plays = {}
        for host_group in self.host_groups:
            self.plays[host_group] = {
                'name': 'Sync %s' % host_group,
                'hosts': host_group,
                'remote_user': 'root',
                'tasks': []
            }

    def play(self):
        # convert the plays dict to a yaml, but preserving the order of host_groups
        playbook_yaml = yaml.dump([self.plays[host_group] for host_group in self.host_groups])

        # write the yaml into a (secure) temporary file
        f, playbook_file = tempfile.mkstemp()
        os.write(f, playbook_yaml)
        os.close(f)

        # call ansible using a subprocess
        args = ['ansible-playbook', '--inventory=%s' % self.inventory_file, playbook_file]
        subprocess.call(args)

        # remove the temporary playbook file
        os.remove(playbook_file)