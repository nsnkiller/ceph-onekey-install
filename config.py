host_to_deploy = "ceph-0"

hosts = ["ceph-0", "ceph-1", "ceph-2"]
monitors = ["ceph-0", "ceph-1", "ceph-2"]

hosts_path = "/etc/hosts"

host_password = "123123"

# dict config hostname:ip
host_ip_dict = {"ceph-0": "192.168.204.80",
                "ceph-1": "192.168.204.81",
                "ceph-2": "192.168.204.82"}


host_disks_dict = {"ceph-0": ["/dev/vdb", "/dev/vdc", "/dev/vdd"],
                   "ceph-1": ["/dev/vdb", "/dev/vdc", "/dev/vdd"],
                   "ceph-2": ["/dev/vdb", "/dev/vdc", "/dev/vdd"]}


ceph_rpm_path = "/root/ceph-luminous"
yum_path = "/etc/yum.repos.d/ceph.repo"
deploy_dir = "/root/deploy/"
ceph_conf = "ceph.conf"


public_network = "192.168.204.0/24"
cluster_network = "192.168.127.0/24"


