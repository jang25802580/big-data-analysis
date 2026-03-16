// Azure Static Web Apps module for React frontend
@description('Static Web App name')
param staticWebAppName string

@description('Location for Static Web App')
param location string

@description('Resource tags')
param tags object

@description('Function App hostname for API endpoint')
param functionAppHostName string

@description('SKU for Static Web App')
@allowed([
  'Free'
  'Standard'
])
param sku string = 'Free'

// Static Web App
resource staticWebApp 'Microsoft.Web/staticSites@2023-12-01' = {
  name: staticWebAppName
  location: location
  tags: tags
  sku: {
    name: sku
    tier: sku
  }
  properties: {
    repositoryUrl: '' // To be configured via GitHub Actions
    branch: '' // To be configured via GitHub Actions
    buildProperties: {
      appLocation: '/kaist-ai-webapp'
      apiLocation: ''
      outputLocation: 'dist'
    }
    stagingEnvironmentPolicy: 'Enabled'
    allowConfigFileUpdates: true
    provider: 'Custom'
    enterpriseGradeCdnStatus: 'Disabled'
  }
}

// Static Web App Configuration (API Backend)
resource staticWebAppConfig 'Microsoft.Web/staticSites/config@2023-12-01' = {
  parent: staticWebApp
  name: 'appsettings'
  properties: {
    VITE_API_ENDPOINT: 'https://${functionAppHostName}'
    VITE_APP_NAME: 'KAIST PDF Chatbot'
  }
}

// Outputs
output staticWebAppId string = staticWebApp.id
output staticWebAppName string = staticWebApp.name
output staticWebAppDefaultHostName string = staticWebApp.properties.defaultHostname
output staticWebAppUrl string = 'https://${staticWebApp.properties.defaultHostname}'
output staticWebAppDeploymentToken string = staticWebApp.listSecrets().properties.apiKey
