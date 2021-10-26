# automate-study

The purpose is to provide a high-capacity GPU machine in a dynamic way, meaning it can be started and stopped easily, and files can be stored in a persistent file system (which remains when the GPU machine is destroyed).
 
Currently, the GPU machine is specified to be the Azure compute machine: `Standard_ND40rs_v2`.
 
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
