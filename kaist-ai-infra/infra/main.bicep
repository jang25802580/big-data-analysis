// Main Bicep template for KAIST AI PDF Chatbot Infrastructure
targetScope = 'subscription'

// Parameters
@description('Environment name (e.g., dev, staging, prod)')
@allowed([
  'dev'
  'staging'
  'prod'
])
param environment string = 'dev'

@description('Azure region for resource deployment')
param location string = 'koreacentral'

@description('Base name for resource naming')
param baseName string = 'kaist-ai-agent'

@description('Owner tag for resources')
param owner string = 'KAIST Big Data Analysis Team'

@description('Cost center tag for resources')
param costCenter string = 'KAIST-BDA'

@description('Creation date for resources')
param createdDate string = utcNow('yyyy-MM-dd')

// Variables
var resourceGroupName = '${baseName}-rg'
var tags = {
  environment: environment
  project: 'PDF Knowledge Base Chatbot'
  owner: owner
  costCenter: costCenter
  managedBy: 'azd'
  createdDate: createdDate
}

// Resource Group
resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: resourceGroupName
  location: location
  tags: tags
}

// Naming Module
module naming 'modules/naming.bicep' = {
  name: 'naming'
  scope: rg
  params: {
    baseName: baseName
    environment: environment
    locationShortCode: 'krc'
  }
}

// Storage Account Module
module storage 'modules/storage.bicep' = {
  name: 'storage-deployment'
  scope: rg
  params: {
    storageAccountName: naming.outputs.storageAccountName
    location: location
    tags: tags
    sku: 'Standard_LRS'
    accessTier: 'Hot'
    blobSoftDeleteRetentionDays: 7
    enableDefender: true
    corsAllowedOrigins: [
      'https://*.azurestaticapps.net'
      'http://localhost:3000'
      'http://localhost:5173'
    ]
  }
}

// Cosmos DB Module
module cosmos 'modules/cosmos.bicep' = {
  name: 'cosmos-deployment'
  scope: rg
  params: {
    cosmosAccountName: naming.outputs.cosmosDbAccountName
    location: location
    tags: tags
    databaseName: 'knowledgebase'
    enableFreeTier: false
    defaultTtl: 7776000 // 90 days
  }
}

// Azure Functions Module
module functions 'modules/functions.bicep' = {
  name: 'functions-deployment'
  scope: rg
  params: {
    functionAppName: naming.outputs.functionAppName
    appServicePlanName: naming.outputs.appServicePlanName
    appInsightsName: naming.outputs.appInsightsName
    logAnalyticsName: naming.outputs.logAnalyticsName
    storageAccountName: storage.outputs.storageAccountName
    location: location
    tags: tags
    cosmosEndpoint: cosmos.outputs.cosmosEndpoint
    cosmosDatabaseName: cosmos.outputs.databaseName
    keyVaultName: naming.outputs.keyVaultName
    corsAllowedOrigins: [
      'https://*.azurestaticapps.net'
      'http://localhost:3000'
      'http://localhost:5173'
    ]
  }
}

// Static Web App Module
module staticWebApp 'modules/staticwebapp.bicep' = {
  name: 'staticwebapp-deployment'
  scope: rg
  params: {
    staticWebAppName: naming.outputs.staticWebAppName
    location: 'eastasia' // Static Web Apps not available in koreacentral
    tags: tags
    functionAppHostName: functions.outputs.functionAppHostName
    sku: 'Free'
  }
}

// Key Vault and Security Module
module keyVault 'modules/keyvault.bicep' = {
  name: 'keyvault-deployment'
  scope: rg
  params: {
    keyVaultName: naming.outputs.keyVaultName
    location: location
    tags: tags
    functionAppPrincipalId: functions.outputs.functionAppPrincipalId
    cosmosAccountName: cosmos.outputs.cosmosAccountName
    storageAccountName: storage.outputs.storageAccountName
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
  }
}

// Outputs
output resourceGroupName string = rg.name
output location string = location
output environment string = environment
output tags object = tags
output storageAccountName string = storage.outputs.storageAccountName
output blobEndpoint string = storage.outputs.blobEndpoint
output pdfContainerName string = storage.outputs.containerName
output cosmosAccountName string = cosmos.outputs.cosmosAccountName
output cosmosEndpoint string = cosmos.outputs.cosmosEndpoint
output cosmosDatabaseName string = cosmos.outputs.databaseName
output cosmosDocumentsContainer string = cosmos.outputs.documentsContainerName
output cosmosChunksContainer string = cosmos.outputs.chunksContainerName
output cosmosSessionsContainer string = cosmos.outputs.sessionsContainerName
output functionAppName string = functions.outputs.functionAppName
output functionAppHostName string = functions.outputs.functionAppHostName
output functionAppPrincipalId string = functions.outputs.functionAppPrincipalId
output appInsightsConnectionString string = functions.outputs.appInsightsConnectionString
output staticWebAppName string = staticWebApp.outputs.staticWebAppName
output staticWebAppUrl string = staticWebApp.outputs.staticWebAppUrl
output staticWebAppHostName string = staticWebApp.outputs.staticWebAppDefaultHostName
output keyVaultName string = keyVault.outputs.keyVaultName
output keyVaultUri string = keyVault.outputs.keyVaultUri
