---
title: PDF Knowledge Base Chatbot Agent Architecture Specification
version: 1.0
date_created: 2026-03-12
last_updated: 2026-03-12
owner: KAIST Big Data Analysis Team
tags: [architecture, chatbot, pdf, knowledge-base, azure, ai-agent, infrastructure]
---

# Introduction

This specification defines the architecture and requirements for a PDF-based knowledge base chatbot agent system. The solution enables users to upload PDF documents, build a searchable knowledge base, and interact with an AI-powered chatbot that answers questions based on the uploaded content. The system leverages Microsoft Azure cloud infrastructure with Azure Functions for the API layer and Azure Static Web Apps for the client application.

## 1. Purpose & Scope

**Purpose**: Define the architectural requirements, constraints, and guidelines for implementing a scalable, secure, and cost-effective PDF knowledge base chatbot agent system.

**Scope**: This specification covers:
- Cloud infrastructure architecture and deployment on Microsoft Azure
- API server implementation using Azure Functions
- Web client application using React
- Data storage and retrieval mechanisms
- Integration points between components
- Security and compliance requirements

**Intended Audience**: Software engineers, DevOps engineers, cloud architects, and AI/ML engineers implementing or maintaining the system.

**Assumptions**:
- Users have access to Azure subscription with sufficient permissions
- PDF documents are text-based or OCR-processed
- Users have basic familiarity with React and Python
- Azure DevOps or GitHub Actions will be used for CI/CD

## 2. Definitions

| Term | Definition |
|------|------------|
| **azd** | Azure Developer CLI - command-line tool for deploying Azure applications |
| **Bicep** | Infrastructure-as-Code (IaC) language for declaratively deploying Azure resources |
| **Cosmos DB** | Azure's globally distributed, multi-model database service |
| **Hybrid Search** | Search technique combining vector similarity search and keyword-based search |
| **Knowledge Base** | Collection of documents and their embeddings used for information retrieval |
| **Serverless Mode** | Cosmos DB billing model where resources scale automatically based on usage |
| **Blob Storage** | Azure object storage service for unstructured data |
| **Static Web Apps** | Azure service for hosting static web applications with integrated CI/CD |
| **Azure Functions** | Serverless compute service for running event-driven code |
| **Gemini-3-Pro** | Large Language Model from Google Cloud Platform (planned integration) |
| **Embedding** | Vector representation of text used for semantic search |
| **RAG** | Retrieval-Augmented Generation - technique for grounding LLM responses in retrieved documents |

## 3. Requirements, Constraints & Guidelines

### Infrastructure Requirements

- **REQ-001**: The system must be deployed on Microsoft Azure cloud platform
- **REQ-002**: All Azure resources must be provisioned in the `koreacentral` region
- **REQ-003**: Infrastructure must be managed using Azure Developer CLI (`azd`) commands
- **REQ-004**: All infrastructure must be defined as code using Bicep templates
- **REQ-005**: All resources must be grouped in a resource group named `kaist-ai-agent-rg`
- **REQ-006**: Cosmos DB must operate in serverless mode with hybrid search capabilities enabled
- **REQ-007**: Uploaded PDF files must be persisted in Azure Blob Storage
- **REQ-008**: The system must support future integration with GCP Gemini-3-Pro LLM

### API Server Requirements

- **REQ-009**: API server must be implemented using Python 3.11 runtime
- **REQ-010**: API server must be deployed as Azure Functions
- **REQ-011**: API must provide endpoints for PDF upload, processing, and query handling
- **REQ-012**: API must extract text and generate embeddings from uploaded PDFs
- **REQ-013**: API must store PDF metadata and embeddings in Cosmos DB
- **REQ-014**: API must implement retrieval-augmented generation (RAG) for answering queries

### Client Application Requirements

- **REQ-015**: Client must be built using React framework with TypeScript
- **REQ-016**: Client must use Vite as the build tool
- **REQ-017**: Client must use Tailwind CSS for styling
- **REQ-018**: Client must be deployed using Azure Static Web Apps
- **REQ-019**: Client must provide UI for PDF upload with progress indication
- **REQ-020**: Client must provide chat interface for user queries
- **REQ-021**: Client must display chat history and sources for answers

### Security Requirements

- **SEC-001**: All API endpoints must implement authentication and authorization
- **SEC-002**: Uploaded PDFs must be scanned for malware before processing
- **SEC-003**: Communication between client and API must use HTTPS/TLS
- **SEC-004**: Sensitive configuration values must be stored in Azure Key Vault
- **SEC-005**: Access to Cosmos DB and Blob Storage must use managed identities
- **SEC-006**: User data must be isolated using tenant-based or user-based partitioning

### Performance Requirements

- **PER-001**: PDF processing must support files up to 50MB in size
- **PER-002**: Chat responses must be returned within 5 seconds for 95th percentile
- **PER-003**: System must support at least 100 concurrent users
- **PER-004**: Embedding generation must be batched for efficiency

### Data Requirements

- **DAT-001**: PDF metadata must include filename, upload date, user ID, and size
- **DAT-002**: Text chunks must be stored with their embeddings and source references
- **DAT-003**: Chat history must be persisted per user session
- **DAT-004**: Data retention policy must be configurable (default: 90 days)

### Constraints

- **CON-001**: Initial implementation will use Azure OpenAI or similar for embeddings until Gemini integration
- **CON-002**: Cosmos DB serverless mode has throughput limits (5000 RU/s)
- **CON-003**: Azure Functions consumption plan has timeout limits (10 minutes for HTTP-triggered functions)
- **CON-004**: Blob Storage must use appropriate tier (hot/cool) based on access patterns
- **CON-005**: Client application must work on modern browsers (Chrome, Firefox, Safari, Edge - last 2 versions)

### Guidelines

- **GUD-001**: Use structured logging with correlation IDs for distributed tracing
- **GUD-002**: Implement retry logic with exponential backoff for transient failures
- **GUD-003**: Use feature flags for gradual rollout of new capabilities
- **GUD-004**: Follow Azure Well-Architected Framework principles
- **GUD-005**: Implement health check endpoints for monitoring
- **GUD-006**: Use semantic versioning for API endpoints
- **GUD-007**: Document all API endpoints using OpenAPI/Swagger specifications

### Design Patterns

- **PAT-001**: Use CQRS pattern separating read and write operations where appropriate
- **PAT-002**: Implement Circuit Breaker pattern for external service calls
- **PAT-003**: Use Repository pattern for data access abstraction
- **PAT-004**: Implement Factory pattern for creating LLM client instances
- **PAT-005**: Use Adapter pattern for future LLM provider switching (Gemini integration)

## 4. Interfaces & Data Contracts

### API Endpoints

#### PDF Upload Endpoint

```http
POST /api/pdf/upload
Content-Type: multipart/form-data
Authorization: Bearer <token>

Body:
- file: PDF file (max 50MB)
- metadata: JSON object with optional description

Response (200 OK):
{
  "documentId": "uuid",
  "fileName": "string",
  "status": "processing",
  "uploadedAt": "ISO8601 timestamp"
}
```

#### PDF Processing Status Endpoint

```http
GET /api/pdf/status/{documentId}
Authorization: Bearer <token>

Response (200 OK):
{
  "documentId": "uuid",
  "status": "completed|processing|failed",
  "progress": 100,
  "chunkCount": 42,
  "error": "string|null"
}
```

#### Chat Query Endpoint

```http
POST /api/chat/query
Content-Type: application/json
Authorization: Bearer <token>

Body:
{
  "query": "string",
  "sessionId": "uuid",
  "documentIds": ["uuid"] // optional, filter by specific documents
}

Response (200 OK):
{
  "answer": "string",
  "sources": [
    {
      "documentId": "uuid",
      "fileName": "string",
      "chunkId": "string",
      "relevanceScore": 0.95,
      "excerpt": "string"
    }
  ],
  "messageId": "uuid",
  "timestamp": "ISO8601 timestamp"
}
```

#### Chat History Endpoint

```http
GET /api/chat/history
Authorization: Bearer <token>

Query Parameters:
- sessionId: uuid (optional)
- limit: integer (default: 50)
- offset: integer (default: 0)

Response (200 OK):
{
  "messages": [
    {
      "messageId": "uuid",
      "role": "user|assistant",
      "content": "string",
      "timestamp": "ISO8601 timestamp",
      "sources": [...]
    }
  ],
  "total": 150,
  "hasMore": true
}
```

### Cosmos DB Schema

#### Documents Container

```json
{
  "id": "uuid",
  "type": "document",
  "userId": "string",
  "fileName": "string",
  "blobUrl": "string",
  "uploadedAt": "ISO8601 timestamp",
  "processedAt": "ISO8601 timestamp",
  "status": "completed|processing|failed",
  "metadata": {
    "size": 1234567,
    "pageCount": 42,
    "description": "string"
  },
  "chunkCount": 42,
  "_partitionKey": "userId"
}
```

#### Chunks Container (with Vector Embeddings)

```json
{
  "id": "uuid",
  "type": "chunk",
  "documentId": "uuid",
  "userId": "string",
  "chunkIndex": 0,
  "text": "string",
  "embedding": [0.1, 0.2, ...], // vector array
  "metadata": {
    "pageNumber": 1,
    "section": "string"
  },
  "_partitionKey": "userId"
}
```

#### Chat Sessions Container

```json
{
  "id": "uuid",
  "type": "session",
  "userId": "string",
  "createdAt": "ISO8601 timestamp",
  "updatedAt": "ISO8601 timestamp",
  "messages": [
    {
      "messageId": "uuid",
      "role": "user|assistant",
      "content": "string",
      "timestamp": "ISO8601 timestamp",
      "sources": [...]
    }
  ],
  "_partitionKey": "userId"
}
```

### Blob Storage Structure

```
container: pdfs
  └── {userId}/
      └── {documentId}/
          ├── original.pdf
          └── metadata.json
```

## 5. Acceptance Criteria

- **AC-001**: Given a valid PDF file under 50MB, When user uploads the file, Then the system shall store it in Blob Storage and return a documentId
- **AC-002**: Given an uploaded PDF, When processing completes, Then the system shall create document chunks with embeddings in Cosmos DB
- **AC-003**: Given a user query, When the query is submitted, Then the system shall return a relevant answer within 5 seconds with source citations
- **AC-004**: Given multiple PDFs uploaded by a user, When the user asks a question, Then the system shall search across all user's documents
- **AC-005**: Given a deployed infrastructure, When `azd up` is executed, Then all Azure resources shall be provisioned in koreacentral region
- **AC-006**: Given API endpoints, When called without authentication, Then the system shall return 401 Unauthorized
- **AC-007**: Given a chat session, When user sends multiple queries, Then the system shall maintain conversation context
- **AC-008**: Given the client application, When loaded in a modern browser, Then the UI shall be responsive and styled with Tailwind CSS
- **AC-009**: Given Cosmos DB in serverless mode, When queries are executed, Then hybrid search (vector + keyword) shall be utilized
- **AC-010**: Given a failed PDF processing, When the error occurs, Then the system shall log the error and update status to failed

## 6. Test Automation Strategy

### Test Levels

- **Unit Tests**: Test individual functions and components in isolation
  - Python API: pytest with coverage reporting
  - React Client: Vitest with React Testing Library
- **Integration Tests**: Test interactions between components
  - API integration with Cosmos DB and Blob Storage
  - End-to-end PDF upload and processing workflow
- **End-to-End Tests**: Test complete user workflows
  - Playwright or Cypress for browser automation
  - Test PDF upload → processing → query → response flow

### Frameworks

- **Python API**: pytest, pytest-asyncio, pytest-mock, pytest-cov
- **React Client**: Vitest, React Testing Library, MSW (Mock Service Worker)
- **E2E Tests**: Playwright
- **API Testing**: httpx for async HTTP testing

### Test Data Management

- Use fixture files for sample PDFs (small, valid test documents)
- Mock Cosmos DB responses using in-memory store for unit tests
- Use Azure Storage Emulator (Azurite) for local integration testing
- Implement test data cleanup in teardown hooks

### CI/CD Integration

- Run unit tests on every pull request
- Run integration tests on merge to main branch
- Run E2E tests nightly or before production deployments
- Integrate with GitHub Actions workflows
- Fail builds if tests fail or coverage drops below threshold

### Coverage Requirements

- **Python API**: Minimum 80% code coverage
- **React Client**: Minimum 75% code coverage
- **Critical Paths**: 100% coverage for authentication, payment, and data processing logic

### Performance Testing

- Use Locust or k6 for load testing API endpoints
- Simulate 100 concurrent users submitting queries
- Measure response times at 50th, 95th, and 99th percentiles
- Test PDF processing throughput (PDFs processed per minute)
- Monitor Cosmos DB RU consumption under load

## 7. Rationale & Context

### Why Azure?

Azure provides comprehensive PaaS services that align with project requirements:
- Cosmos DB offers serverless billing suitable for variable workloads
- Azure Functions eliminates server management overhead
- Static Web Apps provides integrated CI/CD for frontend applications
- Azure's presence in Korea Central ensures low latency for target users

### Why Serverless Cosmos DB?

Serverless mode automatically scales based on demand without pre-provisioning throughput, making it cost-effective for:
- Variable workloads with unpredictable traffic patterns
- Development and testing environments
- Applications with intermittent usage

Hybrid search capability combines vector similarity (semantic search) with keyword matching for improved retrieval accuracy.

### Why Python 3.11 for API?

- Rich ecosystem for ML/AI libraries (LangChain, sentence-transformers)
- Azure Functions first-class support
- Type hints and performance improvements in Python 3.11
- Strong community support for LLM integrations

### Why React + Vite?

- Vite provides faster development experience than Create React App
- React's component model suits chat interface development
- Large ecosystem of UI libraries and tools
- TypeScript ensures type safety and better developer experience

### Future Gemini-3-Pro Integration

The architecture uses adapter pattern to allow swapping LLM providers without major refactoring. Initial implementation may use Azure OpenAI for embeddings and chat, but the system is designed to integrate with GCP's Gemini-3-Pro when available.

## 8. Dependencies & External Integrations

### External Systems

- **EXT-001**: Google Cloud Platform - Future integration for Gemini-3-Pro LLM service (gRPC/REST API)

### Third-Party Services

- **SVC-001**: Azure OpenAI Service - Embeddings generation and optional LLM inference until Gemini integration (REST API, 99.9% SLA)
- **SVC-002**: Azure Active Directory / Entra ID - User authentication and authorization (OpenID Connect/OAuth 2.0)

### Infrastructure Dependencies

- **INF-001**: Azure Cosmos DB - Document metadata, chunks with embeddings, chat sessions (Serverless mode, NoSQL API)
- **INF-002**: Azure Blob Storage - PDF file storage (Hot tier for recent uploads, cool tier for archival)
- **INF-003**: Azure Functions - Serverless compute for API endpoints (Python 3.11 runtime, Consumption plan)
- **INF-004**: Azure Static Web Apps - Frontend hosting and CDN (Integrated CI/CD from GitHub)
- **INF-005**: Azure Key Vault - Secrets management for API keys and connection strings
- **INF-006**: Azure Application Insights - Monitoring, logging, and distributed tracing
- **INF-007**: Azure API Management - Optional API gateway for rate limiting and throttling

### Data Dependencies

- **DAT-001**: PDF Documents - User-uploaded files (PDF format, max 50MB, text-extractable)
- **DAT-002**: Embedding Model - Pre-trained model for text-to-vector conversion (e.g., text-embedding-ada-002 or all-MiniLM-L6-v2)

### Technology Platform Dependencies

- **PLT-001**: Python Runtime - Version 3.11.x required for Azure Functions compatibility and type hint features
- **PLT-002**: Node.js Runtime - Version 18.x or 20.x required for Vite build process and frontend tooling
- **PLT-003**: Azure CLI - Version 2.40+ required for resource management and deployment scripts
- **PLT-004**: Azure Developer CLI (azd) - Version 1.0+ required for infrastructure deployment workflows

### Compliance Dependencies

- **COM-001**: GDPR Compliance - User data must support deletion requests within 30 days; implement data retention policies
- **COM-002**: Data Residency - All data must remain in Korea Central region to comply with data sovereignty requirements

**Note**: Specific package versions (e.g., LangChain, React Router) are implementation details managed in requirements.txt and package.json. This specification focuses on architectural dependencies affecting system design and integration patterns.

## 9. Examples & Edge Cases

### Example: PDF Upload and Query Flow

```python
# API endpoint implementation example
from azure.functions import HttpRequest, HttpResponse
from azure.storage.blob import BlobServiceClient
from azure.cosmos import CosmosClient
import PyPDF2
import uuid

async def upload_pdf(req: HttpRequest) -> HttpResponse:
    # Validate request
    if 'file' not in req.files:
        return HttpResponse("No file provided", status_code=400)
    
    file = req.files['file']
    
    # Validate file size and type
    if file.size > 50 * 1024 * 1024:  # 50MB
        return HttpResponse("File too large", status_code=400)
    
    if not file.filename.endswith('.pdf'):
        return HttpResponse("Invalid file type", status_code=400)
    
    # Generate document ID
    document_id = str(uuid.uuid4())
    user_id = req.headers.get('X-User-ID')  # From auth middleware
    
    # Upload to Blob Storage
    blob_client = blob_service.get_blob_client(
        container="pdfs",
        blob=f"{user_id}/{document_id}/original.pdf"
    )
    await blob_client.upload_blob(file.stream)
    
    # Create document record in Cosmos DB
    document = {
        "id": document_id,
        "type": "document",
        "userId": user_id,
        "fileName": file.filename,
        "blobUrl": blob_client.url,
        "status": "processing",
        "uploadedAt": datetime.utcnow().isoformat()
    }
    await cosmos_container.create_item(document)
    
    # Trigger async processing (via queue or durable function)
    await queue_client.send_message({
        "documentId": document_id,
        "userId": user_id
    })
    
    return HttpResponse(
        json.dumps({
            "documentId": document_id,
            "fileName": file.filename,
            "status": "processing"
        }),
        mimetype="application/json",
        status_code=200
    )
```

### Example: React Component for Chat Interface

```typescript
// ChatInterface.tsx
import { useState } from 'react';
import axios from 'axios';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
}

interface Source {
  fileName: string;
  excerpt: string;
  relevanceScore: number;
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post('/api/chat/query', {
        query: input,
        sessionId: sessionStorage.getItem('sessionId')
      });

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.answer,
        sources: response.data.sources
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Query failed:', error);
      // Handle error
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-2xl rounded-lg px-4 py-2 ${
                msg.role === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-white border border-gray-200'
              }`}
            >
              <p>{msg.content}</p>
              {msg.sources && (
                <div className="mt-2 text-xs opacity-75">
                  <p>Sources:</p>
                  {msg.sources.map((src, i) => (
                    <p key={i}>• {src.fileName}</p>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
      
      <div className="border-t border-gray-200 p-4 bg-white">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Ask a question about your documents..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={loading}
          />
          <button
            onClick={sendMessage}
            disabled={loading}
            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Sending...' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  );
}
```

### Example: Bicep Infrastructure Definition

```bicep
// main.bicep
param location string = 'koreacentral'
param environmentName string = 'dev'

var resourceGroupName = 'kaist-ai-agent-rg'
var cosmosAccountName = 'kaist-cosmos-${environmentName}'
var storageAccountName = 'kaiststore${environmentName}'
var functionAppName = 'kaist-func-${environmentName}'
var staticWebAppName = 'kaist-web-${environmentName}'

// Cosmos DB Account
resource cosmosAccount 'Microsoft.DocumentDB/databaseAccounts@2023-04-15' = {
  name: cosmosAccountName
  location: location
  kind: 'GlobalDocumentDB'
  properties: {
    databaseAccountOfferType: 'Standard'
    locations: [
      {
        locationName: location
        failoverPriority: 0
      }
    ]
    capabilities: [
      {
        name: 'EnableServerless'
      }
      {
        name: 'EnableNoSQLVectorSearch'
      }
    ]
  }
}

// Cosmos DB Database
resource cosmosDatabase 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2023-04-15' = {
  parent: cosmosAccount
  name: 'knowledgebase'
  properties: {
    resource: {
      id: 'knowledgebase'
    }
  }
}

// Storage Account for PDFs
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
  }
}

// Azure Functions
resource functionApp 'Microsoft.Web/sites@2022-09-01' = {
  name: functionAppName
  location: location
  kind: 'functionapp,linux'
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'Python|3.11'
      appSettings: [
        {
          name: 'COSMOS_ENDPOINT'
          value: cosmosAccount.properties.documentEndpoint
        }
        {
          name: 'STORAGE_CONNECTION_STRING'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
      ]
    }
  }
}

// Static Web App
resource staticWebApp 'Microsoft.Web/staticSites@2022-09-01' = {
  name: staticWebAppName
  location: location
  sku: {
    name: 'Free'
    tier: 'Free'
  }
  properties: {
    repositoryUrl: 'https://github.com/<org>/<repo>'
    branch: 'main'
    buildProperties: {
      appLocation: '/kaist-ai-webapp'
      apiLocation: ''
      outputLocation: 'dist'
    }
  }
}
```

### Edge Cases

1. **Large PDF Processing**
   - **Case**: 50MB PDF with 500 pages
   - **Handling**: Implement chunking strategy (e.g., 1000 tokens per chunk); process asynchronously with progress updates; use durable functions for reliability

2. **Empty or Corrupted PDF**
   - **Case**: PDF file that cannot be read or contains no extractable text
   - **Handling**: Return error status with clear message; suggest OCR processing or file re-upload

3. **Concurrent Queries During PDF Processing**
   - **Case**: User asks question before PDF processing completes
   - **Handling**: Return response indicating processing in progress; optionally queue query to execute after completion

4. **Query with No Matching Documents**
   - **Case**: User's question has no relevant content in knowledge base
   - **Handling**: Return response stating no relevant information found; suggest uploading relevant documents

5. **Session Timeout**
   - **Case**: User returns after long period of inactivity
   - **Handling**: Maintain session data in Cosmos DB; restore chat history when user returns

6. **Rate Limiting**
   - **Case**: User submits many queries in short time
   - **Handling**: Implement rate limiting (e.g., 10 queries per minute); return 429 Too Many Requests with Retry-After header

7. **Language Detection**
   - **Case**: PDF contains multiple languages or non-English text
   - **Handling**: Detect document language; use appropriate embedding model; maintain language metadata for retrieval

## 10. Validation Criteria

| ID | Validation Criterion | Verification Method |
|----|---------------------|---------------------|
| VAL-001 | All infrastructure resources deployed to koreacentral | Verify via `az resource list --resource-group kaist-ai-agent-rg --query "[].location"` |
| VAL-002 | Bicep templates successfully deploy all resources | Execute `azd up` and verify no errors; check all resources created |
| VAL-003 | Cosmos DB operates in serverless mode | Query Cosmos DB account properties; verify billing model |
| VAL-004 | PDF upload stores files in Blob Storage | Upload test PDF; verify blob exists in expected path |
| VAL-005 | Python API runs on version 3.11 | Check Azure Function runtime settings |
| VAL-006 | Client application uses React + TypeScript + Vite | Inspect package.json and build configuration |
| VAL-007 | Client styling uses Tailwind CSS | Verify tailwind.config.js exists; inspect rendered CSS classes |
| VAL-008 | API endpoints require authentication | Call endpoint without token; verify 401 response |
| VAL-009 | Hybrid search enabled in Cosmos DB | Execute vector similarity query combined with keyword filter |
| VAL-010 | Chat responses include source citations | Submit query; verify response contains sources array with document references |
| VAL-011 | System handles 50MB PDF upload | Upload test file of exactly 50MB; verify successful processing |
| VAL-012 | Response time < 5 seconds for 95th percentile | Load test with 100 users; measure response times |
| VAL-013 | Infrastructure supports Gemini integration | Verify adapter pattern implementation; check LLM client abstraction |
| VAL-014 | Managed identity configured for Azure resource access | Verify Function App has system-assigned identity with appropriate role assignments |
| VAL-015 | Logging and monitoring operational | Generate test requests; verify logs appear in Application Insights |

## 11. Related Specifications / Further Reading

- [Azure Functions Python Developer Guide](https://learn.microsoft.com/azure/azure-functions/functions-reference-python)
- [Azure Cosmos DB for NoSQL Vector Search](https://learn.microsoft.com/azure/cosmos-db/nosql/vector-search)
- [Azure Static Web Apps Documentation](https://learn.microsoft.com/azure/static-web-apps/)
- [Azure Developer CLI (azd) Reference](https://learn.microsoft.com/azure/developer/azure-developer-cli/)
- [Bicep Language Specification](https://learn.microsoft.com/azure/azure-resource-manager/bicep/)
- [React + TypeScript Best Practices](https://react-typescript-cheatsheet.netlify.app/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Azure Well-Architected Framework](https://learn.microsoft.com/azure/well-architected/)
- [Retrieval-Augmented Generation (RAG) Pattern](https://arxiv.org/abs/2005.11401)
- [LangChain Documentation](https://python.langchain.com/)
- [Google Cloud Gemini API Documentation](https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/gemini)
