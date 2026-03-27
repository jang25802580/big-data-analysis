---
applyTo: ".copilot/changes/20260327-kaist-ai-webapp-changes.md"
---

<!-- markdownlint-disable-file -->

# Task Checklist: kaist-ai-webapp React Frontend 구현

## Overview

`kaist-ai-webapp/`에 Vite + React 19 + TypeScript + Tailwind CSS v4 기반 PDF 챗봇 프론트엔드를 스캐폴딩하고, 기존 Azure Functions 백엔드와 연동하여 Azure Static Web App에 배포 가능한 상태로 구현한다.

## Objectives

- `kaist-ai-webapp/`에 완전한 Vite React TypeScript 프로젝트 구조 생성
- PDF 업로드(드래그앤드롭 + 진행률 + 상태 폴링) UI 구현
- RAG 채팅 인터페이스(메시지 히스토리 + 소스 인용) 구현
- `https://func-kaist-ai-agent-dev-krc.azurewebsites.net` 백엔드와 연동
- `kaist-ai-infra/azure.yaml`에 webapp 서비스 등록
- `npm run build` 에러 없이 `dist/` 생성 검증

## Research Summary

### Project Files

- `kaist-ai-webapp/` — 현재 비어 있음, 전체 신규 생성 대상
- `kaist-ai-infra/azure.yaml` — webapp 서비스 항목 추가 필요
- `kaist-ai-infra/infra/modules/staticwebapp.bicep` — `appLocation: '/kaist-ai-webapp'`, `outputLocation: 'dist'`, `VITE_API_ENDPOINT` 환경변수 설정됨
- `kaist-ai-functions/function_app.py` — 백엔드 API 엔드포인트 (health ANONYMOUS, 나머지 FUNCTION key 필요)
- `kaist-ai-functions/shared/models.py` — Pydantic 모델이 snake_case 직렬화

### External References

- `.copilot/research/20260327-kaist-ai-webapp-react-research.md` — 전체 리서치 (패키지 버전, 컴포넌트 구조, API 타입, 설정 파일 예제)
- Tailwind CSS v4 + `@tailwindcss/vite` — `tailwind.config.ts` 불필요, `@import "tailwindcss"` 한 줄
- React 19 + Vite 6 공식 스캐폴드 구조

### Standards References

- `.github/copilot-instructions.md` — 명시적 변수명, 모듈형 설계, 보안 우선

## Implementation Checklist

### [ ] Phase 1: 프로젝트 설정 파일 생성

- [ ] Task 1.1: `package.json` 생성
  - Details: .copilot/details/20260327-kaist-ai-webapp-details.md (Lines 20-55)

- [ ] Task 1.2: TypeScript 설정 파일 생성 (`tsconfig.json`, `tsconfig.app.json`, `tsconfig.node.json`)
  - Details: .copilot/details/20260327-kaist-ai-webapp-details.md (Lines 56-110)

- [ ] Task 1.3: `vite.config.ts` 생성
  - Details: .copilot/details/20260327-kaist-ai-webapp-details.md (Lines 111-135)

- [ ] Task 1.4: `index.html` 생성
  - Details: .copilot/details/20260327-kaist-ai-webapp-details.md (Lines 136-150)

- [ ] Task 1.5: `.env.example`, `staticwebapp.config.json` 생성
  - Details: .copilot/details/20260327-kaist-ai-webapp-details.md (Lines 151-210)

### [ ] Phase 2: TypeScript 타입 및 API 클라이언트

- [ ] Task 2.1: `src/types/index.ts` 생성 (snake_case API 응답 타입)
  - Details: .copilot/details/20260327-kaist-ai-webapp-details.md (Lines 211-290)

- [ ] Task 2.2: `src/api/client.ts` 생성 (axios 인스턴스 + 타입화된 API 함수)
  - Details: .copilot/details/20260327-kaist-ai-webapp-details.md (Lines 291-360)

### [ ] Phase 3: 커스텀 훅

- [ ] Task 3.1: `src/hooks/usePDFUpload.ts` 생성 (업로드 + 2초 폴링)
  - Details: .copilot/details/20260327-kaist-ai-webapp-details.md (Lines 361-430)

- [ ] Task 3.2: `src/hooks/useChat.ts` 생성 (메시지 상태 + 세션 관리)
  - Details: .copilot/details/20260327-kaist-ai-webapp-details.md (Lines 431-490)

### [ ] Phase 4: React 컴포넌트

- [ ] Task 4.1: `src/components/HealthStatus.tsx` 생성
  - Details: .copilot/details/20260327-kaist-ai-webapp-details.md (Lines 491-530)

- [ ] Task 4.2: `src/components/SourceCitation.tsx` 생성
  - Details: .copilot/details/20260327-kaist-ai-webapp-details.md (Lines 531-560)

- [ ] Task 4.3: `src/components/ChatMessage.tsx` 생성
  - Details: .copilot/details/20260327-kaist-ai-webapp-details.md (Lines 561-600)

- [ ] Task 4.4: `src/components/PDFUploadPanel.tsx` 생성
  - Details: .copilot/details/20260327-kaist-ai-webapp-details.md (Lines 601-660)

- [ ] Task 4.5: `src/components/ChatPanel.tsx` 생성
  - Details: .copilot/details/20260327-kaist-ai-webapp-details.md (Lines 661-720)

### [ ] Phase 5: 진입점 및 azd 통합

- [ ] Task 5.1: `src/main.tsx`, `src/App.tsx`, `src/index.css` 생성
  - Details: .copilot/details/20260327-kaist-ai-webapp-details.md (Lines 721-770)

- [ ] Task 5.2: `kaist-ai-infra/azure.yaml` 업데이트 (webapp 서비스 추가)
  - Details: .copilot/details/20260327-kaist-ai-webapp-details.md (Lines 771-800)

### [ ] Phase 6: 빌드 검증

- [ ] Task 6.1: `npm install` 실행 및 의존성 설치
  - Details: .copilot/details/20260327-kaist-ai-webapp-details.md (Lines 801-820)

- [ ] Task 6.2: `npm run build` 실행 — TypeScript 에러 없이 `dist/` 생성 확인
  - Details: .copilot/details/20260327-kaist-ai-webapp-details.md (Lines 821-840)

## Dependencies

- Node.js 20.x LTS
- npm
- React 19, Vite 6, TypeScript 5.7, Tailwind CSS v4
- axios ^1.7.9, react-dropzone ^14.3.5, lucide-react ^0.460.0
- `VITE_API_FUNCTION_KEY` — `az functionapp function keys list` 명령으로 획득 필요

## Success Criteria

- `kaist-ai-webapp/` 내 모든 파일 생성 완료 (13개 핵심 파일)
- `npm run build` 성공적으로 완료 (`dist/` 생성, TypeScript 컴파일 오류 없음)
- `kaist-ai-infra/azure.yaml`에 `kaist-ai-webapp` 서비스 등록 완료
- 로컬 `npm run dev` 실행 시 `http://localhost:5173` 접근 가능
