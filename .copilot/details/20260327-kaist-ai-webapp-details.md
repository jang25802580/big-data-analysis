<!-- markdownlint-disable-file -->

# Task Details: kaist-ai-webapp React Frontend 구현

## Research Reference

**Source Research**: `.copilot/research/20260327-kaist-ai-webapp-react-research.md`

---

## Phase 1: 프로젝트 설정 파일 생성

### Task 1.1: `package.json` 생성

`kaist-ai-webapp/package.json` 신규 생성. Vite 6 + React 19 + TypeScript + Tailwind v4 + axios + react-dropzone + lucide-react.

- **Files**:
  - `kaist-ai-webapp/package.json` — 프로젝트 메타 및 의존성 정의
- **Success**:
  - `npm install` 실행 시 오류 없음
  - `scripts.build = "tsc -b && vite build"` 포함
  - `type: "module"` 포함
- **Research References**:
  - `.copilot/research/20260327-kaist-ai-webapp-react-research.md (Lines 355-395) — package.json 완성본`
- **Dependencies**:
  - 없음

**`package.json` 내용:**

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

---

### Task 1.2: TypeScript 설정 파일 생성

세 개의 tsconfig 파일 생성: `tsconfig.json` (참조 root), `tsconfig.app.json` (src 대상), `tsconfig.node.json` (vite.config.ts 대상).

- **Files**:
  - `kaist-ai-webapp/tsconfig.json`
  - `kaist-ai-webapp/tsconfig.app.json`
  - `kaist-ai-webapp/tsconfig.node.json`
- **Success**:
  - `tsc -b` 실행 시 타입 오류 없음
- **Research References**:
  - `.copilot/research/20260327-kaist-ai-webapp-react-research.md (Lines 410-460) — tsconfig 완성본`
- **Dependencies**:
  - Task 1.1 완료

**`tsconfig.json`:**

```json
{
  "files": [],
  "references": [
    { "path": "./tsconfig.app.json" },
    { "path": "./tsconfig.node.json" }
  ]
}
```

**`tsconfig.app.json`:**

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

**`tsconfig.node.json`:**

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

---

### Task 1.3: `vite.config.ts` 생성

`@vitejs/plugin-react`와 `@tailwindcss/vite` 플러그인 등록. 로컬 dev 프록시로 `/api` → `VITE_API_ENDPOINT` 설정.

- **Files**:
  - `kaist-ai-webapp/vite.config.ts`
- **Success**:
  - `vite build` 실행 시 오류 없음
- **Research References**:
  - `.copilot/research/20260327-kaist-ai-webapp-react-research.md (Lines 396-415) — vite.config.ts 완성본`
- **Dependencies**:
  - Task 1.2 완료

**`vite.config.ts`:**

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

---

### Task 1.4: `index.html` 생성

Vite 진입점 HTML. `lang="ko"`, title "KAIST PDF Chatbot".

- **Files**:
  - `kaist-ai-webapp/index.html`
- **Success**:
  - `vite build` 시 index.html이 dist/에 복사됨
- **Research References**:
  - `.copilot/research/20260327-kaist-ai-webapp-react-research.md (Lines 494-508) — index.html 완성본`
- **Dependencies**:
  - Task 1.3 완료

**`index.html`:**

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

---

### Task 1.5: `.env.example` 및 `staticwebapp.config.json` 생성

환경변수 예시 파일과 Azure Static Web App 라우팅/보안 헤더 설정 파일.

- **Files**:
  - `kaist-ai-webapp/.env.example`
  - `kaist-ai-webapp/staticwebapp.config.json`
- **Success**:
  - `.env.example`에 `VITE_API_ENDPOINT`, `VITE_API_FUNCTION_KEY` 문서화
  - `staticwebapp.config.json`에 SPA fallback 라우팅 및 보안 헤더 포함
- **Research References**:
  - `.copilot/research/20260327-kaist-ai-webapp-react-research.md (Lines 510-565) — 두 파일 완성본`
- **Dependencies**:
  - Task 1.4 완료

**`.env.example`:**

```dotenv
# Backend Azure Functions base URL (no trailing slash)
VITE_API_ENDPOINT=https://func-kaist-ai-agent-dev-krc.azurewebsites.net

# Azure Functions function key (required for all endpoints except /health)
VITE_API_FUNCTION_KEY=your-function-key-here

# App display name
VITE_APP_NAME=KAIST PDF Chatbot
```

**`staticwebapp.config.json`:**

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
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin"
  },
  "mimeTypes": {
    ".json": "text/json"
  }
}
```

---

## Phase 2: TypeScript 타입 및 API 클라이언트

### Task 2.1: `src/types/index.ts` 생성

백엔드 Pydantic 모델의 실제 직렬화 형태인 snake_case 기반 TypeScript 인터페이스 정의.

- **Files**:
  - `kaist-ai-webapp/src/types/index.ts`
- **Success**:
  - 모든 API 응답 타입 커버
  - `ChatHistoryResponse.hasMore`는 camelCase (백엔드 raw dict 반환)
  - UI 전용 `UIMessage` 타입 포함
- **Research References**:
  - `.copilot/research/20260327-kaist-ai-webapp-react-research.md (Lines 223-285) — 전체 타입 정의`
- **Dependencies**:
  - Phase 1 완료

**`src/types/index.ts`:**

```typescript
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
  hasMore: boolean;
}

export interface HealthResponse {
  status: 'healthy' | 'degraded';
  checks: {
    storage: 'ok' | 'unavailable';
    cosmos: 'ok' | 'unavailable';
    gemini: 'ok' | 'unavailable';
  };
}

export interface UIMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  sources?: SourceReference[];
  isLoading?: boolean;
}
```

---

### Task 2.2: `src/api/client.ts` 생성

axios 인스턴스 생성 후 `VITE_API_ENDPOINT` + `x-functions-key` 헤더 설정. 각 엔드포인트별 타입화된 함수 export.

- **Files**:
  - `kaist-ai-webapp/src/api/client.ts`
- **Success**:
  - 모든 API 함수 타입 안전
  - `uploadPDF`에 `onProgress` 콜백 지원
  - 함수 키 헤더 자동 포함 (health 제외 포함 — 헤더가 있어도 anonymous endpoint는 무시함)
- **Research References**:
  - `.copilot/research/20260327-kaist-ai-webapp-react-research.md (Lines 286-350) — client.ts 완성본`
- **Dependencies**:
  - Task 2.1 완료

**`src/api/client.ts`:**

```typescript
import axios from 'axios';
import type {
  UploadResponse,
  StatusResponse,
  ChatQueryRequest,
  ChatQueryResponse,
  ChatHistoryResponse,
  HealthResponse,
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

---

## Phase 3: 커스텀 훅

### Task 3.1: `src/hooks/usePDFUpload.ts` 생성

파일 업로드 state 관리. uploadPDF 호출 후 `202` 응답의 `document_id`로 2초마다 getPDFStatus 폴링, `completed` 또는 `failed` 상태가 되면 폴링 중단.

- **Files**:
  - `kaist-ai-webapp/src/hooks/usePDFUpload.ts`
- **Success**:
  - `upload(file)` 호출 → 업로드 진행률 표시 → 폴링 시작 → 완료/실패 상태 반영
  - `useEffect` cleanup으로 컴포넌트 unmount 시 폴링 중단
- **Research References**:
  - `.copilot/research/20260327-kaist-ai-webapp-react-research.md (Lines 638-660) — 구현 가이던스`
- **Dependencies**:
  - Task 2.2 완료

**`src/hooks/usePDFUpload.ts`:**

```typescript
import { useState, useRef, useCallback } from 'react';
import { uploadPDF, getPDFStatus } from '../api/client';
import type { DocumentStatus } from '../types';

export interface PDFUploadState {
  isUploading: boolean;
  uploadProgress: number;
  documentId: string | null;
  documentStatus: DocumentStatus | null;
  fileName: string | null;
  error: string | null;
}

const INITIAL_STATE: PDFUploadState = {
  isUploading: false,
  uploadProgress: 0,
  documentId: null,
  documentStatus: null,
  fileName: null,
  error: null,
};

const POLL_INTERVAL_MS = 2000;

export function usePDFUpload() {
  const [state, setState] = useState<PDFUploadState>(INITIAL_STATE);
  const pollTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const stopPolling = useCallback(() => {
    if (pollTimerRef.current !== null) {
      clearInterval(pollTimerRef.current);
      pollTimerRef.current = null;
    }
  }, []);

  const startPolling = useCallback(
    (documentId: string) => {
      stopPolling();
      pollTimerRef.current = setInterval(async () => {
        try {
          const status = await getPDFStatus(documentId);
          setState((prev) => ({ ...prev, documentStatus: status.status }));
          if (status.status === 'completed' || status.status === 'failed') {
            stopPolling();
            if (status.status === 'failed') {
              setState((prev) => ({
                ...prev,
                error: status.error ?? 'PDF 처리 중 오류가 발생했습니다.',
              }));
            }
          }
        } catch {
          stopPolling();
          setState((prev) => ({
            ...prev,
            error: '상태 조회 중 오류가 발생했습니다.',
          }));
        }
      }, POLL_INTERVAL_MS);
    },
    [stopPolling],
  );

  const upload = useCallback(
    async (file: File) => {
      stopPolling();
      setState({
        ...INITIAL_STATE,
        isUploading: true,
        fileName: file.name,
      });
      try {
        const response = await uploadPDF(file, (percent) => {
          setState((prev) => ({ ...prev, uploadProgress: percent }));
        });
        setState((prev) => ({
          ...prev,
          isUploading: false,
          documentId: response.document_id,
          documentStatus: response.status,
        }));
        startPolling(response.document_id);
      } catch {
        setState((prev) => ({
          ...prev,
          isUploading: false,
          error: 'PDF 업로드에 실패했습니다.',
        }));
      }
    },
    [startPolling, stopPolling],
  );

  const reset = useCallback(() => {
    stopPolling();
    setState(INITIAL_STATE);
  }, [stopPolling]);

  return { ...state, upload, reset };
}
```

---

### Task 3.2: `src/hooks/useChat.ts` 생성

채팅 메시지 상태 관리. `sendMessage(query)` 호출 시 사용자 메시지 즉시 추가, 로딩 메시지 표시, API 응답으로 교체. `session_id`는 첫 메시지 전송 시 UUID 생성.

- **Files**:
  - `kaist-ai-webapp/src/hooks/useChat.ts`
- **Success**:
  - 메시지 전송 → 즉시 사용자 메시지 추가 → 로딩 표시 → 어시스턴트 응답 교체
  - `session_id` 유지
  - 오류 발생 시 에러 메시지 표시
- **Research References**:
  - `.copilot/research/20260327-kaist-ai-webapp-react-research.md (Lines 638-660) — 구현 가이던스`
- **Dependencies**:
  - Task 2.2 완료

**`src/hooks/useChat.ts`:**

```typescript
import { useState, useCallback, useRef } from 'react';
import { sendChatQuery } from '../api/client';
import type { UIMessage, SourceReference } from '../types';

function generateId(): string {
  return crypto.randomUUID();
}

export interface ChatState {
  messages: UIMessage[];
  isLoading: boolean;
  error: string | null;
  sessionId: string | null;
}

export function useChat() {
  const [messages, setMessages] = useState<UIMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const sessionIdRef = useRef<string | null>(null);

  const sendMessage = useCallback(async (query: string) => {
    if (!query.trim() || isLoading) return;

    if (!sessionIdRef.current) {
      sessionIdRef.current = generateId();
    }

    const userMessage: UIMessage = {
      id: generateId(),
      role: 'user',
      content: query,
      timestamp: new Date().toISOString(),
    };

    const loadingMessage: UIMessage = {
      id: generateId(),
      role: 'assistant',
      content: '',
      timestamp: new Date().toISOString(),
      isLoading: true,
    };

    setMessages((prev) => [...prev, userMessage, loadingMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const response = await sendChatQuery({
        query,
        session_id: sessionIdRef.current,
      });

      const assistantMessage: UIMessage = {
        id: response.message_id,
        role: 'assistant',
        content: response.answer,
        timestamp: response.timestamp,
        sources: response.sources as SourceReference[],
      };

      setMessages((prev) => {
        const without = prev.filter((m) => !m.isLoading);
        return [...without, assistantMessage];
      });
    } catch {
      setMessages((prev) => prev.filter((m) => !m.isLoading));
      setError('메시지 전송 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  }, [isLoading]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
    sessionIdRef.current = null;
  }, []);

  return { messages, isLoading, error, sendMessage, clearMessages };
}
```

---

## Phase 4: React 컴포넌트

### Task 4.1: `src/components/HealthStatus.tsx` 생성

`getHealth()` API 호출 후 storage/cosmos/gemini 상태를 색상 인디케이터로 표시. 컴포넌트 마운트 시 자동 조회, 30초마다 갱신.

- **Files**:
  - `kaist-ai-webapp/src/components/HealthStatus.tsx`
- **Success**:
  - healthy: 초록, degraded: 노랑, unavailable: 빨강 표시
  - 30초 interval로 자동 갱신
  - useEffect cleanup으로 메모리 누수 방지
- **Research References**:
  - `.copilot/research/20260327-kaist-ai-webapp-react-research.md (Lines 628-635) — 컴포넌트 목록`
- **Dependencies**:
  - Task 2.2 완료

```typescript
import { useState, useEffect, useCallback } from 'react';
import { getHealth } from '../api/client';
import type { HealthResponse } from '../types';

type CheckStatus = 'ok' | 'unavailable' | 'loading';

const STATUS_COLORS: Record<CheckStatus, string> = {
  ok: 'bg-green-500',
  unavailable: 'bg-red-500',
  loading: 'bg-gray-300',
};

const CHECK_LABELS: Record<keyof HealthResponse['checks'], string> = {
  storage: 'Storage',
  cosmos: 'Cosmos DB',
  gemini: 'Gemini',
};

const REFRESH_INTERVAL_MS = 30_000;

export function HealthStatus() {
  const [health, setHealth] = useState<HealthResponse | null>(null);

  const fetchHealth = useCallback(async () => {
    try {
      const data = await getHealth();
      setHealth(data);
    } catch {
      setHealth(null);
    }
  }, []);

  useEffect(() => {
    void fetchHealth();
    const id = setInterval(() => void fetchHealth(), REFRESH_INTERVAL_MS);
    return () => clearInterval(id);
  }, [fetchHealth]);

  const checks = health?.checks;

  return (
    <div className="flex items-center gap-3 text-sm">
      {(Object.keys(CHECK_LABELS) as Array<keyof typeof CHECK_LABELS>).map((key) => {
        const status: CheckStatus = checks ? checks[key] : 'loading';
        return (
          <span key={key} className="flex items-center gap-1">
            <span className={`inline-block w-2 h-2 rounded-full ${STATUS_COLORS[status]}`} />
            <span className="text-gray-600">{CHECK_LABELS[key]}</span>
          </span>
        );
      })}
    </div>
  );
}
```

---

### Task 4.2: `src/components/SourceCitation.tsx` 생성

소스 인용 하나를 카드 형식으로 표시. 파일명, 관련도 점수, 발췌문 포함.

- **Files**:
  - `kaist-ai-webapp/src/components/SourceCitation.tsx`
- **Success**:
  - `SourceReference` 타입을 props로 받아 렌더링
  - 발췌문 접기/펼치기 기능
- **Research References**:
  - `.copilot/research/20260327-kaist-ai-webapp-react-research.md (Lines 175-200) — 컴포넌트 아키텍처`
- **Dependencies**:
  - Task 2.1 완료

```typescript
import { useState } from 'react';
import { ChevronDown, ChevronUp, FileText } from 'lucide-react';
import type { SourceReference } from '../types';

interface SourceCitationProps {
  source: SourceReference;
  index: number;
}

export function SourceCitation({ source, index }: SourceCitationProps) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="border border-gray-200 rounded-md p-2 text-xs bg-gray-50">
      <button
        type="button"
        className="w-full flex items-center justify-between gap-2 text-left"
        onClick={() => setExpanded((prev) => !prev)}
      >
        <span className="flex items-center gap-1 font-medium text-gray-700">
          <FileText className="w-3 h-3 flex-shrink-0" />
          <span>[{index + 1}] {source.file_name}</span>
        </span>
        <span className="flex items-center gap-1 text-gray-500 flex-shrink-0">
          <span>{(source.relevance_score * 100).toFixed(0)}%</span>
          {expanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
        </span>
      </button>
      {expanded && (
        <p className="mt-1 text-gray-600 whitespace-pre-wrap">{source.excerpt}</p>
      )}
    </div>
  );
}
```

---

### Task 4.3: `src/components/ChatMessage.tsx` 생성

사용자/어시스턴트 메시지 버블. 어시스턴트 메시지에는 소스 인용 목록 포함. 로딩 상태 애니메이션.

- **Files**:
  - `kaist-ai-webapp/src/components/ChatMessage.tsx`
- **Success**:
  - user 메시지: 오른쪽 정렬, 파란 배경
  - assistant 메시지: 왼쪽 정렬, 흰 배경 + 소스 목록
  - isLoading: 점 세 개 애니메이션
- **Research References**:
  - `.copilot/research/20260327-kaist-ai-webapp-react-research.md (Lines 175-200) — 컴포넌트 아키텍처`
- **Dependencies**:
  - Task 4.2 완료

```typescript
import { SourceCitation } from './SourceCitation';
import type { UIMessage } from '../types';

interface ChatMessageProps {
  message: UIMessage;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-3`}>
      <div
        className={`max-w-[80%] px-4 py-2 rounded-2xl text-sm ${
          isUser
            ? 'bg-blue-600 text-white rounded-tr-sm'
            : 'bg-white border border-gray-200 text-gray-800 rounded-tl-sm shadow-sm'
        }`}
      >
        {message.isLoading ? (
          <span className="flex gap-1 items-center py-1">
            <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:-0.3s]" />
            <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:-0.15s]" />
            <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
          </span>
        ) : (
          <>
            <p className="whitespace-pre-wrap">{message.content}</p>
            {!isUser && message.sources && message.sources.length > 0 && (
              <div className="mt-2 space-y-1">
                <p className="text-xs text-gray-500 font-medium">참고 문서</p>
                {message.sources.map((src, idx) => (
                  <SourceCitation key={src.chunk_id} source={src} index={idx} />
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
```

---

### Task 4.4: `src/components/PDFUploadPanel.tsx` 생성

`react-dropzone` 기반 드래그앤드롭 업로드 패널. 업로드 진행률 바, 처리 상태 표시.

- **Files**:
  - `kaist-ai-webapp/src/components/PDFUploadPanel.tsx`
- **Success**:
  - PDF만 허용 (accept: `application/pdf`)
  - 50MB 초과 파일 클라이언트 측 거부 (`maxSize: 50 * 1024 * 1024`)
  - 업로드 진행률 바, 폴링 상태 표시
  - 완료/실패 피드백
- **Research References**:
  - `.copilot/research/20260327-kaist-ai-webapp-react-research.md (Lines 175-200) — 컴포넌트 아키텍처`
- **Dependencies**:
  - Task 3.1 완료

```typescript
import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, CheckCircle, XCircle, Loader2 } from 'lucide-react';
import { usePDFUpload } from '../hooks/usePDFUpload';

const MAX_SIZE_BYTES = 50 * 1024 * 1024;

export function PDFUploadPanel() {
  const { isUploading, uploadProgress, documentStatus, fileName, error, upload, reset } =
    usePDFUpload();

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles[0]) {
        void upload(acceptedFiles[0]);
      }
    },
    [upload],
  );

  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    maxSize: MAX_SIZE_BYTES,
    multiple: false,
    disabled: isUploading,
  });

  const sizeError = fileRejections.find((r) =>
    r.errors.some((e) => e.code === 'file-too-large'),
  );

  return (
    <div className="p-4 bg-white rounded-xl border border-gray-200 shadow-sm space-y-3">
      <h2 className="font-semibold text-gray-800 text-sm">PDF 업로드</h2>

      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
          isDragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        } ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <input {...getInputProps()} />
        <Upload className="w-6 h-6 mx-auto text-gray-400 mb-2" />
        <p className="text-sm text-gray-500">
          {isDragActive ? 'PDF를 여기에 놓으세요' : 'PDF 파일을 드래그하거나 클릭하여 선택'}
        </p>
        <p className="text-xs text-gray-400 mt-1">최대 50MB</p>
      </div>

      {sizeError && (
        <p className="text-xs text-red-500">파일 크기가 50MB를 초과합니다.</p>
      )}

      {isUploading && (
        <div>
          <div className="flex justify-between text-xs text-gray-500 mb-1">
            <span>{fileName}</span>
            <span>{uploadProgress}%</span>
          </div>
          <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-500 rounded-full transition-all duration-200"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
        </div>
      )}

      {documentStatus === 'processing' && (
        <div className="flex items-center gap-2 text-xs text-blue-600">
          <Loader2 className="w-3 h-3 animate-spin" />
          <span>PDF 처리 중...</span>
        </div>
      )}

      {documentStatus === 'completed' && (
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs text-green-600">
            <CheckCircle className="w-3 h-3" />
            <span>{fileName} 처리 완료</span>
          </div>
          <button
            type="button"
            onClick={reset}
            className="text-xs text-gray-400 hover:text-gray-600"
          >
            초기화
          </button>
        </div>
      )}

      {(documentStatus === 'failed' || error) && (
        <div className="flex items-center gap-2 text-xs text-red-500">
          <XCircle className="w-3 h-3" />
          <span>{error ?? 'PDF 처리에 실패했습니다.'}</span>
        </div>
      )}
    </div>
  );
}
```

---

### Task 4.5: `src/components/ChatPanel.tsx` 생성

메시지 목록 스크롤 영역 + 입력창 + 전송 버튼. `useChat` 훅 연동.

- **Files**:
  - `kaist-ai-webapp/src/components/ChatPanel.tsx`
- **Success**:
  - 새 메시지 추가 시 자동 스크롤 하단
  - Enter 키로 전송 (Shift+Enter 줄바꿈)
  - 로딩 중 입력 비활성화
- **Research References**:
  - `.copilot/research/20260327-kaist-ai-webapp-react-research.md (Lines 175-200) — 컴포넌트 아키텍처`
- **Dependencies**:
  - Task 3.2, 4.3 완료

```typescript
import { useRef, useEffect, useState, type KeyboardEvent } from 'react';
import { Send, Trash2 } from 'lucide-react';
import { useChat } from '../hooks/useChat';
import { ChatMessage } from './ChatMessage';

export function ChatPanel() {
  const { messages, isLoading, error, sendMessage, clearMessages } = useChat();
  const [input, setInput] = useState('');
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = () => {
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;
    setInput('');
    void sendMessage(trimmed);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-xl border border-gray-200 shadow-sm">
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
        <h2 className="font-semibold text-gray-800 text-sm">채팅</h2>
        <button
          type="button"
          onClick={clearMessages}
          disabled={messages.length === 0}
          className="text-gray-400 hover:text-gray-600 disabled:opacity-30"
          title="대화 초기화"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-1 min-h-0">
        {messages.length === 0 && (
          <p className="text-center text-sm text-gray-400 mt-8">
            PDF를 업로드한 후 질문을 입력하세요.
          </p>
        )}
        {messages.map((msg) => (
          <ChatMessage key={msg.id} message={msg} />
        ))}
        {error && (
          <p className="text-center text-xs text-red-500">{error}</p>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="px-4 py-3 border-t border-gray-100">
        <div className="flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="질문을 입력하세요... (Enter로 전송)"
            disabled={isLoading}
            rows={2}
            className="flex-1 resize-none rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:border-blue-500 disabled:opacity-50"
          />
          <button
            type="button"
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
```

---

## Phase 5: 진입점 및 azd 통합

### Task 5.1: `src/main.tsx`, `src/App.tsx`, `src/index.css` 생성

React 진입점, 최상위 레이아웃 컴포넌트, Tailwind CSS v4 임포트.

- **Files**:
  - `kaist-ai-webapp/src/main.tsx`
  - `kaist-ai-webapp/src/App.tsx`
  - `kaist-ai-webapp/src/index.css`
- **Success**:
  - `src/index.css`에 `@import "tailwindcss"` 포함
  - `App.tsx`가 `HealthStatus`, `PDFUploadPanel`, `ChatPanel` 렌더링
  - 반응형 2단 레이아웃 (좌: PDF 패널, 우: 채팅)
- **Research References**:
  - `.copilot/research/20260327-kaist-ai-webapp-react-research.md (Lines 160-175) — 프로젝트 구조`
- **Dependencies**:
  - Task 4.1~4.5 완료

**`src/index.css`:**

```css
@import "tailwindcss";
```

**`src/main.tsx`:**

```typescript
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App';

const rootElement = document.getElementById('root');
if (!rootElement) throw new Error('Root element not found');

createRoot(rootElement).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
```

**`src/App.tsx`:**

```typescript
import { HealthStatus } from './components/HealthStatus';
import { PDFUploadPanel } from './components/PDFUploadPanel';
import { ChatPanel } from './components/ChatPanel';

export default function App() {
  const appName = import.meta.env.VITE_APP_NAME ?? 'KAIST PDF Chatbot';

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      <header className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
        <h1 className="font-bold text-gray-900">{appName}</h1>
        <HealthStatus />
      </header>

      <main className="flex-1 p-4 grid grid-cols-1 md:grid-cols-[360px_1fr] gap-4 min-h-0">
        <PDFUploadPanel />
        <ChatPanel />
      </main>
    </div>
  );
}
```

---

### Task 5.2: `kaist-ai-infra/azure.yaml` 업데이트

`kaist-ai-webapp` 서비스 항목 추가. `azd deploy`가 Static Web App에 webapp을 배포하도록 연결.

- **Files**:
  - `kaist-ai-infra/azure.yaml` — `kaist-ai-webapp` 서비스 항목 추가
- **Success**:
  - `kaist-ai-webapp.host: staticwebapp`, `project: ../kaist-ai-webapp`, `dist: dist` 포함
- **Research References**:
  - `.copilot/research/20260327-kaist-ai-webapp-react-research.md (Lines 556-575) — azure.yaml 완성본`
- **Dependencies**:
  - Task 5.1 완료

기존 `azure.yaml`에 `kaist-ai-webapp` 서비스 블록 추가:

```yaml
  kaist-ai-webapp:
    host: staticwebapp
    project: ../kaist-ai-webapp
    dist: dist
```

---

## Phase 6: 빌드 검증

### Task 6.1: `npm install` 실행

`kaist-ai-webapp/` 디렉터리에서 `npm install` 실행. `node_modules/` 설치 완료 확인.

- **Files**:
  - `kaist-ai-webapp/node_modules/` — 자동 생성
  - `kaist-ai-webapp/package-lock.json` — 자동 생성
- **Success**:
  - `npm install` 오류 없이 완료
  - `node_modules/.bin/vite` 존재 확인
- **Research References**:
  - `.copilot/research/20260327-kaist-ai-webapp-react-research.md (Lines 651-655) — 기술 요구사항`
- **Dependencies**:
  - Phase 1~5 완료 (package.json 존재해야 함)

---

### Task 6.2: `npm run build` 실행 및 검증

TypeScript 컴파일 + Vite 빌드 실행. `dist/` 생성, 타입 에러 없음 확인.

- **Files**:
  - `kaist-ai-webapp/dist/` — 자동 생성
- **Success**:
  - `tsc -b` 타입 에러 없음
  - `vite build` 완료 (`dist/index.html`, `dist/assets/` 생성)
- **Research References**:
  - `.copilot/research/20260327-kaist-ai-webapp-react-research.md (Lines 651-655) — 빌드 명령`
- **Dependencies**:
  - Task 6.1 완료

---

## Dependencies

- Node.js 20.x LTS
- npm 10.x
- `VITE_API_FUNCTION_KEY`: `az functionapp function keys list --name func-kaist-ai-agent-dev-krc --resource-group kaist-ai-agent-rg --function-name pdf_upload --query value -o tsv`

## Success Criteria

- 모든 13개 핵심 파일 생성 완료
- `npm run build` 성공 (TypeScript 오류 없음, `dist/` 생성)
- `kaist-ai-infra/azure.yaml`에 `kaist-ai-webapp` 서비스 등록
