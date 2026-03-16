// Naming convention module for consistent resource naming
// Based on Azure naming best practices

@description('Base name for the project')
param baseName string

@description('Environment name')
@allowed([
  'dev'
  'staging'
  'prod'
])
param environment string

@description('Azure region short code')
param locationShortCode string = 'krc' // koreacentral

// Resource name outputs following Azure naming conventions
// Format: {resource-type}-{base-name}-{environment}-{location}

output storageAccountName string = toLower(replace('st${baseName}${environment}${locationShortCode}', '-', ''))
output cosmosDbAccountName string = toLower('cosmos-${baseName}-${environment}-${locationShortCode}')
output keyVaultName string = toLower('kv${baseName}${environment}${locationShortCode}')
output functionAppName string = toLower('func-${baseName}-${environment}-${locationShortCode}')
output appServicePlanName string = toLower('asp-${baseName}-${environment}-${locationShortCode}')
output staticWebAppName string = toLower('swa-${baseName}-${environment}-${locationShortCode}')
output appInsightsName string = toLower('appi-${baseName}-${environment}-${locationShortCode}')
output logAnalyticsName string = toLower('log-${baseName}-${environment}-${locationShortCode}')
output managedIdentityName string = toLower('id-${baseName}-${environment}-${locationShortCode}')
output containerName string = 'pdfs'
