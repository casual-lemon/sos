# This file is part of the sos project: https://github.com/sosreport/sos
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions of
# version 2 of the GNU General Public License.
#
# See the LICENSE file in the source distribution for further information.

from sos.plugins import Plugin, RedHatPlugin, DebianPlugin, UbuntuPlugin


class RabbitMQ(Plugin, RedHatPlugin, DebianPlugin, UbuntuPlugin):
    """RabbitMQ messaging service
    """
    plugin_name = 'rabbitmq'
    profiles = ('services',)
    var_puppet_gen = "/var/lib/config-data/puppet-generated/rabbitmq"
    files = (
        '/etc/rabbitmq/rabbitmq.conf',
        var_puppet_gen + '/etc/rabbitmq/rabbitmq.config'
    )
    packages = ('rabbitmq-server',)
    """ regardless of given status for any container(docker,lxc, etc) , collect logs or data for any rabbitmq service"""
    def setup(self):
        container_status = self.exec_cmd(
            "docker ps --format='{{ .Image}}'"
        )
        in_container = False
        container_id = []
        if container_status['status'] == 0:
            for line in container_status['output'].splitlines():
                if line.startswith("rabbitmq"):
                    in_container = True
                    con = self.exec_cmd(
                        "docker ps --format='{{ .ID}}'"
                    )
                    container_id.append(con['output'].splitlines())

        if in_container:
            for container in container_id:
                self.add_cmd_output('docker logs {0} '.format(container))
                self.add_cmd_output('docker exec -t {0} rabbitmqctl report'.format(container))
                self.add_cmd_output('docker exec -t {0} rabbitmqctl list_unresponsive_queues'.format(container))
                self.add_cmd_output('docker exec -t {0} rabbitmqctl list_queues'.format(container))
        else:
            self.add_cmd_output("rabbitmqctl report")
            self.add_cmd_output("rabbitmqctl list_queues")
            self.add_cmd_output("rabbitmqctl list_unresponsive_queues")

        self.add_copy_spec([
            "/etc/rabbitmq/*",
            self.var_puppet_gen + "/etc/rabbitmq/*",
            self.var_puppet_gen + "/etc/security/limits.d/",
            self.var_puppet_gen + "/etc/systemd/"
        ])
        self.add_copy_spec([
            "/var/log/rabbitmq/*",
        ])

    def postproc(self):
        self.do_file_sub("/etc/rabbitmq/rabbitmq.conf",
                         r"(\s*default_pass\s*,\s*)\S+", r"\1<<***>>},")

# vim: set et ts=4 sw=4 :
