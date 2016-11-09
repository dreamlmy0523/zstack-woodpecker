'''

Create an unified test_stub to share test operations

@author: Youyk
'''

import os
import subprocess
import time
import uuid

import zstacklib.utils.ssh as ssh
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
import zstackwoodpecker.zstack_test.zstack_test_volume as zstack_volume_header
import zstackwoodpecker.zstack_test.zstack_test_eip as zstack_eip_header
import zstackwoodpecker.zstack_test.zstack_test_vip as zstack_vip_header
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.account_operations as acc_ops

test_file = '/tmp/test.img'
TEST_TIME = 120
original_root_password = "password"

#def create_vlan_vm_with_volume(l3_name=None, disk_offering_uuids=None, disk_number=None, session_uuid = None):
#    if not disk_offering_uuids:
#        disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'))
#        disk_offering_uuids = [disk_offering.uuid]
#        if disk_number:
#            for i in range(disk_number - 1):
#                disk_offering_uuids.append(disk_offering.uuid)
#
#    return create_vlan_vm(l3_name, disk_offering_uuids, \
#            session_uuid = session_uuid)
#
#def create_vlan_vm(l3_name=None, disk_offering_uuids=None, system_tags=None, session_uuid = None, instance_offering_uuid = None):
#    image_name = os.environ.get('imageName_net')
#    if not l3_name:
#        l3_name = os.environ.get('l3VlanNetworkName1')
#
#    return create_vm('vlan_vm', image_name, l3_name, \
#            disk_offering_uuids=disk_offering_uuids, system_tags=system_tags, \
#            instance_offering_uuid = instance_offering_uuid,
#            session_uuid = session_uuid)

def create_vm(vm_name='virt-vm', \
        image_name = None, \
        l3_name = None, \
        instance_offering_uuid = None, \
        host_uuid = None, \
        disk_offering_uuids=None, system_tags=None, \
        root_password=None, session_uuid = None):


    if not image_name:
        image_name = os.environ.get('imageName_net') 
    else:
        image_name = os.environ.get(image_name)
    if not l3_name:
        l3_name = os.environ.get('l3PublicNetworkName')

    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    if not instance_offering_uuid:
	instance_offering_name = os.environ.get('instanceOfferingName_m')
        instance_offering_uuid = test_lib.lib_get_instance_offering_by_name(instance_offering_name).uuid

    vm_creation_option = test_util.VmOption()
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name(vm_name)
    vm_creation_option.set_system_tags(system_tags)
    vm_creation_option.set_data_disk_uuids(disk_offering_uuids)
    if root_password:
        vm_creation_option.set_root_password(root_password)
    if host_uuid:
        vm_creation_option.set_host_uuid(host_uuid)
    if session_uuid:
        vm_creation_option.set_session_uuid(session_uuid)

    vm = zstack_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm 


def create_user_in_vm(vm, username, password):
    """
    create non-root user with password setting
    """
    global original_root_password

    vm_ip = vm.vmNics[0].ip

    cmd = "adduser %s" % (username)
    ret, output, stderr = ssh.execute(cmd, vm_ip, "root", original_root_password, False, 22)
    if ret != 0:
        test_util.test_fail("the user created failure")

    cmd = "echo -e \'%s\n%s\' | passwd %s" % (password, password, username)
    ret, output, stderr = ssh.execute(cmd, vm_ip, "root", original_root_password, False, 22)
    if ret != 0:
        test_util.test_fail("set non-root password failure")


#def create_volume(volume_creation_option=None, session_uuid = None):
#    if not volume_creation_option:
#        disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'))
#        volume_creation_option = test_util.VolumeOption()
#        volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
#        volume_creation_option.set_name('vr_test_volume')
#
#    volume_creation_option.set_session_uuid(session_uuid)
#    volume = zstack_volume_header.ZstackTestVolume()
#    volume.set_creation_option(volume_creation_option)
#    volume.create()
#    return volume
#
#def make_ssh_no_password(vm_inv):
#    vm_ip = vm_inv.vmNics[0].ip
#    ssh.make_ssh_no_password(vm_ip, test_lib.lib_get_vm_username(vm_inv), \
#            test_lib.lib_get_vm_password(vm_inv))
#
#def execute_shell_in_process(cmd, timeout=10, logfd=None):
#    if not logfd:
#        process = subprocess.Popen(cmd, executable='/bin/sh', shell=True, universal_newlines=True)
#    else:
#        process = subprocess.Popen(cmd, executable='/bin/sh', shell=True, stdout=logfd, stderr=logfd, universal_newlines=True)
#
#    start_time = time.time()
#    while process.poll() is None:
#        curr_time = time.time()
#        TEST_TIME = curr_time - start_time
#        if TEST_TIME > timeout:
#            process.kill()
#            test_util.test_logger('[shell:] %s timeout ' % cmd)
#            return False
#        time.sleep(1)
#
#    test_util.test_logger('[shell:] %s is finished.' % cmd)
#    return process.returncode
#
#def create_test_file(vm_inv, bandwidth):
#    '''
#    the bandwidth is for calculate the test file size, 
#    since the test time should be finished in 60s. 
#    bandwidth unit is KB.
#    '''
#    vm_ip = vm_inv.vmNics[0].ip
#    file_size = bandwidth * TEST_TIME
#    seek_size = file_size / 1024 - 1
#    timeout = 10
#
#    ssh_cmd = 'ssh  -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
#    cmd = '%s "dd if=/dev/zero of=%s bs=1M count=1 seek=%d"' \
#            % (ssh_cmd, test_file, seek_size)
#    if  execute_shell_in_process(cmd, timeout) != 0:
#        test_util.test_fail('test file is not created')
#
#def test_scp_vm_outbound_speed(vm_inv, bandwidth):
#    '''
#    bandwidth unit is KB
#    '''
#    timeout = TEST_TIME + 30
#    vm_ip = vm_inv.vmNics[0].ip
#    cmd = 'scp -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s:%s /dev/null' \
#            % (vm_ip, test_file)
#    start_time = time.time()
#    if execute_shell_in_process(cmd, timeout) != 0:
#        test_util.test_fail('scp test file failed')
#
#    end_time = time.time()
#
#    scp_time = end_time - start_time
#    if scp_time < TEST_TIME:
#        test_util.test_fail('network outbound QOS test file failed, since the scp time: %d is smaller than the expected test time: %d. It means the bandwidth limitation: %d KB/s is not effect. ' % (scp_time, TEST_TIME, bandwidth))
#    else:
#        test_util.test_logger('network outbound QOS test file pass, since the scp time: %d is bigger than the expected test time: %d. It means the bandwidth limitation: %d KB/s is effect. ' % (scp_time, TEST_TIME, bandwidth))
#
#    return True
#
#def test_scp_vm_inbound_speed(vm_inv, bandwidth):
#    '''
#    bandwidth unit is KB
#    '''
#    timeout = TEST_TIME + 30
#    vm_ip = vm_inv.vmNics[0].ip
#    file_size = bandwidth * TEST_TIME
#    seek_size = file_size / 1024 - 1
#    cmd = 'dd if=/dev/zero of=%s bs=1M count=1 seek=%d' \
#            % (test_file, seek_size)
#    os.system(cmd)
#    cmd = 'scp -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s %s:/dev/null' \
#            % (test_file, vm_ip)
#    start_time = time.time()
#    if execute_shell_in_process(cmd, timeout) != 0:
#        test_util.test_fail('scp test file failed')
#
#    end_time = time.time()
#    os.system('rm -f %s' % test_file)
#
#    scp_time = end_time - start_time
#    if scp_time < TEST_TIME:
#        test_util.test_fail('network inbound QOS test file failed, since the scp time: %d is smaller than the expected test time: %d. It means the bandwidth limitation: %d KB/s is not effect. ' % (scp_time, TEST_TIME, bandwidth))
#    else:
#        test_util.test_logger('network inbound QOS test file pass, since the scp time: %d is bigger than the expected test time: %d. It means the bandwidth limitation: %d KB/s is effect. ' % (scp_time, TEST_TIME, bandwidth))
#
#    return True
#
#def install_fio(vm_inv):
#    timeout = TEST_TIME + 30 
#    vm_ip = vm_inv.vmNics[0].ip
#
#    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
#    cmd = '%s "which fio || yum install -y fio"' \
#            % (ssh_cmd)
#    if  execute_shell_in_process(cmd, timeout) != 0:
#        test_util.test_fail('fio installation failed.')
#
#def test_fio_iops(vm_inv, iops):
#    def cleanup_log():
#        logfd.close()
#        os.system('rm -f %s' % tmp_file)
#
#    timeout = TEST_TIME + 120
#    vm_ip = vm_inv.vmNics[0].ip
#
#    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
#    cmd1 = """%s "fio -ioengine=libaio -bs=4k -direct=1 -thread -rw=write -size=256M -filename=/tmp/test1.img -name='EBS 4k write' -iodepth=64 -runtime=60 -numjobs=4 -group_reporting|grep iops" """ \
#            % (ssh_cmd)
#    cmd2 = """%s "fio -ioengine=libaio -bs=4k -direct=1 -thread -rw=write -size=256M -filename=/tmp/test2.img -name='EBS 4k write' -iodepth=64 -runtime=60 -numjobs=4 -group_reporting|grep iops" """ \
#            % (ssh_cmd)
#
#
#    tmp_file = '/tmp/%s' % uuid.uuid1().get_hex()
#    logfd = open(tmp_file, 'w', 0)
#    #rehearsal
#    execute_shell_in_process(cmd1, timeout)
#
#    if  execute_shell_in_process(cmd2, timeout, logfd) != 0:
#        logfd.close()
#        logfd = open(tmp_file, 'r')
#        test_util.test_logger('test_fio_bandwidth log: %s ' % '\n'.join(logfd.readlines()))
#        cleanup_log()
#        test_util.test_fail('fio test failed.')
#
#    logfd.close()
#    logfd = open(tmp_file, 'r')
#    result_lines = logfd.readlines()
#    test_util.test_logger('test_fio_bandwidth log: %s ' % '\n'.join(result_lines))
#    bw=0
#    for line in result_lines: 
#        if  'iops' in line:
#            test_util.test_logger('test_fio_bandwidth: %s' % line)
#            results = line.split()
#            for result in results:
#                if 'iops=' in result:
#                    bw = int(float(result[5:]))
#
#    #cleanup_log()
#    if bw == 0:
#        test_util.test_fail('Did not get bandwidth for fio test')
#
#    if bw == iops or bw < (iops - 10):
#        test_util.test_logger('disk iops: %s is <= setting: %s' % (bw, iops))
#        return True
#    else:
#        test_util.test_logger('disk iops :%s is not same with %s' % (bw, iops))
#        test_util.test_fail('fio bandwidth test fails')
#        return False
#
#def test_fio_bandwidth(vm_inv, bandwidth, path = '/tmp'):
#    def cleanup_log():
#        logfd.close()
#        os.system('rm -f %s' % tmp_file)
#
#    timeout = TEST_TIME + 120
#    vm_ip = vm_inv.vmNics[0].ip
#
#    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
#    cmd1 = """%s "fio -ioengine=libaio -bs=1M -direct=1 -thread -rw=write -size=100M -filename=%s/test1.img -name='EBS 1M write' -iodepth=64 -runtime=60 -numjobs=4 -group_reporting|grep iops" """ \
#            % (ssh_cmd, path)
#    cmd2 = """%s "fio -ioengine=libaio -bs=1M -direct=1 -thread -rw=write -size=900G -filename=%s/test2.img -name='EBS 1M write' -iodepth=64 -runtime=60 -numjobs=4 -group_reporting|grep iops" """ \
#            % (ssh_cmd, path)
#
#
#    tmp_file = '/tmp/%s' % uuid.uuid1().get_hex()
#    logfd = open(tmp_file, 'w', 0)
#    #rehearsal
#    execute_shell_in_process(cmd1, timeout)
#
#    if  execute_shell_in_process(cmd2, timeout, logfd) != 0:
#        logfd.close()
#        logfd = open(tmp_file, 'r')
#        test_util.test_logger('test_fio_bandwidth log: %s ' % '\n'.join(logfd.readlines()))
#        cleanup_log()
#        test_util.test_fail('fio test failed.')
#
#    logfd.close()
#    logfd = open(tmp_file, 'r')
#    result_lines = logfd.readlines()
#    test_util.test_logger('test_fio_bandwidth log: %s ' % '\n'.join(result_lines))
#    bw=0
#    for line in result_lines: 
#        if  'iops' in line:
#            test_util.test_logger('test_fio_bandwidth: %s' % line)
#            results = line.split()
#            for result in results:
#                if 'bw=' in result:
#                    bw = int(float(result[3:].split('KB')[0]))
#
#    #cleanup_log()
#    if bw == 0:
#        test_util.test_fail('Did not get bandwidth for fio test')
#
#    bw_up_limit = bandwidth/1024 + 10240
#    bw_down_limit = bandwidth/1024 - 10240
#    if bw > bw_down_limit and bw < bw_up_limit:
#        test_util.test_logger('disk bandwidth:%s is between %s and %s' \
#                % (bw, bw_down_limit, bw_up_limit))
#        return True
#    else:
#        test_util.test_logger('disk bandwidth:%s is not between %s and %s' \
#                % (bw, bw_down_limit, bw_up_limit))
#        test_util.test_fail('fio bandwidth test fails')
#        return False
#
#def create_volume(volume_creation_option=None, session_uuid = None):
#    if not volume_creation_option:
#        disk_offering_uuid = res_ops.query_resource(res_ops.DISK_OFFERING)[0].uuid
#        volume_creation_option = test_util.VolumeOption()
#        volume_creation_option.set_disk_offering_uuid(disk_offering_uuid)
#        volume_creation_option.set_name('vr_test_volume')
#
#    volume_creation_option.set_session_uuid(session_uuid)
#    volume = zstack_volume_header.ZstackTestVolume()
#    volume.set_creation_option(volume_creation_option)
#    volume.create()
#    return volume
#
#def migrate_vm_to_random_host(vm, timeout = None):
#    test_util.test_dsc("migrate vm to random host")
#    target_host = test_lib.lib_find_random_host(vm.vm)
#    current_host = test_lib.lib_find_host_by_vm(vm.vm)
#    vm.migrate(target_host.uuid, timeout)
#
#    new_host = test_lib.lib_get_vm_host(vm.vm)
#    if not new_host:
#        test_util.test_fail('Not find available Hosts to do migration')
#
#    if new_host.uuid != target_host.uuid:
#        test_util.test_fail('[vm:] did not migrate from [host:] %s to target [host:] %s, but to [host:] %s' % (vm.vm.uuid, current_host.uuid, target_host.uuid, new_host.uuid))
#    else:
#        test_util.test_logger('[vm:] %s has been migrated from [host:] %s to [host:] %s' % (vm.vm.uuid, current_host.uuid, target_host.uuid))
#
#def create_eip(eip_name=None, vip_uuid=None, vnic_uuid=None, vm_obj=None, \
#        session_uuid = None):
#    if not vip_uuid:
#        l3_name = os.environ.get('l3PublicNetworkName')
#        l3_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
#        vip_uuid = net_ops.acquire_vip(l3_uuid).uuid
#
#    eip_option = test_util.EipOption()
#    eip_option.set_name(eip_name)
#    eip_option.set_vip_uuid(vip_uuid)
#    eip_option.set_vm_nic_uuid(vnic_uuid)
#    eip_option.set_session_uuid(session_uuid)
#    eip = zstack_eip_header.ZstackTestEip()
#    eip.set_creation_option(eip_option)
#    if vnic_uuid and not vm_obj:
#        test_util.test_fail('vm_obj can not be None in create_eip() API, when setting vm_nic_uuid.')
#    eip.create(vm_obj)
#    return eip
#
#def create_vip(vip_name=None, l3_uuid=None, session_uuid = None):
#    if not vip_name:
#        vip_name = 'test vip'
#    if not l3_uuid:
#        l3_name = os.environ.get('l3PublicNetworkName')
#        l3_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
#
#    vip_creation_option = test_util.VipOption()
#    vip_creation_option.set_name(vip_name)
#    vip_creation_option.set_l3_uuid(l3_uuid)
#    vip_creation_option.set_session_uuid(session_uuid)
#
#    vip = zstack_vip_header.ZstackTestVip()
#    vip.set_creation_option(vip_creation_option)
#    vip.create()
#
#    return vip
#
#def attach_mount_volume(volume, vm, mount_point):
#    volume.attach(vm)
#    import tempfile
#    script_file = tempfile.NamedTemporaryFile(delete=False)
#    script_file.write('''
#mkdir -p %s
#device="/dev/`ls -ltr --file-type /dev | grep disk | awk '{print $NF}' | grep -v '[[:digit:]]' | tail -1`"
#mount ${device}1 %s
#''' % (mount_point, mount_point))
#    script_file.close()
#
#    vm_inv = vm.get_vm()
#    if not test_lib.lib_execute_shell_script_in_vm(vm_inv, script_file.name):
#        test_util.test_fail("mount operation failed in [volume:] %s in [vm:] %s" % (volume.get_volume().uuid, vm_inv.uuid))
#
#        os.unlink(script_file.name)

def share_admin_resource(account_uuid_list):
    instance_offerings = res_ops.get_resource(res_ops.INSTANCE_OFFERING)
    for instance_offering in instance_offerings:
        acc_ops.share_resources(account_uuid_list, [instance_offering.uuid])
    cond = res_ops.gen_query_conditions('mediaType', '!=', 'ISO')
    images =  res_ops.query_resource(res_ops.IMAGE, cond)
    for image in images:
        acc_ops.share_resources(account_uuid_list, [image.uuid])
    l3net_uuid = res_ops.get_resource(res_ops.L3_NETWORK)[0].uuid
    root_disk_uuid = test_lib.lib_get_disk_offering_by_name(os.environ.get('rootDiskOfferingName')).uuid
    data_disk_uuid = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName')).uuid
    acc_ops.share_resources(account_uuid_list, [l3net_uuid, root_disk_uuid, data_disk_uuid])



