---
mode: agent
model: Claude Sonnet 4.6
---

<!-- markdownlint-disable-file -->

# Implementation Prompt: kaist-ai-webapp React Frontend 구현

## Implementation Instructions

### Step 1: Changes Tracking 파일 생성

`.copilot/changes/` 디렉터리에 `20260327-kaist-ai-webapp-changes.md` 파일이 없으면 생성하세요.

### Step 2: 구현 실행

`.copilot/plans/20260327-kaist-ai-webapp-plan.instructions.md` 파일의 각 Phase와 Task를 순서대로 구현하세요.

구현 시 다음 파일들을 반드시 참조하세요:

- **플랜**: `.copilot/plans/20260327-kaist-ai-webapp-plan.instructions.md`
- **상세**: `.copilot/details/20260327-kaist-ai-webapp-details.md`
- **리서치**: `.copilot/research/20260327-kaist-ai-webapp-react-research.md`

**CRITICAL — 반드시 지켜야 할 사항**:

1. **snake_case API 타입**: 백엔드 Pydantic 모델이 snake_case로 직렬화됨. TypeScript 타입에서 `document_id`, `file_name`, `chunk_count`, `chunk_id`, `relevance_score`, `uploaded_at` 등 snake_case 사용. 예외: `ChatHistoryResponse.hasMore` (raw dict 반환으로 camelCase)

2. **HTTP 202 for upload**: `/api/pdf/upload` 엔드포인트는 HTTP **202** 반환 (200 아님). axios default validators는 2xx 전체를 성공으로 처리하므로 별도 처리 불필요.

3. **Tailwind CSS v4**: `tailwind.config.ts` 파일 생성 금지. postcss.config.js 생성 금지. `src/index.css`에 `@import "tailwindcss"` 한 줄만 추가. `vite.config.ts`에 `@tailwindcss/vite` 플러그인만 사용.

4. **환경변수명**: `VITE_API_BASE_URL` 사용 금지. 반드시 `VITE_API_ENDPOINT` 사용.

5. **Function Key**: 헤더명 `x-functions-key`, 환경변수명 `VITE_API_FUNCTION_KEY`.

6. **azure.yaml**: `kaist-ai-infra/azure.yaml`에 `kaist-ai-webapp` 서비스 항목 반드시 추가.

**CRITICAL**: `${input:phaseStop:true}` 가 true이면 각 Phase 완료 후 사용자 확인을 받고 진행하세요.
**CRITICAL**: `${input:taskStop:false}` 가 true이면 각 Task 완료 후 사용자 확인을 받고 진행하세요.

### Step 3: 구현 후 검증

모든 Phase 완료 후:

1. `kaist-ai-webapp/` 디렉터리에서 `npm install` 실행
2. `npm run build` 실행하여 TypeScript 오류 없음 및 `dist/` 생성 확인
3. 빌드 오류 발생 시 즉시 수정

### Step 4: 완료 처리

모든 Phase 체크 완료 후:

1. `.copilot/changes/20260327-kaist-ai-webapp-changes.md` 의 변경 내역 요약을 마크다운 링크와 함께 사용자에게 제공
   - 전체 요약은 간결하게
   - 모든 파일 참조는 마크다운 링크로 표시

2. 다음 문서 링크 제공:
   - [플랜](.copilot/plans/20260327-kaist-ai-webapp-plan.instructions.md)
   - [상세](.copilot/details/20260327-kaist-ai-webapp-details.md)
   - [리서치](.copilot/research/20260327-kaist-ai-webapp-react-research.md)

3. **MANDATORY**: `.copilot/prompts/implement-kaist-ai-webapp.prompt.md` 파일 삭제 시도

## Success Criteria

- [ ] `.copilot/changes/20260327-kaist-ai-webapp-changes.md` 파일 생성
- [ ] `kaist-ai-webapp/package.json` 생성 (React 19, Vite 6, Tailwind v4)
- [ ] `kaist-ai-webapp/tsconfig.json`, `tsconfig.app.json`, `tsconfig.node.json` 생성
- [ ] `kaist-ai-webapp/vite.config.ts` 생성 (@tailwindcss/vite 플러그인 포함)
- [ ] `kaist-ai-webapp/index.html` 생성
- [ ] `kaist-ai-webapp/.env.example` 생성 (VITE_API_ENDPOINT, VITE_API_FUNCTION_KEY)
- [ ] `kaist-ai-webapp/staticwebapp.config.json` 생성
- [ ] `kaist-ai-webapp/src/types/index.ts` 생성 (snake_case 타입)
- [ ] `kaist-ai-webapp/src/api/client.ts` 생성 (x-functions-key 헤더)
- [ ] `kaist-ai-webapp/src/hooks/usePDFUpload.ts` 생성 (폴링 포함)
- [ ] `kaist-ai-webapp/src/hooks/useChat.ts` 생성
- [ ] `kaist-ai-webapp/src/components/HealthStatus.tsx` 생성
- [ ] `kaist-ai-webapp/src/components/SourceCitation.tsx` 생성
- [ ] `kaist-ai-webapp/src/components/ChatMessage.tsx` 생성
- [ ] `kaist-ai-webapp/src/components/PDFUploadPanel.tsx` 생성
- [ ] `kaist-ai-webapp/src/components/ChatPanel.tsx` 생성
- [ ] `kaist-ai-webapp/src/main.tsx`, `src/App.tsx`, `src/index.css` 생성
- [ ] `kaist-ai-infra/azure.yaml` 업데이트 (kaist-ai-webapp 서비스 추가)
- [ ] `npm install` 성공
- [ ] `npm run build` 성공 (TypeScript 오류 없음, dist/ 생성)
