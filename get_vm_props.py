
import pyvim
import pyVmomi
import ssl
import requests
import re
import sys
import argparse
from pyvim.connect import SmartConnect, Disconnect
from pyVmomi import vim, vmodl

parser = argparse.ArgumentParser()
parser.add_argument("--vcenter",
                    choices=["server1","server2"],
                    required=True, type=str, help="vcenter address")

args = parser.parse_args()
vcenter = args.vcenter

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
ssl_context.verify_mode = ssl.CERT_NONE
service_instance = SmartConnect(host=vcenter, user="user@vsphere.local", pwd='pass123',sslContext=ssl_context)
content=service_instance.content

 
# Method that populates objects of type vimtype
content = service_instance.RetrieveContent()
container = content.rootFolder
vm_viewType = [vim.VirtualMachine]
vm_containerView = content.viewManager.CreateContainerView(content.rootFolder, vm_viewType, True)
vm_children = vm_containerView.view
host_viewType = [vim.HostSystem]
host_containerView = content.viewManager.CreateContainerView(content.rootFolder, host_viewType, True)
host_children = host_containerView.view
net_viewType = [vim.Network]
net_containerView = content.viewManager.CreateContainerView(content.rootFolder, net_viewType, True)
net_children = net_containerView.view
vm_containerView.Destroy()
host_containerView.Destroy()
net_containerView.Destroy()

vm_props_list = []
vm_disk_list = []
vm_net_list = []
vm_host_disk_list = []



class vm_class(object):
    def __init__(self, propName=None, numCpu=None, memorySizeMB=None, propVMHost=None, propPowerState=None, propIpAddress=None, propMacAddress=None, propNetwork=None, guestFullName=None, propVmPathName=None, toolsStatus=None, toolsRunningStatus=None, uptimeSeconds=None, hwVersion=None):
        self.propName = propName
        self.numCpu = numCpu
        self.memorySizeMB = memorySizeMB
        self.propVMHost = propVMHost
        self.propPowerState = propPowerState
        self.propIpAddress = propIpAddress
        self.propMacAddress = propMacAddress
        self.propNetwork = propNetwork
        self.guestFullName = guestFullName
        self.propVmPathName = propVmPathName
        self.toolsStatus = toolsStatus
        self.toolsRunningStatus = toolsRunningStatus
        self.uptimeSeconds =  uptimeSeconds
        self.hwVersion = hwVersion

class vm_disk_class(object):
    def __init__(self, diskName=None, disk=None, capacity=None, diskVmPathName=None, diskPowerState=None, diskVMHost=None):
        self.diskName = diskName
        self.disk = disk
        self.capacity = capacity
        self.diskVmPathName = diskVmPathName
        self.diskPowerState = diskPowerState
        self.diskVMHost = diskVMHost
        
class vm_net_class(object):
    def __init__(self, netName=None, netIpAddress=None, netMacAddress=None, netNetwork=None, netPowerState=None, netVMHost=None):
        self.netName = netName
        self.netIpAddress = netIpAddress
        self.netMacAddress = netMacAddress
        self.netNetwork = netNetwork
        self.netPowerState = netPowerState
        self.netVMHost = netVMHost
        
for child in vm_children:
    vm_ip = ""
    vm_mac = ""
    #print(child.summary.config.name + "_ip")
    vm_host_raw = child.summary.runtime.host
    host_name = vm_host_raw.summary.config.name
    for nic in child.guest.net:
        if (nic.deviceConfigId >= 4000) and (nic.deviceConfigId < 5000):
            if nic.ipConfig is not None:
                for ip in nic.ipConfig.ipAddress:
                    if nic.network is not None:
                        vm_network = nic.network
                    else:
                        vm_network = "na"  
                        #if ip.state == 'preferred':
                    vm_ip = ip.ipAddress
                    vm_mac = nic.macAddress          
                    vm_net_list.append(vm_net_class(child.summary.config.name,
                        vm_ip,
                        vm_mac,
                        vm_network,
                        child.summary.runtime.powerState,
                        host_name))
#print('done')
for child in vm_children:
    #print(child.summary.config.name + "_props")    
    vm_host_raw = child.summary.runtime.host
    host_name = vm_host_raw.summary.config.name
    for nic in child.guest.net:
        if nic.deviceConfigId == 4000:
            if nic.ipConfig is not None:
                for ip in nic.ipConfig.ipAddress:              
                    if ip.state == 'preferred':
                        vm_ip = ip.ipAddress
                        vm_mac = nic.macAddress
                        vm_network = nic.network 
            else:
                vm_ip = "na"
                vm_mac = "na"                 
    vm_props_list.append(vm_class(child.summary.config.name,
        child.summary.config.numCpu,
        child.summary.config.memorySizeMB,
        host_name,
        child.summary.runtime.powerState,
        vm_ip,
        vm_mac,
        vm_network,
        child.summary.config.guestFullName,
        child.summary.config.vmPathName,
        child.summary.guest.toolsStatus,
        child.summary.guest.toolsRunningStatus,
        child.summary.quickStats.uptimeSeconds,
        child.config.version))
    for each_vm_hardware in child.config.hardware.device:
        if (each_vm_hardware.key >= 2000) and (each_vm_hardware.key < 3000):
            vm_disk_list.append(vm_disk_class(child.summary.config.name,
                each_vm_hardware.deviceInfo.label,
                ('{:.1f}GB'.format(each_vm_hardware.capacityInKB/1024/1024)),
                child.summary.config.vmPathName,
                child.summary.runtime.powerState,
                host_name))
Disconnect(service_instance)


def main():
    for vm_guest in vm_props_list:
        print(vm_guest.__dict__)
    for vm_guest in vm_disk_list:
        print(vm_guest.__dict__)
    for vm_guest in vm_net_list:
        print(vm_guest.__dict__)
main()




