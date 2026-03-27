<!-- markdownlint-disable-file -->

# Task Research Notes: kaist-ai-webapp React TypeScript Frontend

## Research Executed

### File Analysis

- `/Users/ahri/Documents/GitHub/big-data-analysis/docs/spec/spec-architecture-pdf-chatbot-agent.md`
  - REQ-015~021 defines React + TypeScript + Vite + Tailwind CSS + Azure Static Web Apps
  - SEC-001~006 defines authentication (Bearer token), HTTPS, Key Vault, managed identity requirements
  - API contracts defined (spec uses camelCase; **actual backend serializes snake_case** — see critical issue)
  - PER-001: 50MB PDF limit, PER-002: 5s response time
  - CON-005: Must support Chrome/Firefox/Safari/Edge last 2 versions

- `/Users/ahri/Documents/GitHub/big-data-analysis/kaist-ai-infra/infra/modules/staticwebapp.bicep`
  - `appLocation: '/kaist-ai-webapp'` — build source root
  - `outputLocation: 'dist'` — Vite default build output
  - `provider: 'Custom'` — manual deployment (not GitHub Actions auto-linked)
  - App settings: `VITE_API_ENDPOINT` (full URL) and `VITE_APP_NAME` = 'KAIST PDF Chatbot'
  - SKU: `Free`
  - Region: `eastasia` (Static Web Apps not available in koreacentral)
  - **Listens on `https://lemon-mushroom-0c74d5700.6.azurestaticapps.net`** (already provisioned)

- `/Users/ahri/Documents/GitHub/big-data-analysis/kaist-ai-infra/azure.yaml`
  - Only `kaist-ai-functions` service defined — **webapp service is MISSING**

- `/Users/ahri/Documents/GitHub/big-data-analysis/kaist-ai-functions/function_app.py`
  - `GET /api/health` — `AuthLevel.ANONYMOUS`
  - `POST /api/pdf/upload` — `AuthLevel.FUNCTION` (requires function key)
  - `GET /api/pdf/status/{documentId}` — `AuthLevel.FUNCTION`
  - `POST /api/pdf/process` — `AuthLevel.FUNCTION` (internal, not called from frontend)
  - `POST /api/chat/query` — `AuthLevel.FUNCTION`
  - `GET /api/chat/history` — `AuthLevel.FUNCTION`
  - PDF upload returns **HTTP 202** (not 200 as spec says)

- `/Users/ahri/Documents/GitHub/big-data-analysis/kaist-ai-functions/shared/models.py`
  - All Pydantic response models use **snake_case** field names (no alias generator)
  - `model_dump_json()` outputs snake_case — frontend must use snake_case keys

### Code Search Results

- `corsAllowedOrigins` in `main.bicep`
  - Already allows `https://*.azurestaticapps.net`, `http://localhost:3000`, `http://localhost:5173`
- `AuthLevel.FUNCTION` in `function_app.py`
  - All endpoints except health require function key via `?code=<key>` or `x-functions-key` header
- `VITE_API_ENDPOINT` in `staticwebapp.bicep`
  - Env var name is `VITE_API_ENDPOINT`, not `VITE_API_BASE_URL`

### External Research

- #fetch:https://vitejs.dev/guide/
  - Vite 6 is current stable; `vite.config.ts` is the config file
  - `npm create vite@latest` scaffold for React + TypeScript
- #fetch:https://tailwindcss.com/docs/installation/using-vite
  - Tailwind CSS v4 uses `@tailwindcss/vite` plugin — no PostCSS config needed, no `tailwind.config.ts`
  - Import: `@import "tailwindcss"` in CSS (replaces `@tailwind base/components/utilities`)

### Project Conventions

- Python backend uses snake_case consistently
- Infrastructure uses `kaist-ai-agent` naming prefix
- CORS already allows localhost:5173 (Vite default dev port)

---

## Critical Issues Found

### ISSUE-1: API Response Shape Is snake_case (Not camelCase)

The spec contract shows camelCase (`documentId`, `fileName`, etc.) but the Pydantic models serialize to snake_case by default with `model_dump_json()`. No `model_config` with alias generator is set.

**Actual backend JSON responses (verified from models.py):**

```json
// POST /api/pdf/upload → HTTP 202
{
  "document_id": "uuid",
  "file_name": "string",
  "status": "pending",
  "uploaded_at": "ISO8601"
}

// GET /api/pdf/status/{documentId} → HTTP 200
{
  "document_id": "uuid",
  "status": "completed|processing|failed|pending",
  "progress": 100,
  "chunk_count": 42,
  "error": null
}

// POST /api/chat/query → HTTP 200
{
  "answer": "string",
  "sources": [
    {
      "document_id": "uuid",
      "file_name": "string",
      "chunk_id": "string",
      "relevance_score": 0.95,
      "excerpt": "string"
    }
  ],
  "message_id": "uuid",
  "timestamp": "ISO8601"
}

// GET /api/chat/history → HTTP 200
{
  "messages": [
    {
      "message_id": "uuid",
      "role": "user|assistant",
      "content": "string",
      "timestamp": "ISO8601",
      "sources": []
    }
  ],
  "total": 150,
  "has_more": true   ← NOTE: Actual code uses Python dict key "hasMore" (see function_app.py line)
}
```

> **Note on chat/history**: `function_app.py` builds the response via `json.dumps({"messages": page, "total": total, "hasMore": ...})` — so `hasMore` is camelCase here (raw dict, not Pydantic).

### ISSUE-2: PDF Upload Returns 202, Not 200

Backend returns `status_code=202` for upload. Frontend polling logic must handle 202.

### ISSUE-3: `azure.yaml` Missing Webapp Service

`kaist-ai-infra/azure.yaml` only defines `kaist-ai-functions`. Add:

```yaml
services:
  kaist-ai-functions:
    host: function
    project: ../kaist-ai-functions
    language: python
  kaist-ai-webapp:
    host: staticwebapp
    project: ../kaist-ai-webapp
    dist: dist
```

### ISSUE-4: Function Key Required for Most Endpoints

All endpoints except `/api/health` use `AuthLevel.FUNCTION`. API calls require either:
- URL query param: `?code=<function-key>`
- HTTP header: `x-functions-key: <function-key>`

The `VITE_API_ENDPOINT` env var provides the base URL. A separate `VITE_API_FUNCTION_KEY` env var is needed. The Static Web App infra does NOT currently set this — it must be added.

### ISSUE-5: Bicep Environment Variable Name Mismatch

`staticwebapp.bicep` sets `VITE_API_ENDPOINT` but any code using `VITE_API_BASE_URL` will fail. Use `VITE_API_ENDPOINT` consistently.

---

## Key Discoveries

### Project Structure

```
kaist-ai-webapp/
├── index.html
├── package.json
├── tsconfig.json
├── tsconfig.node.json
├── vite.config.ts
├── staticwebapp.config.json
├── .env.example
├── .env.local                    ← gitignored, local dev only
├── public/
│   └── favicon.ico
└── src/
    ├── main.tsx                  ← React entry point
    ├── App.tsx                   ← Root component
    ├── index.css                 ← @import "tailwindcss"
    ├── api/
    │   └── client.ts             ← axios instance + all API functions
    ├── types/
    │   └── index.ts              ← TypeScript interfaces
    ├── components/
    │   ├── HealthStatus.tsx
    │   ├── PDFUploadPanel.tsx
    │   ├── ChatPanel.tsx
    │   ├── ChatMessage.tsx
    │   └── SourceCitation.tsx
    └── hooks/
        ├── useChat.ts            ← chat state + sendMessage logic
        └── usePDFUpload.ts       ← upload + polling logic
```

### Implementation Patterns

**API Base URL**: From `import.meta.env.VITE_API_ENDPOINT`

**Function Key Pattern**:
```typescript
const headers = {
  'x-functions-key': import.meta.env.VITE_API_FUNCTION_KEY ?? '',
};
```

**Polling Upload Status**: Poll `GET /api/pdf/status/{documentId}` every 2s until `status === 'completed' || 'failed'`

### Complete Examples

#### TypeScript Types (derived from models.py)

```typescript
// src/types/index.ts

export type DocumentStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface UploadResponse {
  document_id: string;
  file_name: string;
  status: DocumentStatus;
  uploaded_at: string;
}

export interface StatusResponse {
  document_id: string;
  status: DocumentStatus;
  progress: number;
  chunk_count: number;
  error: string | null;
}

export interface SourceReference {
  document_id: string;
  file_name: string;
  chunk_id: string;
  relevance_score: number;
  excerpt: string;
}

export interface ChatQueryRequest {
  query: string;
  session_id?: string;
  document_ids?: string[];
}

export interface ChatQueryResponse {
  answer: string;
  sources: SourceReference[];
  message_id: string;
  timestamp: string;
}

export interface ChatMessage {
  message_id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  sources: SourceReference[];
}

export interface ChatHistoryResponse {
  messages: ChatMessage[];
  total: number;
  hasMore: boolean;   // camelCase — built via raw json.dumps in function_app.py
}

export interface HealthResponse {
  status: 'healthy' | 'degraded';
  checks: {
    storage: 'ok' | 'unavailable';
    cosmos: 'ok' | 'unavailable';
    gemini: 'ok' | 'unavailable';
  };
}

// UI-only type for local chat message display
export interface UIMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  sources?: SourceReference[];
  isLoading?: boolean;
}
```

#### API Client

```typescript
// src/api/client.ts
import axios from 'axios';
import type {
  UploadResponse, StatusResponse, ChatQueryRequest,
  ChatQueryResponse, ChatHistoryResponse, HealthResponse
} from '../types';

const BASE_URL = import.meta.env.VITE_API_ENDPOINT ?? '';
const FUNCTION_KEY = import.meta.env.VITE_API_FUNCTION_KEY ?? '';

const api = axios.create({
  baseURL: `${BASE_URL}/api`,
  headers: {
    'x-functions-key': FUNCTION_KEY,
  },
});

export async function getHealth(): Promise<HealthResponse> {
  const { data } = await api.get<HealthResponse>('/health');
  return data;
}

export async function uploadPDF(
  file: File,
  onProgress?: (percent: number) => void,
): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await api.post<UploadResponse>('/pdf/upload', formData, {
    onUploadProgress: (e) => {
      if (onProgress && e.total) {
        onProgress(Math.round((e.loaded / e.total) * 100));
      }
    },
  });
  return data;
}

export async function getPDFStatus(documentId: string): Promise<StatusResponse> {
  const { data } = await api.get<StatusResponse>(`/pdf/status/${documentId}`);
  return data;
}

export async function sendChatQuery(
  req: ChatQueryRequest,
): Promise<ChatQueryResponse> {
  const { data } = await api.post<ChatQueryResponse>('/chat/query', req);
  return data;
}

export async function getChatHistory(
  sessionId?: string,
  limit = 50,
  offset = 0,
): Promise<ChatHistoryResponse> {
  const { data } = await api.get<ChatHistoryResponse>('/chat/history', {
    params: { sessionId, limit, offset },
  });
  return data;
}
```

### API and Schema Documentation

| Endpoint | Method | Auth | Request | Response | Status |
|---|---|---|---|---|---|
| `/api/health` | GET | None | — | `HealthResponse` | 200/503 |
| `/api/pdf/upload` | POST | FunctionKey | `multipart/form-data` field `file` | `UploadResponse` | **202** |
| `/api/pdf/status/{documentId}` | GET | FunctionKey | — | `StatusResponse` | 200/404 |
| `/api/chat/query` | POST | FunctionKey | `ChatQueryRequest` (JSON) | `ChatQueryResponse` | 200 |
| `/api/chat/history` | GET | FunctionKey | `?sessionId&limit&offset` | `ChatHistoryResponse` | 200 |

### Configuration Examples

#### `package.json`

```json
{
  "name": "kaist-ai-webapp",
  "private": true,
  "version": "0.0.1",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "lint": "eslint .",
    "preview": "vite preview",
    "test": "vitest"
  },
  "dependencies": {
    "axios": "^1.7.9",
    "lucide-react": "^0.460.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "react-dropzone": "^14.3.5"
  },
  "devDependencies": {
    "@tailwindcss/vite": "^4.0.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "@vitejs/plugin-react": "^4.3.4",
    "tailwindcss": "^4.0.0",
    "typescript": "~5.7.2",
    "vite": "^6.0.5",
    "vitest": "^2.1.8"
  }
}
```

#### `vite.config.ts`

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: process.env.VITE_API_ENDPOINT ?? 'http://localhost:7071',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  },
});
```

> **Note**: The proxy only applies in local dev (`npm run dev`). In production, `VITE_API_ENDPOINT` is injected at build time via the SWA app settings and baked into the bundle via `import.meta.env`.

#### `tsconfig.json`

```json
{
  "files": [],
  "references": [
    { "path": "./tsconfig.app.json" },
    { "path": "./tsconfig.node.json" }
  ]
}
```

#### `tsconfig.app.json`

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "isolatedModules": true,
    "moduleDetection": "force",
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedSideEffectImports": true
  },
  "include": ["src"]
}
```

#### `tsconfig.node.json`

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2023"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "noEmit": true,
    "skipLibCheck": true
  },
  "include": ["vite.config.ts"]
}
```

#### `src/index.css` (Tailwind CSS v4)

```css
@import "tailwindcss";
```

No `tailwind.config.ts` required for v4 with `@tailwindcss/vite`.

#### `index.html`

```html
<!doctype html>
<html lang="ko">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>KAIST PDF Chatbot</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

#### `.env.example`

```dotenv
# Backend Azure Functions base URL (no trailing slash)
VITE_API_ENDPOINT=https://func-kaist-ai-agent-dev-krc.azurewebsites.net

# Azure Functions function key (required for all endpoints except /health)
VITE_API_FUNCTION_KEY=your-function-key-here

# App display name (optional — already set via SWA app settings)
VITE_APP_NAME=KAIST PDF Chatbot
```

#### `staticwebapp.config.json`

```json
{
  "routes": [
    {
      "route": "/api/*",
      "allowedRoles": ["anonymous"]
    },
    {
      "route": "/*",
      "serve": "/index.html",
      "statusCode": 200
    }
  ],
  "navigationFallback": {
    "rewrite": "/index.html",
    "exclude": ["/images/*.{png,jpg,gif}", "/css/*", "/js/*", "/assets/*"]
  },
  "responseOverrides": {
    "404": {
      "rewrite": "/index.html",
      "statusCode": 200
    }
  },
  "globalHeaders": {
    "content-security-policy": "default-src 'self'; connect-src 'self' https://func-kaist-ai-agent-dev-krc.azurewebsites.net; style-src 'self' 'unsafe-inline'; script-src 'self'",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin"
  },
  "mimeTypes": {
    ".json": "text/json"
  }
}
```

> **Note**: SWA has a built-in `/api` proxy feature. Since the backend is a **separate** Azure Functions app (not SWA linked functions), use `VITE_API_ENDPOINT` pointing directly to the function app URL. The `/api/*` route rule above exists to ensure no SWA routing conflict.

#### Updated `azure.yaml`

```yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/Azure/azure-dev/main/schemas/v1.0/azure.yaml.json

name: kaist-ai-infra
metadata:
  template: kaist-ai-infra@0.0.1-beta
services:
  kaist-ai-functions:
    host: function
    project: ../kaist-ai-functions
    language: python
  kaist-ai-webapp:
    host: staticwebapp
    project: ../kaist-ai-webapp
    dist: dist
```

### Technical Requirements

- Node.js 20.x LTS required (per PLT-002)
- VITE_API_FUNCTION_KEY must be obtained from: `az functionapp function keys list --name func-kaist-ai-agent-dev-krc --resource-group kaist-ai-agent-rg --function-name pdf_upload`
- Build command: `npm run build` (tsc -b && vite build)
- Dev: `npm run dev` starts on `http://localhost:5173`

---

## Recommended Approach

**Tailwind CSS v4 with `@tailwindcss/vite`** (no PostCSS, no config file).

Rationale:
- Eliminates `postcss.config.js` and `tailwind.config.ts` boilerplate
- `@tailwindcss/vite` is the officially recommended approach for Vite projects as of v4
- Single `@import "tailwindcss"` line in CSS replaces three `@tailwind` directives
- Full compatibility with Vite 6

**No heavy state management library** (no Redux/Zustand). Use `useState` + custom hooks `useChat` and `usePDFUpload`. Rationale: only two data concerns (PDF upload state, chat messages list) which do not need cross-component shared state beyond prop drilling or simple context.

**`react-dropzone`** for file upload UI — handles drag-and-drop, file type validation (accept `.pdf`), and file size validation before hitting the API.

**`axios`** for HTTP — simpler `onUploadProgress` integration than native fetch for multipart upload progress tracking.

**`lucide-react`** for icons — tree-shakeable, TypeScript-native, already used in many React + Tailwind projects.

---

## Implementation Guidance

- **Objectives**:
  - Scaffold `kaist-ai-webapp/` as a Vite + React 19 + TypeScript + Tailwind v4 project
  - Implement PDF upload panel with drag-and-drop, progress bar, and polling status
  - Implement chat panel with message history, sources, and session management
  - Connect to live backend at `https://func-kaist-ai-agent-dev-krc.azurewebsites.net`
  - Deploy to `https://lemon-mushroom-0c74d5700.6.azurestaticapps.net`

- **Key Tasks**:
  1. Create all config files (`package.json`, `vite.config.ts`, `tsconfig.json`, `tsconfig.app.json`, `tsconfig.node.json`, `index.html`, `.env.example`, `staticwebapp.config.json`)
  2. Create `src/types/index.ts` with all TypeScript interfaces (snake_case matching actual API)
  3. Create `src/api/client.ts` with axios instance and typed API functions
  4. Create `src/hooks/usePDFUpload.ts` (upload + 2s polling until completed/failed)
  5. Create `src/hooks/useChat.ts` (messages state + sendMessage + session ID)
  6. Create components: `HealthStatus`, `PDFUploadPanel`, `ChatPanel`, `ChatMessage`, `SourceCitation`
  7. Create `src/App.tsx` as layout shell
  8. Update `kaist-ai-infra/azure.yaml` to add webapp service

- **Dependencies**:
  - Function key for local dev: obtain via `az functionapp function keys list`
  - Backend CORS already allows `http://localhost:5173`

- **Success Criteria**:
  - `npm run build` in `kaist-ai-webapp/` produces `dist/` with no TypeScript errors
  - Health indicator shows green for storage/cosmos/gemini
  - PDF drag-and-drop uploads file, shows progress, polls until `completed`
  - Chat sends query and renders answer + expandable source citations
  - `azd deploy` deploys both functions and webapp via updated `azure.yaml`
