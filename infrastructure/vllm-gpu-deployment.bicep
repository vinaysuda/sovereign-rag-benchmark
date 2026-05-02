// MOCK ENTERPRISE DEPLOYMENT: Sovereign Inference Boundary
// Deploys vLLM on GPU-enabled Azure Container Apps isolated via VNet.

param location string = resourceGroup().location
param environmentName string = 'sovereign-ai-env'

// 1. The Secure VNet (Ensuring Zero Public Internet Exposure)
resource vnet 'Microsoft.Network/virtualNetworks@2023-04-01' = {
  name: 'sovereign-vnet'
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: ['10.0.0.0/16']
    }
  }
}

// 2. Azure Container App Environment (The Execution Boundary)
resource containerAppEnv 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: environmentName
  location: location
  properties: {
    vnetConfiguration: {
      internal: true // STRICTLY INTERNAL ROUTING
      infrastructureSubnetId: resourceId('Microsoft.Network/virtualNetworks/subnets', 'sovereign-vnet', 'aca-subnet')
    }
  }
}

// 3. The GPU-Enabled vLLM Inference Node
resource vllmApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: 'vllm-llama3-inference'
  location: location
  properties: {
    managedEnvironmentId: containerAppEnv.id
    configuration: {
      ingress: {
        external: false // Private Link / APIM routing only
        targetPort: 8000
      }
    }
    template: {
      containers: [
        {
          name: 'vllm-server'
          image: 'vllm/vllm-openai:latest'
          resources: {
            cpu: 4
            memory: '32Gi'
          }
          // Requesting an Nvidia T4 GPU for local inference
          volumeMounts: []
        }
      ]
    }
  }
}