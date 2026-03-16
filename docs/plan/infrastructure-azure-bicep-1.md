---
goal: Implement Azure Infrastructure for PDF Knowledge Base Chatbot using Bicep and azd
version: 1.0
date_created: 2026-03-12
last_updated: 2026-03-12
owner: KAIST Big Data Analysis Team
status: 'Planned'
tags: [infrastructure, azure, bicep, azd, iaas, deployment]
---

# Introduction

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

This implementation plan defines the steps for deploying Azure infrastructure for the PDF Knowledge Base Chatbot Agent system. The infrastructure will be implemented as code using Bicep templates and managed via Azure Developer CLI (azd). This plan focuses exclusively on infrastructure provisioning and does not include application code implementation.

The infrastructure consists of:
- **Azure Cosmos DB** (serverless mode with hybrid search for vector embeddings)
- **Azure Blob Storage** (PDF file storage)
- **Azure Functions** (compute infrastructure for API server)
- **Azure Static Web Apps** (frontend hosting)
- **Azure Key Vault** (secrets management)
- **Azure Application Insights** (monitoring and logging)
- **Managed Identities** (secure resource access)

All resources will be deployed to the `koreacentral` region within the `kaist-ai-agent-rg` resource group.

## 1. Requirements & Constraints

### Infrastructure Requirements

- **REQ-001**: All Azure resources must be deployed on Microsoft Azure cloud platform
- **REQ-002**: All resources must be provisioned in the `koreacentral` region
- **REQ-003**: Infrastructure must be managed using Azure Developer CLI (`azd`) commands
- **REQ-004**: All infrastructure must be defined as code using Bicep templates
- **REQ-005**: Resource group must be named `kaist-ai-agent-rg`
- **REQ-006**: Cosmos DB must operate in serverless mode with hybrid search (vector + keyword) enabled
- **REQ-007**: Blob Storage must be configured for PDF storage with appropriate access tiers
- **REQ-008**: Azure Functions must support Python 3.11 runtime
- **REQ-009**: Infrastructure must support future GCP Gemini-3-Pro integration

### Security Requirements

- **SEC-001**: All resources must use managed identities for authentication
- **SEC-002**: Sensitive configuration must be stored in Azure Key Vault
- **SEC-003**: All endpoints must use HTTPS/TLS encryption
- **SEC-004**: RBAC (Role-Based Access Control) must be configured for all resources
- **SEC-005**: Network security rules must follow principle of least privilege

### Deployment Requirements

- **DEP-001**: Infrastructure must be deployable via single `azd up` command
- **DEP-002**: Environment-specific configurations must be parameterized
- **DEP-003**: Deployment must be idempotent (safe to run multiple times)
- **DEP-004**: Infrastructure must support multiple environments (dev, staging, prod)

### Constraints

- **CON-001**: Cosmos DB serverless mode has 5000 RU/s throughput limit
- **CON-002**: Azure Functions consumption plan has 10-minute timeout for HTTP triggers
- **CON-003**: Must use existing Azure subscription without creating new one
- **CON-004**: Infrastructure costs must be minimized using serverless/consumption pricing tiers

### Guidelines

- **GUD-001**: Use consistent naming conventions across all resources
- **GUD-002**: Tag all resources with environment, project, and owner information
- **GUD-003**: Enable diagnostic logging for all resources
- **GUD-004**: Follow Azure Well-Architected Framework principles
- **GUD-005**: Document all Bicep parameters with descriptions

### Patterns

- **PAT-001**: Use Bicep modules for reusable infrastructure components
- **PAT-002**: Use parameter files for environment-specific configurations
- **PAT-003**: Use outputs for cross-resource references
- **PAT-004**: Use user-assigned managed identities for better control

## 2. Implementation Steps

### Implementation Phase 1: Project Setup and Azure Configuration

**GOAL-001**: Initialize azd project structure and configure Azure subscription

| Task     | Description                                                                                              | Completed | Date       |
| -------- | -------------------------------------------------------------------------------------------------------- | --------- | ---------- |
| TASK-001 | Initialize azd project in `kaist-ai-infra/` directory using `azd init`                                  | ✓         | 2026-03-12 |
| TASK-002 | Create `azure.yaml` configuration file with project metadata and service definitions                     | ✓         | 2026-03-12 |
| TASK-003 | Create `.azure/` directory structure for environment configurations                                      | ✓         | 2026-03-12 |
| TASK-004 | Configure Azure subscription using `azd auth login` and verify permissions                               | ✓         | 2026-03-12 |
| TASK-005 | Create main Bicep file structure: `main.bicep`, `main.parameters.json`                                  | ✓         | 2026-03-12 |
| TASK-006 | Create Bicep modules directory structure: `infra/modules/`                                               | ✓         | 2026-03-12 |
| TASK-007 | Define project-wide naming convention and create `naming.bicep` module                                   | ✓         | 2026-03-12 |
| TASK-008 | Create `.env.sample` file documenting required environment variables                                     | ✓         | 2026-03-12 |

### Implementation Phase 2: Core Infrastructure - Resource Group and Networking

**GOAL-002**: Provision resource group and configure foundational networking

| Task     | Description                                                                                              | Completed | Date       |
| -------- | -------------------------------------------------------------------------------------------------------- | --------- | ---------- |
| TASK-009 | Create `infra/main.bicep` with resource group targeting `koreacentral` region                            | ✓         | 2026-03-12 |
| TASK-010 | Define parameters for environment name, location, and resource naming                                    | ✓         | 2026-03-12 |
| TASK-011 | Implement resource tagging strategy (environment, project, owner, costCenter)                            | ✓         | 2026-03-12 |
| TASK-012 | Configure deployment scope and subscription targeting                                                    | ✓         | 2026-03-12 |
| TASK-013 | Test resource group creation using `azd provision` in dev environment                                    | ✓         | 2026-03-12 |

### Implementation Phase 3: Storage Infrastructure - Azure Blob Storage

**GOAL-003**: Deploy and configure Azure Blob Storage for PDF file persistence

| Task     | Description                                                                                              | Completed | Date       |
| -------- | -------------------------------------------------------------------------------------------------------- | --------- | ---------- |
| TASK-014 | Create `infra/modules/storage.bicep` module for storage account                                          | ✓         | 2026-03-12 |
| TASK-015 | Configure storage account with StorageV2, Standard_LRS SKU, Hot access tier                              | ✓         | 2026-03-12 |
| TASK-016 | Enable blob versioning and soft delete (7-day retention)                                                 | ✓         | 2026-03-12 |
| TASK-017 | Create blob container named `pdfs` with private access level                                             | ✓         | 2026-03-12 |
| TASK-018 | Configure CORS rules for Static Web App access                                                           | ✓         | 2026-03-12 |
| TASK-019 | Enable Azure Defender for Storage (malware scanning)                                                     | ⚠️        | 2026-03-12 |
| TASK-020 | Configure lifecycle management policy for archiving old PDFs to Cool tier after 30 days                  | ✓         | 2026-03-12 |
| TASK-021 | Output storage account name, connection string endpoint, and container name                              | ✓         | 2026-03-12 |

### Implementation Phase 4: Database Infrastructure - Azure Cosmos DB

**GOAL-004**: Deploy Azure Cosmos DB with serverless mode and hybrid search capabilities

| Task     | Description                                                                                              | Completed | Date       |
| -------- | -------------------------------------------------------------------------------------------------------- | --------- | ---------- |
| TASK-022 | Create `infra/modules/cosmos.bicep` module for Cosmos DB account                                         | ✓         | 2026-03-12 |
| TASK-023 | Configure Cosmos DB account with NoSQL API and serverless capacity mode                                  | ✓         | 2026-03-12 |
| TASK-024 | Enable vector search capability using `EnableNoSQLVectorSearch` feature                                  | ✓         | 2026-03-12 |
| TASK-025 | Set location to `koreacentral` with failover priority 0                                                  | ✓         | 2026-03-12 |
| TASK-026 | Create database named `knowledgebase` with default throughput                                            | ✓         | 2026-03-12 |
| TASK-027 | Create container `documents` with partition key `/userId` and no indexing policy override                | ✓         | 2026-03-12 |
| TASK-028 | Create container `chunks` with partition key `/userId` and vector embedding support                      | ✓         | 2026-03-12 |
| TASK-029 | Configure vector index on `chunks` container for `embedding` field (1536 dimensions for OpenAI)          | ✓         | 2026-03-12 |
| TASK-030 | Create container `sessions` with partition key `/userId` for chat history                                | ✓         | 2026-03-12 |
| TASK-031 | Configure TTL (Time-To-Live) on containers for automatic data expiration (90 days default)               | ✓         | 2026-03-12 |
| TASK-032 | Output Cosmos DB endpoint, database name, container names, and connection details                        | ✓         | 2026-03-12 |

### Implementation Phase 5: Compute Infrastructure - Azure Functions

**GOAL-005**: Provision Azure Functions infrastructure for Python 3.11 API server

| Task     | Description                                                                                              | Completed | Date       |
| -------- | -------------------------------------------------------------------------------------------------------- | --------- | ---------- |
| TASK-033 | Create `infra/modules/functions.bicep` module for Function App resources                                 | ✓         | 2026-03-12 |
| TASK-034 | Create App Service Plan with Linux OS and Consumption (Y1) SKU                                           | ✓         | 2026-03-12 |
| TASK-035 | Create Function App with Python 3.11 runtime (`linuxFxVersion: 'Python|3.11'`)                           | ✓         | 2026-03-12 |
| TASK-036 | Configure system-assigned managed identity for the Function App                                          | ✓         | 2026-03-12 |
| TASK-037 | Configure application settings: `FUNCTIONS_WORKER_RUNTIME=python`, `PYTHON_VERSION=3.11`                 | ✓         | 2026-03-12 |
| TASK-038 | Link Function App to Application Insights for monitoring                                                 | ✓         | 2026-03-12 |
| TASK-039 | Configure Function App to use storage account for internal storage                                       | ✓         | 2026-03-12 |
| TASK-040 | Enable HTTPS only and minimum TLS version 1.2                                                            | ✓         | 2026-03-12 |
| TASK-041 | Configure CORS to allow Static Web App origin                                                            | ✓         | 2026-03-12 |
| TASK-042 | Output Function App name, hostname, and managed identity principal ID                                    | ✓         | 2026-03-12 |

### Implementation Phase 6: Frontend Infrastructure - Azure Static Web Apps

**GOAL-006**: Deploy Azure Static Web Apps infrastructure for React client

| Task     | Description                                                                                              | Completed | Date       |
| -------- | -------------------------------------------------------------------------------------------------------- | --------- | ---------- |
| TASK-043 | Create `infra/modules/staticwebapp.bicep` module                                                         | ✓         | 2026-03-12 |
| TASK-044 | Create Static Web App with Free SKU in `koreacentral` region                                             | ✓         | 2026-03-12 |
| TASK-045 | Configure build properties: `appLocation: '/kaist-ai-webapp'`, `outputLocation: 'dist'`                  | ✓         | 2026-03-12 |
| TASK-046 | Configure environment variable for Function App API endpoint                                             | ✓         | 2026-03-12 |
| TASK-047 | Enable custom domain support (configuration placeholder for future)                                      | ✓         | 2026-03-12 |
| TASK-048 | Output Static Web App hostname, deployment token, and default URL                                        | ✓         | 2026-03-12 |

### Implementation Phase 7: Security Infrastructure - Key Vault and Managed Identity

**GOAL-007**: Implement Azure Key Vault and configure managed identities for secure resource access

| Task     | Description                                                                                              | Completed | Date |
| -------- | -------------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-049 | Create `infra/modules/keyvault.bicep` module for Key Vault                                               |           |      |
| TASK-050 | Create Key Vault with Standard SKU and soft delete enabled (90-day retention)                            |           |      |
| TASK-051 | Enable Azure RBAC authorization for Key Vault access                                                     |           |      |
| TASK-052 | Grant Function App managed identity "Key Vault Secrets User" role on Key Vault                           |           |      |
| TASK-053 | Create secret for Cosmos DB connection string                                                            |           |      |
| TASK-054 | Create secret for Storage Account connection string                                                      |           |      |
| TASK-055 | Create placeholder secret for future Gemini API key                                                      |           |      |
| TASK-056 | Grant Function App managed identity "Storage Blob Data Contributor" role on Storage Account              |           |      |
| TASK-057 | Grant Function App managed identity "Cosmos DB Built-in Data Contributor" role on Cosmos DB              |           |      |
| TASK-058 | Output Key Vault name, URI, and secret names                                                             |           |      |

### Implementation Phase 8: Monitoring Infrastructure - Application Insights

**GOAL-008**: Deploy Application Insights for comprehensive monitoring and logging

| Task     | Description                                                                                              | Completed | Date |
| -------- | -------------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-059 | Create `infra/modules/monitoring.bicep` module for Application Insights                                  |           |      |
| TASK-060 | Create Log Analytics Workspace with 30-day retention                                                     |           |      |
| TASK-061 | Create Application Insights resource linked to Log Analytics workspace                                   |           |      |
| TASK-062 | Configure intelligent sampling for high-volume telemetry                                                 |           |      |
| TASK-063 | Enable live metrics stream for real-time monitoring                                                      |           |      |
| TASK-064 | Configure diagnostic settings to forward all resource logs to Log Analytics                              |           |      |
| TASK-065 | Create custom workbook for PDF processing and chat query metrics                                         |           |      |
| TASK-066 | Configure alerts for Function App errors and Cosmos DB throttling                                        |           |      |
| TASK-067 | Output Application Insights instrumentation key, connection string, and workspace ID                     |           |      |

### Implementation Phase 9: azd Configuration and Integration

**GOAL-009**: Configure azd for automated deployment and environment management

| Task     | Description                                                                                              | Completed | Date |
| -------- | -------------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-068 | Create `azure.yaml` with services configuration for functions and webapp                                 |           |      |
| TASK-069 | Define infrastructure provisioning hooks for pre/post deployment scripts                                 |           |      |
| TASK-070 | Create `main.parameters.json` with default parameter values                                              |           |      |
| TASK-071 | Create environment-specific parameter files: `.azure/dev.parameters.json`                                |           |      |
| TASK-072 | Configure azd to output environment variables for application use                                        |           |      |
| TASK-073 | Create `.azure/<env>/.env` template with required environment variables                                  |           |      |
| TASK-074 | Document azd workflow in `kaist-ai-infra/README.md`                                                      |           |      |
| TASK-075 | Test complete deployment workflow: `azd up` from clean state                                             |           |      |

### Implementation Phase 10: Validation and Documentation

**GOAL-010**: Validate infrastructure deployment and create comprehensive documentation

| Task     | Description                                                                                              | Completed | Date |
| -------- | -------------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-076 | Verify all resources created in `koreacentral` region using Azure Portal                                 |           |      |
| TASK-077 | Verify Cosmos DB serverless mode and vector search capability enabled                                    |           |      |
| TASK-078 | Test Blob Storage upload/download with sample PDF file                                                   |           |      |
| TASK-079 | Verify Function App can access Cosmos DB using managed identity                                          |           |      |
| TASK-080 | Verify Function App can access Storage Account using managed identity                                    |           |      |
| TASK-081 | Verify Function App can read secrets from Key Vault                                                      |           |      |
| TASK-082 | Verify Application Insights logging and metrics from Function App                                        |           |      |
| TASK-083 | Test infrastructure destruction and recreation: `azd down` and `azd up`                                  |           |      |
| TASK-084 | Document infrastructure architecture with diagrams in `docs/infrastructure-architecture.md`              |           |      |
| TASK-085 | Create troubleshooting guide for common deployment issues                                                |           |      |
| TASK-086 | Document cost estimation for different usage tiers                                                       |           |      |
| TASK-087 | Create runbook for infrastructure updates and maintenance                                                |           |      |

## 3. Alternatives

### Alternative Approaches Considered

- **ALT-001**: **Terraform instead of Bicep** - Rejected because Bicep is Azure-native, has better Azure resource support, and integrates seamlessly with azd CLI
- **ALT-002**: **Dedicated Cosmos DB throughput instead of serverless** - Rejected because serverless is more cost-effective for variable workloads and development phases
- **ALT-003**: **Azure Container Apps instead of Azure Functions** - Rejected because Functions provide simpler deployment model for HTTP APIs and better integration with azd
- **ALT-004**: **Azure App Service instead of Static Web Apps** - Rejected because Static Web Apps provide better pricing, integrated CI/CD, and optimized CDN for static content
- **ALT-005**: **Key Vault references in Function App settings** - Partially adopted; using managed identity with RBAC provides better security than connection strings
- **ALT-006**: **Azure SQL Database instead of Cosmos DB** - Rejected because vector search and hybrid search are native features in Cosmos DB, avoiding need for extensions
- **ALT-007**: **Manual resource provisioning** - Rejected because IaC provides repeatability, version control, and automated deployments

## 4. Dependencies

### External Dependencies

- **DEP-001**: Azure Subscription with sufficient permissions (Contributor or Owner role)
- **DEP-002**: Azure CLI version 2.40+ installed locally
- **DEP-003**: Azure Developer CLI (azd) version 1.0+ installed locally
- **DEP-004**: Bicep CLI version 0.15+ (installed with Azure CLI)
- **DEP-005**: Git for version control

### Azure Resource Dependencies (Deployment Order)

- **DEP-006**: Resource Group → All other resources
- **DEP-007**: Storage Account → Function App (for internal storage)
- **DEP-008**: Log Analytics Workspace → Application Insights
- **DEP-009**: Application Insights → Function App (for monitoring)
- **DEP-010**: Cosmos DB → Function App (for application configuration)
- **DEP-011**: Key Vault → Function App (for secrets access)
- **DEP-012**: Function App → Static Web App (for API endpoint configuration)

### Feature Dependencies

- **DEP-013**: Cosmos DB NoSQL API with vector search capability (Azure feature flag)
- **DEP-014**: Azure Functions Python 3.11 runtime support (generally available)
- **DEP-015**: Static Web Apps with custom domain support (available in Free tier)

### Documentation Dependencies

- **DEP-016**: Specification document: `docs/spec/spec-architecture-pdf-chatbot-agent.md`
- **DEP-017**: Azure Well-Architected Framework documentation
- **DEP-018**: Azure Bicep documentation: https://learn.microsoft.com/azure/azure-resource-manager/bicep/

## 5. Files

### Bicep Infrastructure Files (kaist-ai-infra/)

- **FILE-001**: `infra/main.bicep` - Main Bicep template orchestrating all modules
- **FILE-002**: `infra/main.parameters.json` - Default parameter values for all environments
- **FILE-003**: `infra/modules/naming.bicep` - Naming convention module for consistent resource naming
- **FILE-004**: `infra/modules/storage.bicep` - Azure Blob Storage configuration module
- **FILE-005**: `infra/modules/cosmos.bicep` - Cosmos DB account, database, and containers module
- **FILE-006**: `infra/modules/functions.bicep` - Azure Functions and App Service Plan module
- **FILE-007**: `infra/modules/staticwebapp.bicep` - Static Web Apps configuration module
- **FILE-008**: `infra/modules/keyvault.bicep` - Key Vault and secrets management module
- **FILE-009**: `infra/modules/monitoring.bicep` - Application Insights and Log Analytics module
- **FILE-010**: `infra/modules/rbac.bicep` - Role assignments for managed identities module

### azd Configuration Files (kaist-ai-infra/)

- **FILE-011**: `azure.yaml` - azd project configuration with service definitions
- **FILE-012**: `.azure/config.json` - azd environment configuration
- **FILE-013**: `.azure/dev/config.json` - Development environment configuration
- **FILE-014**: `.azure/dev/.env` - Development environment variables (git-ignored)
- **FILE-015**: `.env.sample` - Template for required environment variables

### Documentation Files

- **FILE-016**: `kaist-ai-infra/README.md` - Infrastructure project overview and deployment instructions
- **FILE-017**: `docs/infrastructure-architecture.md` - Architecture diagrams and resource relationships
- **FILE-018**: `docs/deployment-guide.md` - Step-by-step deployment guide
- **FILE-019**: `docs/troubleshooting.md` - Common issues and solutions

### Helper Scripts (Optional)

- **FILE-020**: `scripts/validate-deployment.sh` - Post-deployment validation script
- **FILE-021**: `scripts/cleanup.sh` - Resource cleanup script for non-production environments
- **FILE-022**: `scripts/cost-analysis.sh` - Cost estimation and analysis script

## 6. Testing

### Infrastructure Validation Tests

- **TEST-001**: **Deployment Idempotency Test** - Run `azd up` twice consecutively and verify no resources are modified on second run
- **TEST-002**: **Resource Location Test** - Query all resources and verify location is `koreacentral`
- **TEST-003**: **Resource Group Test** - Verify resource group `kaist-ai-agent-rg` exists and contains all expected resources
- **TEST-004**: **Cosmos DB Serverless Test** - Verify Cosmos DB capacity mode is serverless using Azure CLI
- **TEST-005**: **Cosmos DB Vector Search Test** - Verify vector indexing policy exists on `chunks` container
- **TEST-006**: **Storage Container Test** - Verify `pdfs` blob container exists with private access level
- **TEST-007**: **Function App Runtime Test** - Verify Function App configuration shows Python 3.11 runtime
- **TEST-008**: **Managed Identity Test** - Verify Function App has system-assigned identity enabled
- **TEST-009**: **RBAC Test** - Verify Function App identity has required roles on Cosmos DB and Storage
- **TEST-010**: **Key Vault Access Test** - Verify Function App can read secrets from Key Vault
- **TEST-011**: **Application Insights Test** - Verify telemetry connection from Function App to Application Insights
- **TEST-012**: **HTTPS Enforcement Test** - Verify all endpoints require HTTPS
- **TEST-013**: **Tagging Test** - Verify all resources have required tags (environment, project, owner)

### Integration Tests

- **TEST-014**: **Blob Storage Upload Test** - Upload test PDF to blob storage using Azure SDK
- **TEST-015**: **Cosmos DB Write Test** - Create test document in Cosmos DB using connection string
- **TEST-016**: **Cosmos DB Query Test** - Execute NoSQL query on Cosmos DB containers
- **TEST-017**: **Key Vault Secret Retrieval Test** - Retrieve secret from Key Vault using Function App identity
- **TEST-018**: **Cross-Resource Connectivity Test** - Verify Function App can connect to all dependent resources

### Destruction Tests

- **TEST-019**: **Clean Teardown Test** - Run `azd down --purge` and verify all resources deleted
- **TEST-020**: **Soft-Delete Recovery Test** - Verify Key Vault soft-delete retention and recovery process

### Performance Tests

- **TEST-021**: **Deployment Time Test** - Measure and document time for full `azd up` deployment (target: < 10 minutes)
- **TEST-022**: **Cosmos DB Throughput Test** - Verify RU consumption within serverless limits (< 5000 RU/s)

## 7. Risks & Assumptions

### Risks

- **RISK-001**: **Cosmos DB Serverless Throttling** - Serverless mode has 5000 RU/s limit; may cause throttling under high load
  - *Mitigation*: Implement request rate limiting in API; monitor RU consumption; plan migration to provisioned throughput if needed
- **RISK-002**: **Cosmos DB Vector Search Public Preview** - Vector search may have limitations or breaking changes
  - *Mitigation*: Monitor Azure updates; test vector queries thoroughly; have fallback to keyword-only search
- **RISK-003**: **Azure Functions Cold Start** - Consumption plan has cold start latency (2-3 seconds)
  - *Mitigation*: Consider Premium plan for production; implement warmup triggers; optimize function package size
- **RISK-004**: **Key Vault Soft-Delete Conflicts** - Deleted Key Vault names reserved for 90 days
  - *Mitigation*: Use unique naming with environment suffixes; document purge procedures
- **RISK-005**: **Cost Overrun** - Unmonitored usage could lead to unexpected costs
  - *Mitigation*: Set up billing alerts; implement daily cost caps; monitor usage dashboards
- **RISK-006**: **Region Availability** - `koreacentral` may not have all features immediately
  - *Mitigation*: Verify feature availability before deployment; have alternate region plan (koreasouth)
- **RISK-007**: **Managed Identity Propagation Delay** - RBAC assignments may take minutes to propagate
  - *Mitigation*: Implement retry logic in application code; add sleep delay in deployment scripts
- **RISK-008**: **Static Web App Deployment Token Security** - Deployment token has broad permissions
  - *Mitigation*: Store token in GitHub Secrets; rotate periodically; use short-lived tokens when possible

### Assumptions

- **ASSUMPTION-001**: Azure subscription has no policy restrictions preventing resource creation in `koreacentral`
- **ASSUMPTION-002**: User has Contributor or Owner role on the subscription
- **ASSUMPTION-003**: Cosmos DB vector search feature is generally available (not preview) by deployment time
- **ASSUMPTION-004**: Azure Functions Python 3.11 runtime remains supported throughout project lifecycle
- **ASSUMPTION-005**: PDF processing workload fits within Azure Functions timeout limits (10 minutes)
- **ASSUMPTION-006**: Cosmos DB serverless mode is sufficient for initial user load (< 100 concurrent users)
- **ASSUMPTION-007**: GitHub repository will be used for CI/CD integration with Static Web Apps
- **ASSUMPTION-008**: OpenAI embeddings or compatible model will be used initially (1536-dimension vectors)
- **ASSUMPTION-009**: No VNet integration or private endpoints required in initial deployment
- **ASSUMPTION-010**: Development and production environments will use separate resource groups
- **ASSUMPTION-011**: PDF files will not exceed 50MB size limit
- **ASSUMPTION-012**: User authentication will be handled at application layer (not infrastructure)

## 8. Related Specifications / Further Reading

### Project Documentation

- [PDF Knowledge Base Chatbot Agent Architecture Specification](../spec/spec-architecture-pdf-chatbot-agent.md)

### Azure Documentation

- [Azure Developer CLI (azd) Overview](https://learn.microsoft.com/azure/developer/azure-developer-cli/overview)
- [Bicep Language Reference](https://learn.microsoft.com/azure/azure-resource-manager/bicep/file)
- [Azure Cosmos DB for NoSQL](https://learn.microsoft.com/azure/cosmos-db/nosql/)
- [Azure Cosmos DB Serverless](https://learn.microsoft.com/azure/cosmos-db/serverless)
- [Cosmos DB Vector Search](https://learn.microsoft.com/azure/cosmos-db/nosql/vector-search)
- [Azure Functions Python Developer Guide](https://learn.microsoft.com/azure/azure-functions/functions-reference-python)
- [Azure Static Web Apps Overview](https://learn.microsoft.com/azure/static-web-apps/overview)
- [Azure Blob Storage Documentation](https://learn.microsoft.com/azure/storage/blobs/)
- [Azure Key Vault Best Practices](https://learn.microsoft.com/azure/key-vault/general/best-practices)
- [Managed Identities for Azure Resources](https://learn.microsoft.com/azure/active-directory/managed-identities-azure-resources/overview)
- [Application Insights Overview](https://learn.microsoft.com/azure/azure-monitor/app/app-insights-overview)

### Best Practices

- [Azure Well-Architected Framework](https://learn.microsoft.com/azure/well-architected/)
- [Azure Naming Conventions](https://learn.microsoft.com/azure/cloud-adoption-framework/ready/azure-best-practices/resource-naming)
- [Azure Tagging Strategy](https://learn.microsoft.com/azure/cloud-adoption-framework/ready/azure-best-practices/resource-tagging)
- [Infrastructure as Code Best Practices](https://learn.microsoft.com/azure/azure-resource-manager/bicep/best-practices)

### Bicep Templates Examples

- [Azure Quickstart Templates](https://github.com/Azure/azure-quickstart-templates)
- [azd Templates Repository](https://github.com/Azure/awesome-azd)
- [Bicep Sample Templates](https://github.com/Azure/bicep/tree/main/docs/examples)
