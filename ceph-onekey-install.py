#!/usr/bin/env python

import os
import time
import socket

import config


def exec_cmd(cmd):
    print cmd
    # os.system(cmd)


def ssh_cmd(host, cmd):
    remote_cmd = 'ssh ' + host + " " + cmd
    exec_cmd(remote_cmd)


def scp_cmd(host, src, dst):
    cmd = "scp -r " + src + " " + host + ":" + dst
    exec_cmd(cmd)


def pre_check():
    current_hostname = socket.gethostname()
    if current_hostname != config.host_to_deploy:
        print("current hostname [{0}] is not the host [{1}] to "
              "deploy".format(current_hostname, config.host_to_deploy))
        exit(-1)


def hosts_config():
    config_str = ""
    for host in config.hosts:
        config_str += config.host_ip_dict[host] + " " + host + "\n"

    f = open(config.hosts_path, 'a')
    f.write(config_str)
    f.close()


def ssh_no_password():
    exec_cmd("rm -rf /root/.ssh/")
    cmd = 'ssh-keygen -t rsa -f /root/.ssh/id_rsa -q -N ""'
    exec_cmd(cmd)
    for host in config.hosts:
        if host != config.host_to_deploy:
            exec_cmd("ssh-copy-id " + host)


def generate_local_yum():
    yum_path = config.yum_path
    config_str = "[ceph]\n"
    config_str += "name=ceph\n"
    config_str += "baseurl=file://" + config.ceph_rpm_path + "\n"
    config_str += "gpgcheck=0\n"
    config_str += "enabled=1\n"

    f = open(yum_path, 'wb')
    f.write(config_str)
    f.close()


def yum_config():
    # local yum config
    cmd = "createrepo " + config.ceph_rpm_path
    exec_cmd(cmd)
    generate_local_yum()

    # remote yum config
    for host in config.hosts:
        # scp ceph rpm to remote
        scp_cmd(host, config.ceph_rpm_path, config.ceph_rpm_path)
        # remote createrepo
        ssh_cmd(host, cmd)
        # scp ceph.repo to remote
        scp_cmd(host, config.yum_path, config.yum_path)


def pre_install():
    pre_check()
    hosts_config()
    ssh_no_password()
    yum_config()


def ceph_deploy_tool_install():
    exec_cmd("yum -y install ceph-deploy")
    exec_cmd("mkdir -p " + config.deploy_dir)
    exec_cmd("cd " + config.deploy_dir)


def __generate_node_str(nodes):
    nodes_str = ""
    for node in nodes:
        nodes_str += node + " "
    return nodes_str


def ceph_deploy_new():
    exec_cmd("ceph-deploy new " + __generate_node_str(config.monitors))
    cmd = 'echo "public network = %s" >> %s%s' \
          % (config.public_network, config.deploy_dir, config.ceph_conf)
    exec_cmd(cmd)
    cmd = 'echo "cluster network = %s" >> %s%s' \
          % (config.cluster_network, config.deploy_dir, config.ceph_conf)
    exec_cmd(cmd)


def uninstall_unnecessary_rpm():
    cmd = "yum -y remove selinux-policy-targeted"
    exec_cmd(cmd)
    for host in config.hosts:
        if host != config.host_to_deploy:
            ssh_cmd(host, cmd)


def ceph_deploy_install():
    exec_cmd("ceph-deploy install " + __generate_node_str(config.hosts))
    uninstall_unnecessary_rpm()


def ceph_deploy_create_moninital():
    exec_cmd("ceph-deploy mon create-initial")


def ceph_deploy_admin():
    exec_cmd("ceph-deploy admin " + __generate_node_str(config.hosts))


def ceph_deploy_mgr():
    exec_cmd("ceph-deploy mgr create " + __generate_node_str(config.monitors))


def ceph_deploy_osd():
    for host in config.hosts:
        for disk in config.host_disks_dict[host]:
            exec_cmd("ceph-deploy osd create --data " + disk + " " + host)


def ceph_deploy():
    ceph_deploy_tool_install()
    ceph_deploy_new()
    ceph_deploy_install()
    ceph_deploy_create_moninital()
    ceph_deploy_admin()
    ceph_deploy_mgr()
    ceph_deploy_osd()


def main():
    #pre_install()
    ceph_deploy()


if __name__ == '__main__':
    main()

