# This brings up a GPU machine on Azure, with Role to access File Share

import base64
from pulumi import Config, Output, export
import pulumi_azure_native as azure_native
import pulumi_azure_native.compute as compute
import pulumi_azure_native.network as network
import pulumi_azure_native.resources as resources

# We are not using passwords, we are using key-pairs, configured later below
#config = Config()
#username = config.require("username")
#password = config.require("password")

# Basic information about the Azure account
sub="d818cbed-274b-4240-9872-8761fe9e488c"
storageAccountName="riseaicenter9576892428"
resource_group_name_storage="rise-ai-center"

# Create a new resource group for this VM
resource_group_name_base="rise-ai-center"
resource_group_location="westeurope"
resource_group = resources.ResourceGroup(resource_group_name_base, location=resource_group_location)

# Create resources for the VM
net = network.VirtualNetwork(
    "gpu-network",
    resource_group_name=resource_group.name,
    address_space=network.AddressSpaceArgs(
        address_prefixes=["10.0.0.0/16"],
    ),
    subnets=[network.SubnetArgs(
        name="default",
        address_prefix="10.0.1.0/24",
    )])

public_ip = network.PublicIPAddress(
    "gpu-ip",
    resource_group_name=resource_group.name,
    public_ip_allocation_method=network.IPAllocationMethod.DYNAMIC)

network_iface = network.NetworkInterface(
    "gpu-nic",
    resource_group_name=resource_group.name,
    ip_configurations=[network.NetworkInterfaceIPConfigurationArgs(
        name="webserveripcfg",
        subnet=network.SubnetArgs(id=net.subnets[0].id),
        private_ip_allocation_method=network.IPAllocationMethod.DYNAMIC,
        public_ip_address=network.PublicIPAddressArgs(id=public_ip.id),
    )])

init_script = """
#!/bin/bash
touch test.txt

"""
# added the identity= part to trigger the creation of MSI (Managed System Identity) which is used in the Role Assignment
vm = compute.VirtualMachine(
    "gpu",
    identity=compute.VirtualMachineIdentityArgs(type="SystemAssigned") ,
    resource_group_name=resource_group.name,
    network_profile=compute.NetworkProfileArgs(
        network_interfaces=[
            compute.NetworkInterfaceReferenceArgs(id=network_iface.id),
        ],
    ),
    hardware_profile=compute.HardwareProfileArgs(
        vm_size="Standard_ND40rs_v2",
    ),
    os_profile=compute.OSProfileArgs(
        admin_username="azureuser",
        computer_name="gpu",
        custom_data=base64.b64encode(init_script.encode("ascii")).decode("ascii"),
        linux_configuration=azure_native.compute.LinuxConfigurationArgs(
            disable_password_authentication=True,
            ssh=azure_native.compute.SshConfigurationArgs(
                public_keys=[
                    azure_native.compute.SshPublicKeyArgs(
                        key_data="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDBCu0s5YNk4iA/ONZP5CS549sz73VixHbJI2hCj2bcm3M8soYQJGfmHArSYWTPuf1vF24ltcF1n7ZUua4VLA9iajX5GZDkrl4MAeHTSSWtRBNPG2Ss/TqqMNnNjJswLELg40WqU/xB710VWy2Fov1vG9wOx9+iMd+ZlDq8W3Pk3InpTkWhysu3Inech/Y3kLFvJJNlNoSn7exLw53xTzOOAs5XIXMMCbQtG0dBmalU/arKLaPwHrg6klMcZodM2NtotOR6JcLtVIAnzJHwG5EFFX/s05/OWCLd+lFNagrSgQ/JlPdDW8nm/KS8gFGruaXGS2NpSgcbU2UibiH+l1VlTkpT3NRcTVNFq8fLfKt0k5wMOE5iAghRsQu0Nce1SEDcNubzg0VywkSlqxJJBqhibXu8FN6nZaF54DtOsCsHYIPROaq93jJ3OjKx77pWEb7aSXaexN0BhXjzMjEnTDtVw3ShMe5EZ4loiMEbpjbJRfMNvRn9bpSnx2X8hea+q+SNWoSD/nrjVm7W5eYw8LG/mOmFxWRxXPbR/vjqK+u7GyTpH2Z+cRLTi3UUmnzc8G6gal93ezw+b4VgxoWfgU8ncttsEOdI18bpzptcaswNr7HBeg/mURzuTq3kUDozKmoXEsIe/lMf3V64DdFde172AeBJSr5nOpeinRDXIRraIQ==",
                        path="/home/azureuser/.ssh/authorized_keys"),                    
                    azure_native.compute.SshPublicKeyArgs(
                        key_data="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDjhWR1/QifylSFVt+Bm5cK/nLi62dR9HhmNGj+hbvmZwxM5+aZV2QPtUgPj/CVURL6HGxzSsdMDt8jzbRxPkEQCIL5btCAseZ9yqwdK+zfTfNBy/lyZGicifL8iROB2gpx9PUWufFpLWcCKQITSje7Esj1OLE9tat8ncEjrkf2ILJxbs5IXRUHNNQPoEpxty4pw9Lm8KwuR/v2FyWvQyUr8q/luM3HesRBZs+OlYBluylGenttyk+lI9ELseJpzUd5Ccc7Ks5J3Tdlc/DXAt5nblDvHpQO1469q/BdAmbrUKVrachgwzq2blRMCiX1LJiVqrKqFlT1TsrVo1hSoDQN",
                        path="/home/azureuser/.ssh/authorized_keys")
                ],
            ),
        ),
    ),
    storage_profile=compute.StorageProfileArgs(
        os_disk=compute.OSDiskArgs(
            create_option=compute.DiskCreateOptionTypes.FROM_IMAGE,
            name="gpuOSDisk",
        ),
        image_reference=compute.ImageReferenceArgs(
            publisher="canonical",
            offer="UbuntuServer",
            sku="18_04-lts-gen2",
            version="latest",
        ),
    )
)

# Assign Key Operations rights to the VM for the Storage Account 

# Pulumi has special constructs for Input and Output to handle asynchronous behavior
# so if i want to access the result of the resource_group creation above and use it in a role assignment scope, i need to do this:
#scope = Output.concat("subscriptions/", sub, "/resourceGroups/", resource_group.name, "/providers/Microsoft.Storage/storageAccounts/",storageAccountName)
scope="subscriptions/"+sub+"/resourceGroups/"+resource_group_name_storage+"/providers/Microsoft.Storage/storageAccounts/"+storageAccountName
print(scope)
role_definition_id="/subscriptions/"+sub+"/providers/Microsoft.Authorization/roleDefinitions/81a9662b-bebf-436f-a333-f67b29880f12"

role_assignment = azure_native.authorization.RoleAssignment("roleAssignment",
    principal_id=vm.identity.principal_id,
    principal_type="ServicePrincipal",
#    role_assignment_name="05c5a614-a7d6-4502-b150-c2fb455033ff",
    role_definition_id=role_definition_id,
    scope=scope)

# get the resulting resource identities (such as VM public IP address) using the Pulumi Output construct
combined_output = Output.all(vm.id, public_ip.name, resource_group.name)
public_ip_addr = combined_output.apply(
    lambda lst: network.get_public_ip_address(
        public_ip_address_name=lst[1], 
        resource_group_name=lst[2]))
export("public_ip", public_ip_addr.ip_address)
export("principal_id", vm.identity.principal_id)
