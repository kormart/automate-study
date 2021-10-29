# automate-study

The purpose is to provide a high-capacity GPU machine in a dynamic way, meaning it can be started and stopped easily, and files can be stored in a persistent file system (which remains when the GPU machine is destroyed).
 
Currently, the GPU machine is the Azure VM `Standard_ND40rs_v2`.
The next section is a howto for users, below comes howto for setting it up.

## Howto for users

There is a (non-GPU) VM, called `masterops`, on Azure, from where we can start and stop the GPU machine.
To login to `masterops` you have to have provided your public key separately.

    ssh -i <your key file> azureuser@<ip adress of masterops>

In the `masterops` machine, a shared file system is available in the folder `persistent-files` (complete path: `/home/azureuser/persistent-files`)

    cd ~/persistent-files
 
To start the GPU, go to the folder `azure-gpu-ops` (on the `masterops` machine) and run the command `pulumi up`:

    cd ~/azure-gpu-ops
    pulumi up

This will take a couple of minutes, but finally there will be an ip address reported. Use that to login to the GPU Machine:

    ssh -i <your key file> azureuser@<ip address of gpu machine>

On the GPU machine run the following

    curl -sS https://raw.githubusercontent.com/kormart/automate-study/main/mount_fileshare.sh | sh

The shared file system is now available on the GPU machine as well

    cd ~/persistent-files
 
To find the IP adress of a GPU machine that is already. running, run this command in the `azure-gpu-ops` folder on the `masterops` machine:

    pulumi stack output

To stop (and destroy) the GPU machine, go to the `masterops` machine again

    cd ~/azure-gpu-ops
    pulumi destroy
    

## Howto for infra engineer

The setup is using Pulumi, `pulumi.com` for automation, Infrastructure-as-Code.

On the `masterops` machine, install Pulumi

    curl -fsSL https://get.pulumi.com | sh
    
Setup Pulumi to use local filesystem `~/.pulumi` to store deployment state (this is only for non-production setups).

    pulumi login file://~
    
Install the Azure CLI

    curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

Login to your Azure subscription with

    az login
    
### Pulumi setup

To start a new Pulumi automation program, create a new folder and run `pulumi new`, follow the getting started instruction on `pulumi.com`.

For this project, the file `__main__.py` contains Python code that uses the Pulumi SDK for Azure.

The `__main__.py` program creates a VM and assigns a Role (Storage Account Key Operations) for the VM to access the Azure File Share service within an Azure Storage Account.

### Mounting the File Share from the VM

The shell script `mount_fileshare.sh` gets the credentials for accessing the File Share, based on the fact that the Role was created for VM. And then mounts the File Share to a folder, and finally creates a symlink to a folder `~/persistent_files`.
