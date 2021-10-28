#!/bin/bash

# mounts an Azure File Share to a VM
# uses the json parser jq
# assumes that this VM has the right role assigned

sudo apt -qq update
sudo apt -qq install -y jq

sub="d818cbed-274b-4240-9872-8761fe9e488c"
resourceGroupName="rise-ai-center"
storageAccountName="riseaicenter9576892428"
fileShareName="azureml-filestore-a3577153-b708-4da7-ba96-d3d8997a0cac"

# get the Azure storage account key
# assumes that this VM has the right role assigned
accessToken=$(curl -s 'http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https%3A%2F%2Fmanagement.azure.com%2F' -H Metadata:true | jq -r .access_token)
storageAccountKey=$(curl -s https://management.azure.com/subscriptions/$sub/resourceGroups/$resourceGroupName/providers/Microsoft.Storage/storageAccounts/$storageAccountName/listKeys?api-version=2016-12-01 --request POST -d "" -H "Authorization: Bearer $accessToken" | jq -r .keys[0].value)

fileStoreEndpoint=https://riseaicenter9576892428.file.core.windows.net/
httpEndpoint=$fileStoreEndpoint

# diagnostics
# smbPath=$(echo $httpEndpoint | cut -c7-$(expr length $httpEndpoint))
# fileHost=$(echo $smbPath | tr -d "/")
# nc -zvw3 $fileHost 445

smbPath=$(echo $httpEndpoint | cut -c7-$(expr length $httpEndpoint))$fileShareName

mntRoot="/mount"
mntPath="$mntRoot/$storageAccountName/$fileShareName"

# echo $smbPath $mntPath $fileHost

sudo mkdir -p $mntPath

sudo mount -t cifs $smbPath $mntPath -o username=$storageAccountName,password=$storageAccountKey,serverino,gid=1000,uid=1000
ln -s $mntPath /home/azureuser/persistent-files