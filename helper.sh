
resourceGroupName="rise-ai-center"
storageAccountName="riseaicenter9576892428"
test="this is for $resourceGroupName"
storageAccountKey=$(az storage account keys list \
    --resource-group $resourceGroupName \
    --account-name $storageAccountName \
    --query "[0].value" | tr -d '"')

echo $storageAccountKey $test