'''
@author:Mengying.li
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import test_stub

vm=None

def test():
    global vm
    vm=test_stub.create_vm()
    vm.check()
    vm_inv=vm.get_vm()
    vm_uuid=vm_inv.uuid
    vm_state = vm.get_vm().state

    host_inv = test_lib.lib_find_host_by_vm(vm_inv)
    host_ip= host_inv.managementIp
    host_username=host_inv.username
    host_password=host_inv.password

    if  vm_state == 'Running':
        test_util.test_dsc('use virsh to stop vm in host')
        cmd='virsh destroy %s'% (vm_uuid)
        result=test_lib.lib_execute_ssh_cmd(host_ip, host_username, host_password, cmd, 180)
        if result == False :
           test_util.test_fail('Fail to execute cmd')
        
        vm.update()

        if vm.get_vm().state != 'Stopped':
           test_util.test_fail('VM is expected to in state stopped %s' % (vm.get_vm().state))


    elif vm_state == 'Stopped':
        test_util.test_dsc('use virsh to  start vm in host')
        cmd = 'virsh start %s' % vm_uuid
        result=test_lib.lib_execute_ssh_cmd(host_ip, host_username, host_password, cmd,180)
        if result == False:
            test_util.test_fail('Fail to execute cmd')

        vm.update()

        if vm.get_vm().state != 'Running':
            test_util.test_fail('VM is expected to in state running %s' % (vm.get_vm().state))
        
    vm.destroy()
    vm.check()
    test_util.test_pass('Test Success')

def error_cleanup():
     global vm
     if vm:
        vm.destroy()

