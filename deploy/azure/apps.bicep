targetScope = 'resourceGroup'

param location string = resourceGroup().location
param prefix string = 'drybean'
param environmentName string
param registryName string
param identityName string
param apiImage string
param dashboardImage string
@minLength(1)
@maxLength(40)
param revisionSuffix string
@description('Vacio permite acceso publico al dashboard; un CIDR IPv4 restringe el acceso. La API permanece interna.')
param allowedCidr string = ''

var tags = {
  project: 'drybean'
  managedBy: 'gestion-ia-laboratorio'
}

resource environment 'Microsoft.App/managedEnvironments@2026-07-01' existing = {
  name: environmentName
}
resource registry 'Microsoft.ContainerRegistry/registries@2023-07-01' existing = {
  name: registryName
}
resource pullIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = {
  name: identityName
}

resource api 'Microsoft.App/containerApps@2025-01-01' = {
  name: '${prefix}-api'
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: { '${pullIdentity.id}': {} }
  }
  properties: {
    managedEnvironmentId: environment.id
    workloadProfileName: 'Consumption'
    configuration: {
      activeRevisionsMode: 'Single'
      maxInactiveRevisions: 5
      registries: [{ server: registry.properties.loginServer, identity: pullIdentity.id }]
      ingress: {
        external: false
        allowInsecure: false
        targetPort: 8000
        transport: 'auto'
        traffic: [{ latestRevision: true, weight: 100 }]
      }
    }
    template: {
      revisionSuffix: revisionSuffix
      scale: { minReplicas: 1, maxReplicas: 1 }
      containers: [{
        name: 'api'
        image: apiImage
        resources: { cpu: json('0.25'), memory: '0.5Gi' }
        env: [
          { name: 'MODEL_PATH', value: '/app/outputs/models/serving/logistic_regression_drybean.joblib' }
          { name: 'MODEL_MANIFEST_PATH', value: '/app/outputs/models/serving/model_manifest.json' }
          { name: 'MAX_BATCH_SIZE', value: '1000' }
          { name: 'MAX_REQUEST_BYTES', value: '2097152' }
          { name: 'LOG_LEVEL', value: 'INFO' }
        ]
        probes: [
          { type: 'Startup', httpGet: { path: '/health/ready', port: 8000 }, periodSeconds: 5, failureThreshold: 36 }
          { type: 'Readiness', httpGet: { path: '/health/ready', port: 8000 }, periodSeconds: 10, failureThreshold: 3 }
          { type: 'Liveness', httpGet: { path: '/health/live', port: 8000 }, periodSeconds: 20, failureThreshold: 3 }
        ]
      }]
    }
  }
}

resource dashboard 'Microsoft.App/containerApps@2025-01-01' = {
  name: '${prefix}-dashboard'
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: { '${pullIdentity.id}': {} }
  }
  properties: {
    managedEnvironmentId: environment.id
    workloadProfileName: 'Consumption'
    configuration: {
      activeRevisionsMode: 'Single'
      maxInactiveRevisions: 5
      registries: [{ server: registry.properties.loginServer, identity: pullIdentity.id }]
      ingress: {
        external: true
        allowInsecure: false
        targetPort: 8501
        transport: 'auto'
        stickySessions: { affinity: 'sticky' }
        ipSecurityRestrictions: empty(allowedCidr) ? [] : [{
          name: 'equipo'
          description: 'Acceso del equipo del laboratorio'
          action: 'Allow'
          ipAddressRange: allowedCidr
        }]
        traffic: [{ latestRevision: true, weight: 100 }]
      }
    }
    template: {
      revisionSuffix: revisionSuffix
      scale: { minReplicas: 1, maxReplicas: 1 }
      containers: [{
        name: 'dashboard'
        image: dashboardImage
        resources: { cpu: json('0.25'), memory: '0.5Gi' }
        env: [
          { name: 'API_BASE_URL', value: 'https://${api.properties.configuration.ingress.fqdn}' }
          { name: 'MAX_BATCH_SIZE', value: '1000' }
          { name: 'MAX_REQUEST_BYTES', value: '2097152' }
        ]
        probes: [
          { type: 'Startup', httpGet: { path: '/_stcore/health', port: 8501 }, periodSeconds: 5, failureThreshold: 36 }
          { type: 'Readiness', httpGet: { path: '/_stcore/health', port: 8501 }, periodSeconds: 10, failureThreshold: 3 }
          { type: 'Liveness', httpGet: { path: '/_stcore/health', port: 8501 }, periodSeconds: 20, failureThreshold: 3 }
        ]
      }]
    }
  }
}

output dashboardUrl string = 'https://${dashboard.properties.configuration.ingress.fqdn}'
output apiInternalUrl string = 'https://${api.properties.configuration.ingress.fqdn}'
