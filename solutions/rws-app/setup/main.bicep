@description('List of OpenAI resources to create. Add pairs of name and location.')
param openAIConfig array = []

@description('Deployment Name')
param openAIDeploymentName string

@description('Azure OpenAI Sku')
@allowed([
  'S0'
])
param openAISku string = 'S0'

@description('Model Name')
param openAIModelName string

@description('Model Version')
param openAIModelVersion string

@description('Model SKU')
param openAIModelSKU string

@description('Model Capacity')
param openAIModelCapacity int = 20

@description('The name of the API Management resource')
param apimResourceName string

@description('Location for the APIM resource')
param apimResourceLocation string = resourceGroup().location

@description('The pricing tier of this API Management service')
@allowed([
  'Consumption'
  'Developer'
  'Basic'
  'Basicv2'
  'Standard'
  'Standardv2'
  'Premium'
])
param apimSku string = 'Consumption'

@description('The instance size of this API Management service.')
@allowed([
  0
  1
  2
])
param apimSkuCount int = 1

@description('The email address of the owner of the service')
param apimPublisherEmail string = 'noreply@microsoft.com'

@description('The name of the owner of the service')
param apimPublisherName string = 'Microsoft'

@description('The name of the APIM API for OpenAI API')
param openAIAPIName string = 'openai'

@description('The relative path of the APIM API for OpenAI API')
param openAIAPIPath string = 'openai'

@description('The display name of the APIM API for OpenAI API')
param openAIAPIDisplayName string = 'OpenAI'

@description('The description of the APIM API for OpenAI API')
param openAIAPIDescription string = 'Azure OpenAI API inferencing API'

@description('Full URL for the OpenAI API spec')
param openAIAPISpecURL string = 'https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/cognitiveservices/data-plane/AzureOpenAI/inference/stable/2024-02-01/inference.json'

@description('The name of the APIM Subscription for OpenAI API')
param openAISubscriptionName string = 'openai-subscription'

@description('The description of the APIM Subscription for OpenAI API')
param openAISubscriptionDescription string = 'OpenAI Subscription'

@description('The name of the OpenAI backend pool')
param openAIBackendPoolName string = 'openai-backend-pool'

@description('The description of the OpenAI backend pool')
param openAIBackendPoolDescription string = 'Load balancer for multiple OpenAI endpoints'

// built-in logging: additions BEGIN

@description('Name of the Log Analytics resource')
param logAnalyticsName string = 'workspace'

@description('Location of the Log Analytics resource')
param logAnalyticsLocation string = resourceGroup().location

@description('Name of the Application Insights resource')
param applicationInsightsName string = 'insights'

@description('Location of the Application Insights resource')
param applicationInsightsLocation string = resourceGroup().location

@description('Name of the APIM Logger')
param apimLoggerName string = 'apim-logger'

@description('Description of the APIM Logger')
param apimLoggerDescription string  = 'APIM Logger for OpenAI API'

@description('Number of bytes to log for API diagnostics')
param apiDiagnosticsLogBytes int = 8192

@description(' Name for the Workbook')
param workbookName string = 'OpenAIUsageAnalysis'

@description('Location for the Workbook')
param workbookLocation string = resourceGroup().location

@description('Display Name for the Workbook')
param workbookDisplayName string = 'OpenAI Usage Analysis'

// built-in logging: additions END

// function calling: additions BEGIN

@description('The name of the function app')
param functionAppName string

@description('Location for the function app')
param functionAppLocation string = resourceGroup().location

@description('The name of the function with the http trigger')
param functionName string = 'WeatherHttpTrigger'

@description('The name of the storage account')
param storageAccountName string

@description('Location for the storage account')
param storageAccountLocation string = resourceGroup().location

@description('Storage Account type')
@allowed([
  'Standard_LRS'
  'Standard_GRS'
  'Standard_RAGRS'
])
param storageAccountType string = 'Standard_LRS'

@description('The name of the APIM API for Function API')
param functionAPIName string = 'weather'

@description('The relative path of the APIM API for Function API')
param functionAPIPath string = 'weather'

@description('The display name of the APIM API for Function API')
param functionAPIDisplayName string = 'WeatherAPI'

@description('The description of the APIM API for Function API')
param functionAPIDescription string = 'Weather API'

// function calling: additions END

// SQL Server and Database: additions BEGIN

@description('The name of the SQL Server')
param sqlServerName string

@description('Location for the SQL Server')
param sqlServerLocation string = resourceGroup().location

@description('The administrator username for the SQL Server')
param sqlAdministratorLogin string

@description('The administrator password for the SQL Server')
@secure()
param sqlAdministratorLoginPassword string

@description('The name of the SQL Database')
param sqlDatabaseName string

@description('The SKU name for the SQL Database')
param sqlDatabaseSku string = 'Basic'

// SQL Server and Database: additions END

// SQL Function App: additions BEGIN

@description('The name of the SQL function app')
param sqlFunctionAppName string

@description('Location for the SQL function app')
param sqlFunctionAppLocation string = resourceGroup().location

@description('The name of the SQL function with the http trigger')
param sqlFunctionName string = 'sql'

@description('The name of the APIM API for SQL Function API')
param sqlFunctionAPIName string = 'sql'

@description('The relative path of the APIM API for SQL Function API')
param sqlFunctionAPIPath string = 'sql'

@description('The display name of the APIM API for SQL Function API')
param sqlFunctionAPIDisplayName string = 'SQLAPI'

@description('The description of the APIM API for SQL Function API')
param sqlFunctionAPIDescription string = 'SQL Query API'

// SQL Function App: additions END

// RAG Components: Blob Storage and Azure AI Search BEGIN

@description('The name of the storage account for RAG')
param ragStorageAccountName string = 'ragstore'

@description('Location for the RAG storage account')
param ragStorageAccountLocation string = resourceGroup().location

@description('Name of the blob container for documents')
param documentsContainerName string = 'documents'

@description('The name of the Azure AI Search service')
param searchServiceName string = 'ragsearch'

@description('Location for the Azure AI Search service')
param searchServiceLocation string = resourceGroup().location

@description('The SKU name for the Azure AI Search service')
@allowed([
  'free'
  'basic'
  'standard'
  'standard2'
  'standard3'
])
param searchServiceSku string = 'standard'

@description('The number of replicas for the Azure AI Search service')
param searchServiceReplicaCount int = 1

@description('The number of partitions for the Azure AI Search service')
param searchServicePartitionCount int = 1

// RAG Components: Blob Storage and Azure AI Search END

var resourceSuffix = uniqueString(subscription().id, resourceGroup().id)

var policyXml = loadTextContent('policy.xml')
var updatedPolicyXml = replace(policyXml, '{backend-id}', (length(openAIConfig) > 1) ? 'openai-backend-pool' : openAIConfig[0].name)

@description('The name of the OpenAI resource')
resource cognitiveServices 'Microsoft.CognitiveServices/accounts@2021-10-01' = [for config in openAIConfig: if(length(openAIConfig) > 0) {
  name: '${config.name}-${resourceSuffix}'
  location: config.location
  sku: {
    name: openAISku
  }
  kind: 'OpenAI'
  properties: {
    apiProperties: {
      statisticsEnabled: false
    }
    customSubDomainName: toLower('${config.name}-${resourceSuffix}')
  }
}]

@description('The name of the OpenAI resource deployment')
resource deployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01'  =  [for (config, i) in openAIConfig: if(length(openAIConfig) > 0) {
    name: openAIDeploymentName
    parent: cognitiveServices[i]
    properties: {
      model: {
        format: 'OpenAI'
        name: openAIModelName
        version: openAIModelVersion
      }
    }
    sku: {
        name: openAIModelSKU
        capacity: openAIModelCapacity
    }
}]

@description('The name of the APIM resource')
resource apimService 'Microsoft.ApiManagement/service@2023-05-01-preview' = {
  name: '${apimResourceName}-${resourceSuffix}'
  location: apimResourceLocation
  sku: {
    name: apimSku
    capacity: (apimSku == 'Consumption') ? 0 : ((apimSku == 'Developer') ? 1 : apimSkuCount)
  }
  properties: {
    publisherEmail: apimPublisherEmail
    publisherName: apimPublisherName
  }
  identity: {
    type: 'SystemAssigned'
  }
}

@description('Role assignment for APIM to access OpenAI resources')
var roleDefinitionID = resourceId('Microsoft.Authorization/roleDefinitions', '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd')
resource roleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = [for (config, i) in openAIConfig: if(length(openAIConfig) > 0) {
    scope: cognitiveServices[i]
    name: guid(subscription().id, resourceGroup().id, config.name, roleDefinitionID)
    properties: {
        roleDefinitionId: roleDefinitionID
        principalId: apimService.identity.principalId
        principalType: 'ServicePrincipal'
    }
}]

resource api 'Microsoft.ApiManagement/service/apis@2023-05-01-preview' = {
    name: openAIAPIName
    parent: apimService
    properties: {
      apiType: 'http'
      description: openAIAPIDescription
      displayName: openAIAPIDisplayName
      format: 'openapi-link'
      path: openAIAPIPath
      protocols: [
        'https'
      ]
      subscriptionKeyParameterNames: {
        header: 'api-key'
        query: 'api-key'
      }
      subscriptionRequired: true
      type: 'http'
      value: openAIAPISpecURL
    }
  }

resource apiPolicy 'Microsoft.ApiManagement/service/apis/policies@2021-12-01-preview' = {
  name: 'policy'
  parent: api
  properties: {
    format: 'rawxml'
    value: updatedPolicyXml
  }
}

resource backendOpenAI 'Microsoft.ApiManagement/service/backends@2023-05-01-preview' = [for (config, i) in openAIConfig: if(length(openAIConfig) > 0) {
  name: config.name
  parent: apimService
  properties: {
    description: 'backend description'
    url: '${cognitiveServices[i].properties.endpoint}/openai'
    protocol: 'http'
    circuitBreaker: {
      rules: [
        {
          failureCondition: {
            count: 3
            errorReasons: [
              'Server errors'
            ]
            interval: 'PT5M'
            statusCodeRanges: [
              {
                min: 429
                max: 429
              }
            ]
          }
          name: 'openAIBreakerRule'
          tripDuration: 'PT1M'
        }
      ]
    }
  }
}]

resource backendPoolOpenAI 'Microsoft.ApiManagement/service/backends@2023-05-01-preview' = if(length(openAIConfig) > 1) {
  name: openAIBackendPoolName
  parent: apimService
  // BCP035: protocol and url are not needed in the Pool type. This is an incorrect error.
  #disable-next-line BCP035
  properties: {
    description: openAIBackendPoolDescription
    type: 'Pool'
    pool: {
      services: [for (config, i) in openAIConfig: {
          id: '/backends/${backendOpenAI[i].name}'
        }
      ]
    }
  }
}

resource apimSubscription 'Microsoft.ApiManagement/service/subscriptions@2023-05-01-preview' = {
  name: openAISubscriptionName
  parent: apimService
  properties: {
    allowTracing: true
    displayName: openAISubscriptionDescription
    scope: '/apis'
    state: 'active'
  }
}

// built-in logging: additions BEGIN

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2021-12-01-preview' = {
  name: '${logAnalyticsName}-${resourceSuffix}'
  location: logAnalyticsLocation
  properties: any({
    retentionInDays: 30
    features: {
      searchVersion: 1
    }
    sku: {
      name: 'PerGB2018'
    }
  })
}

/*
resource diagnosticSettings 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = [for (config, i) in openAIConfig: if(length(openAIConfig) > 0) {
  name: '${cognitiveServices[i].name}-diagnostics'
  scope: cognitiveServices[i]
  properties: {
    workspaceId: logAnalytics.id
    logs: []
    metrics: [
      {
        category: 'AllMetrics'
        enabled: true
      }
    ]
  }
}]
*/

resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${applicationInsightsName}-${resourceSuffix}'
  location: applicationInsightsLocation
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
  }
}

resource apimLogger 'Microsoft.ApiManagement/service/loggers@2021-12-01-preview' = {
  name: apimLoggerName
  parent: apimService
  properties: {
    credentials: {
      instrumentationKey: applicationInsights.properties.InstrumentationKey
    }
    description: apimLoggerDescription
    isBuffered: false
    loggerType: 'applicationInsights'
    resourceId: applicationInsights.id
  }
}

var logSettings = {
  headers: [ 'Content-type', 'User-agent', 'x-ms-region', 'x-ratelimit-remaining-tokens' , 'x-ratelimit-remaining-requests' ]
  body: { bytes: apiDiagnosticsLogBytes }
}

resource apiDiagnostics 'Microsoft.ApiManagement/service/apis/diagnostics@2022-08-01' = if (!empty(apimLogger.name)) {
  name: 'applicationinsights'
  parent: api
  properties: {
    alwaysLog: 'allErrors'
    httpCorrelationProtocol: 'W3C'
    logClientIp: true
    loggerId: apimLogger.id
    metrics: true
    verbosity: 'verbose'
    sampling: {
      samplingType: 'fixed'
      percentage: 100
    }
    frontend: {
      request: logSettings
      response: logSettings
    }
    backend: {
      request: logSettings
      response: logSettings
    }
  }
}

resource workbook 'Microsoft.Insights/workbooks@2022-04-01' = {
  name: guid(resourceGroup().id, workbookName)
  location: workbookLocation
  kind: 'shared'
  properties: {
    displayName: workbookDisplayName
    serializedData: loadTextContent('openai-usage-analysis-workbook.json')
    sourceId: applicationInsights.id
    category: 'OpenAI'
  }
}
output applicationInsightsAppId string = applicationInsights.properties.AppId

output logAnalyticsWorkspaceId string = logAnalytics.properties.customerId

// built-in logging: additions END

// function calling: additions BEGIN

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: '${storageAccountName}${resourceSuffix}'
  location: storageAccountLocation
  sku: {
    name: storageAccountType
  }
  kind: 'StorageV2'
  properties: {
  }
}

resource hostingPlan 'Microsoft.Web/serverfarms@2022-09-01' = {
  name: '${functionAppName}-asp-${resourceSuffix}'
  location: functionAppLocation
  kind: 'linux'
  sku: {
    name: 'Y1'
    tier: 'Dynamic'
    size: 'Y1'
    family: 'Y'
  }
  properties: {
    reserved: true
  }
}

resource functionApp 'Microsoft.Web/sites@2022-09-01' = {
  name: '${functionAppName}-${resourceSuffix}'
  location: functionAppLocation
  kind: 'functionapp,linux'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: hostingPlan.id
    siteConfig: {
      pythonVersion: '3.11'
      appSettings: [
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
          value: applicationInsights.properties.InstrumentationKey
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
      ]
      linuxFxVersion: 'Python|3.11'
    }
    httpsOnly: true
  }
}

resource functionApi 'Microsoft.ApiManagement/service/apis@2023-05-01-preview' = {
  name: functionAPIName
  parent: apimService
  properties: {
    apiType: 'http'
    description: functionAPIDescription
    displayName: functionAPIDisplayName
    format: 'openapi+json'
    path: functionAPIPath
    serviceUrl: 'https://${functionApp.properties.defaultHostName}/api/weather'
    protocols: [
      'https'
    ]
    subscriptionKeyParameterNames: {
      header: 'api-key'
      query: 'api-key'
    }
    subscriptionRequired: true
    type: 'http'
    value: loadJsonContent('weather.json')
  }
}

output functionAppResourceName string = functionApp.name

// function calling: additions END

// SQL Server and Database: resources BEGIN

resource sqlServer 'Microsoft.Sql/servers@2021-11-01' = {
  name: '${sqlServerName}-${resourceSuffix}'
  location: sqlServerLocation
  properties: {
    administratorLogin: sqlAdministratorLogin
    administratorLoginPassword: sqlAdministratorLoginPassword
    version: '12.0'
  }
}

resource sqlDatabase 'Microsoft.Sql/servers/databases@2021-11-01' = {
  name: sqlDatabaseName
  parent: sqlServer
  location: sqlServerLocation
  sku: {
    name: sqlDatabaseSku
  }
  properties: {
    collation: 'SQL_Latin1_General_CP1_CI_AS'
  }
}

// Allow Azure services to access the SQL server
resource sqlFirewallRule 'Microsoft.Sql/servers/firewallRules@2021-11-01' = {
  name: 'AllowAllAzureIPs'
  parent: sqlServer
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

// SQL Server and Database: resources END

// SQL Function App: resources BEGIN

resource sqlFunctionApp 'Microsoft.Web/sites@2022-09-01' = {
  name: '${sqlFunctionAppName}-${resourceSuffix}'
  location: sqlFunctionAppLocation
  kind: 'functionapp,linux'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: hostingPlan.id
    siteConfig: {
      pythonVersion: '3.11'
      appSettings: [
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
          value: applicationInsights.properties.InstrumentationKey
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        {
          name: 'SQL_CONNECTION_STRING'
          value: 'Server=tcp:${sqlServer.properties.fullyQualifiedDomainName},1433;Initial Catalog=${sqlDatabaseName};Persist Security Info=False;User ID=${sqlAdministratorLogin};Password=${sqlAdministratorLoginPassword};MultipleActiveResultSets=False;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;'
        }
      ]
      linuxFxVersion: 'Python|3.11'
    }
    httpsOnly: true
  }
}

// Create API for SQL Function in APIM
resource sqlFunctionApi 'Microsoft.ApiManagement/service/apis@2023-05-01-preview' = {
  name: sqlFunctionAPIName
  parent: apimService
  properties: {
    apiType: 'http'
    description: sqlFunctionAPIDescription
    displayName: sqlFunctionAPIDisplayName
    format: 'openapi+json'
    path: sqlFunctionAPIPath
    serviceUrl: 'https://${sqlFunctionApp.properties.defaultHostName}/api/${sqlFunctionName}'
    protocols: [
      'https'
    ]
    subscriptionKeyParameterNames: {
      header: 'api-key'
      query: 'api-key'
    }
    subscriptionRequired: true
    type: 'http'
    value: loadJsonContent('sql.json')
  }
}

// SQL Function App: resources END

// RAG Storage and Search resources BEGIN

// Storage Account for storing documents for RAG
resource ragStorageAccount 'Microsoft.Storage/storageAccounts@2024-01-01' = {
  name: '${ragStorageAccountName}${resourceSuffix}'
  location: ragStorageAccountLocation
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    accessTier: 'Hot'
  }
}

// Blob Service for the RAG Storage Account
resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2024-01-01' = {
  parent: ragStorageAccount
  name: 'default'
  properties: {
    cors: {
      corsRules: []
    }
    deleteRetentionPolicy: {
      enabled: false
    }
  }
}

// Container for documents
resource documentsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2024-01-01' = {
  parent: blobService
  name: documentsContainerName
  properties: {
    publicAccess: 'None'
  }
}

// Azure AI Search Service
resource searchService 'Microsoft.Search/searchServices@2025-02-01-preview' = {
  name: '${searchServiceName}-${resourceSuffix}'
  location: searchServiceLocation
  sku: {
    name: searchServiceSku
  }
  properties: {
    replicaCount: searchServiceReplicaCount
    partitionCount: searchServicePartitionCount
    hostingMode: 'default'
    semanticSearch: 'free'
  }
}

// *** NOT WORKING YET ***
// Add a data source connection for the blob storage
// resource searchDataSource 'Microsoft.Search/searchServices/dataSources@2025-02-01-preview' = {
//   name: 'blob-data-source'
//   parent: searchService
//   properties: {
//     type: 'azureblob'
//     credentials: {
//       connectionString: 'DefaultEndpointsProtocol=https;AccountName=${ragStorageAccount.name};EndpointSuffix=${environment().suffixes.storage};AccountKey=${ragStorageAccount.listKeys().keys[0].value}'
//     }
//     container: {
//       name: documentsContainerName
//     }
//   }
//   dependsOn: [
//     searchService
//     documentsContainer
//   ]
// }

// RAG Storage and Search resources END

// Add identity access to Azure AI Search service for the function app
resource searchServiceRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(resourceGroup().id, functionApp.id, 'SearchServiceContributor')
  scope: searchService
  properties: {
    roleDefinitionId: resourceId('Microsoft.Authorization/roleDefinitions', '7ca78c08-252a-4471-8644-bb5ff32d4ba0') // Search Service Contributor role
    principalId: functionApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

// Add identity access to Blob Storage for the function app
resource blobDataContributorRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(resourceGroup().id, functionApp.id, 'StorageBlobDataContributor')
  scope: ragStorageAccount
  properties: {
    roleDefinitionId: resourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe') // Storage Blob Data Contributor role
    principalId: functionApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

output apimServiceId string = apimService.id

output apimResourceGatewayURL string = apimService.properties.gatewayUrl

#disable-next-line outputs-should-not-contain-secrets
output apimSubscriptionKey string = apimSubscription.listSecrets().primaryKey

// SQL outputs
output sqlServerFqdn string = sqlServer.properties.fullyQualifiedDomainName
output sqlDatabaseName string = sqlDatabase.name
output sqlFunctionAppResourceName string = sqlFunctionApp.name

// RAG outputs
output ragStorageAccountName string = ragStorageAccount.name
#disable-next-line outputs-should-not-contain-secrets
output ragStorageAccountKey string = ragStorageAccount.listKeys().keys[0].value
output ragStorageConnectionString string = 'DefaultEndpointsProtocol=https;AccountName=${ragStorageAccount.name};EndpointSuffix=${environment().suffixes.storage};AccountKey=${listKeys(ragStorageAccount.id, ragStorageAccount.apiVersion).keys[0].value}'
output documentsContainerName string = documentsContainer.name
output searchServiceName string = searchService.name
#disable-next-line outputs-should-not-contain-secrets
output searchServiceAdminKey string = searchService.listAdminKeys().primaryKey
output searchServiceEndpoint string = 'https://${searchService.name}.search.windows.net'
