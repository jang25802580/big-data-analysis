---
goal: Implement Azure Functions Python API Backend Skeleton with Google Gemini RAG Pipeline
version: 1.0
date_created: 2026-03-24
last_updated: 2026-03-24
owner: KAIST Big Data Analysis Team
status: 'Planned'
tags: [feature, azure-functions, python, gcp, gemini, langchain, rag, api-backend]
---

# Introduction

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

이 계획서는 `kaist-ai-functions/` 경로에 Azure Functions Python 3.11 기반 API 백엔드 뼈대를 구성하는 구현 단계를 정의합니다. Google Cloud Platform(GCP) 프로젝트를 생성하고 Google Gemini 3 Pro를 LLM 및 임베딩 모델로 연동하며, `langchain-google-genai` 패키지를 통해 RAG(Retrieval-Augmented Generation) 파이프라인을 구성합니다. 인프라는 기존 Bicep 템플릿(`kaist-ai-infra/`)을 통해 이미 프로비저닝된 Azure Storage, Cosmos DB, Key Vault를 활용하며, 로컬 모의 스토리지(Azurite) 대신 Azure Storage 클라우드를 직접 사용합니다.

구성 대상:
- **Azure Functions v2 (Python 3.11)** — HTTP 트리거 기반 REST API 엔드포인트
- **Google Gemini 3 Pro** — LLM 응답 생성 및 텍스트 임베딩 (`text-embedding-004`)
- **LangChain Google GenAI** — `langchain-google-genai` 패키지 기반 LLM/임베딩 통합
- **Azure Blob Storage** — PDF 파일 저장 (클라우드 직접 연결)
- **Azure Cosmos DB** — 문서 메타데이터, 청크 임베딩, 채팅 세션 저장
- **Azure Key Vault** — `gemini-api-key`, `cosmos-connection-string`, `storage-connection-string` 비밀값 관리

## 1. Requirements & Constraints

- **REQ-001**: API 서버는 Python 3.11 런타임을 사용하는 Azure Functions v2 모델로 구현해야 한다
- **REQ-002**: LLM 및 임베딩 모델은 Google Gemini 3 Pro (`gemini-2.0-flash` / `text-embedding-004`)를 사용해야 한다
- **REQ-003**: LangChain 통합은 `langchain-google-vertexai` 대신 `langchain-google-genai` 패키지를 사용해야 한다
- **REQ-004**: 로컬 개발 환경에서도 Azurite 없이 Azure Storage 클라우드를 직접 연결해야 한다
- **REQ-005**: GCP 인증 키(`gemini-api-key`)는 Azure Key Vault의 `gemini-api-key` 시크릿에 저장되어야 한다
- **REQ-006**: 함수 앱은 `kaist-ai-infra/` Bicep 인프라가 출력하는 리소스 이름을 환경변수로 참조해야 한다
- **REQ-007**: 구현할 HTTP 엔드포인트: `GET /api/health`, `POST /api/pdf/upload`, `GET /api/pdf/status/{documentId}`, `POST /api/chat/query`, `GET /api/chat/history`
- **REQ-008**: PDF 텍스트 추출에는 `PyMuPDF(fitz)` 패키지를 사용해야 한다
- **REQ-009**: 데이터 모델은 Pydantic v2로 정의해야 한다
- **REQ-010**: 모든 Azure 리소스 접근은 관리 ID(Managed Identity) 또는 Key Vault 시크릿 참조를 통해야 한다

- **SEC-001**: `local.settings.json`은 `.gitignore`에 추가하여 자격증명을 저장소에 커밋하지 않아야 한다
- **SEC-002**: GCP API 키는 코드 내 하드코딩 금지이며 환경변수 `GOOGLE_API_KEY`를 통해서만 참조해야 한다
- **SEC-003**: 업로드된 PDF 파일 이름은 UUID 기반으로 재명명하여 경로 순회(Path Traversal) 공격을 방지해야 한다
- **SEC-004**: HTTP 트리거 함수는 `authLevel: function`을 기본으로 사용하고, 인증 레이어는 향후 확장을 위해 별도 미들웨어로 분리해야 한다
- **SEC-005**: Cosmos DB 연결은 `azure-cosmos` SDK + `DefaultAzureCredential`(관리 ID)를 통해야 한다; connection string은 로컬 개발 전용으로만 허용한다
- **SEC-006**: 파일 업로드 시 MIME 타입을 서버 측에서 검증하여 `application/pdf` 외 파일 업로드를 거부해야 한다

- **CON-001**: Azure Functions 소비 플랜(Consumption Plan)은 HTTP 트리거 제한 시간이 10분이므로, 대용량 PDF 처리는 비동기 큐 방식으로 설계해야 한다
- **CON-002**: `langchain-google-genai` 패키지는 `GOOGLE_API_KEY` 환경변수를 통해 인증하며, GCP 서비스 계정 JSON 방식을 사용하려면 추가 설정이 필요하다
- **CON-003**: Azure Functions v2 Python 모델은 `function_app.py` 단일 진입점에 데코레이터로 모든 함수를 등록한다
- **CON-004**: Cosmos DB Serverless 모드의 최대 처리량은 5,000 RU/s로 제한된다
- **CON-005**: 이 계획서의 범위는 뼈대(skeleton) 구현이며, 완전한 인증(JWT 검증) 및 멀티테넌트 분리는 후속 계획서에서 다룬다

- **GUD-001**: 모든 함수에 Application Insights를 통한 구조적 로깅을 적용한다 (`logging` 모듈 표준 사용)
- **GUD-002**: 외부 서비스 호출에는 `tenacity` 기반 지수 백오프 재시도 로직을 구현한다
- **GUD-003**: 서비스 레이어는 함수 진입점(function_app.py)과 분리하여 독립적으로 테스트 가능하도록 구성한다
- **GUD-004**: 환경변수는 중앙화된 `shared/config.py` 모듈을 통해서만 참조한다

- **PAT-001**: Azure Functions Python v2 프로그래밍 모델 사용 (데코레이터 기반)
- **PAT-002**: Repository 패턴으로 Cosmos DB 데이터 접근 추상화
- **PAT-003**: Factory 패턴으로 LLM 및 임베딩 클라이언트 생성 관리
- **PAT-004**: `DefaultAzureCredential`로 로컬/클라우드 환경 통합 인증

## 2. Implementation Steps

### Implementation Phase 1: GCP 프로젝트 생성 및 Gemini API 설정

- GOAL-001: Google Cloud Platform 프로젝트를 생성하고 Gemini API 키를 발급하여 Azure Key Vault에 등록한다

| Task     | Description                                                                                                                                                         | Completed | Date |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-001 | [Google Cloud Console](https://console.cloud.google.com)에서 신규 GCP 프로젝트 생성: 이름 `kaist-ai-agent`, 프로젝트 ID는 고유값으로 지정 후 메모              |           |      |
| TASK-002 | GCP 콘솔 → **API 및 서비스** → **라이브러리**에서 `Generative Language API` (`generativelanguage.googleapis.com`) 활성화                                        |           |      |
| TASK-003 | [Google AI Studio](https://aistudio.google.com/app/apikey)에서 API 키 생성: 키 이름 `kaist-ai-agent-key`, 생성된 키 값 복사                                      |           |      |
| TASK-004 | Azure CLI로 Key Vault의 `gemini-api-key` 시크릿 값을 실제 API 키로 업데이트: `az keyvault secret set --vault-name <KEY_VAULT_NAME> --name gemini-api-key --value <API_KEY>` |           |      |
| TASK-005 | GCP 프로젝트 ID를 Key Vault에 추가: `az keyvault secret set --vault-name <KEY_VAULT_NAME> --name google-cloud-project --value <GCP_PROJECT_ID>`                 |           |      |
| TASK-006 | Gemini API 키 동작 확인: `curl "https://generativelanguage.googleapis.com/v1beta/models?key=<API_KEY>"` 실행하여 모델 목록 반환 확인                              |           |      |

### Implementation Phase 2: Azure Functions 프로젝트 구조 초기화

- GOAL-002: `kaist-ai-functions/` 디렉터리에 Azure Functions v2 Python 프로젝트의 뼈대 파일을 생성한다

| Task     | Description                                                                                                                                                         | Completed | Date |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-007 | `kaist-ai-functions/` 디렉터리에서 `func init . --python -m V2` 명령으로 Azure Functions v2 Python 프로젝트 초기화 (Azure Functions Core Tools 필요)             |           |      |
| TASK-008 | `kaist-ai-functions/host.json` 파일 생성: `extensionBundle` v4, `logging.logLevel.default: "Information"`, `functionTimeout: "00:10:00"` 설정                     |           |      |
| TASK-009 | `kaist-ai-functions/requirements.txt` 파일 생성: 아래 **DEP** 섹션에 명시된 모든 패키지 버전 고정하여 작성                                                        |           |      |
| TASK-010 | `kaist-ai-functions/local.settings.json.sample` 파일 생성: 필요한 모든 환경변수 키를 빈 값으로 작성 (실제 값 없이 키 목록만 문서화)                              |           |      |
| TASK-011 | `kaist-ai-functions/.funcignore` 파일 생성: `.git`, `.venv`, `__pycache__`, `*.pyc`, `tests/`, `local.settings.json` 제외 설정                                 |           |      |
| TASK-012 | `kaist-ai-functions/.gitignore`에 `local.settings.json`, `.venv/`, `__pycache__/`, `*.pyc` 추가                                                                  |           |      |
| TASK-013 | `kaist-ai-functions/` 하위 디렉터리 구조 생성: `shared/`, `services/`, `tests/` 디렉터리 및 각 `__init__.py` 파일 생성                                           |           |      |

### Implementation Phase 3: 공유 설정 및 데이터 모델 구현

- GOAL-003: 중앙화된 환경변수 로딩과 Pydantic v2 기반 데이터 모델을 구현한다

| Task     | Description                                                                                                                                                                           | Completed | Date |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-014 | `shared/config.py` 구현: `pydantic_settings.BaseSettings`를 상속하는 `AppConfig` 클래스 정의, `GOOGLE_API_KEY`, `COSMOS_ENDPOINT`, `COSMOS_DATABASE_NAME`, `STORAGE_ACCOUNT_NAME`, `PDF_CONTAINER_NAME`, `APPLICATIONINSIGHTS_CONNECTION_STRING` 필드 포함 |           |      |
| TASK-015 | `shared/models.py` 구현: `DocumentRecord`(Cosmos DB 문서 컨테이너용), `ChunkRecord`(청크+임베딩용), `ChatSession`(채팅 세션용), `UploadResponse`, `StatusResponse`, `ChatQueryRequest`, `ChatQueryResponse`, `SourceReference` Pydantic v2 모델 정의 |           |      |
| TASK-016 | `shared/exceptions.py` 구현: `PDFProcessingError`, `EmbeddingError`, `StorageError`, `DocumentNotFoundError`, `InvalidFileTypeError` 커스텀 예외 클래스 정의                       |           |      |

### Implementation Phase 4: 서비스 레이어 구현

- GOAL-004: Azure Storage, Cosmos DB, PDF 추출, Gemini 임베딩/LLM 서비스 클래스를 구현한다

| Task     | Description                                                                                                                                                                           | Completed | Date |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-017 | `services/storage_service.py` 구현: `BlobStorageService` 클래스, `DefaultAzureCredential` + `BlobServiceClient` 초기화, `upload_pdf(file_bytes, blob_name)`, `download_pdf(blob_name)`, `delete_pdf(blob_name)` 메서드 구현 |           |      |
| TASK-018 | `services/cosmos_service.py` 구현: `CosmosRepository` 클래스, `DefaultAzureCredential` + `CosmosClient` 초기화, `upsert_document`, `get_document`, `upsert_chunk`, `get_chunks_by_document`, `upsert_session`, `get_session` 메서드 구현 |           |      |
| TASK-019 | `services/pdf_service.py` 구현: `PDFService` 클래스, `pymupdf(fitz)` 기반 `extract_text(pdf_bytes) -> list[dict]` 메서드 (페이지별 텍스트 추출), `chunk_text(pages, chunk_size=1000, overlap=200) -> list[str]` 메서드 구현 |           |      |
| TASK-020 | `services/embedding_service.py` 구현: `EmbeddingService` 클래스, `langchain_google_genai.GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")` 초기화, `embed_texts(texts: list[str]) -> list[list[float]]` 배치 임베딩 메서드 구현 |           |      |
| TASK-021 | `services/llm_service.py` 구현: `LLMService` 클래스, `langchain_google_genai.ChatGoogleGenerativeAI(model="gemini-2.0-flash")` 초기화, `generate_rag_answer(query, context_chunks) -> str` 메서드 구현 (LangChain `ChatPromptTemplate` 사용) |           |      |

### Implementation Phase 5: Azure Functions HTTP 엔드포인트 구현

- GOAL-005: `function_app.py`에 모든 HTTP 트리거 함수를 Azure Functions v2 데코레이터 방식으로 등록한다

| Task     | Description                                                                                                                                                                           | Completed | Date |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-022 | `function_app.py` 진입점 구성: `azure.functions.FunctionApp` 인스턴스 생성, HTTP 인증 레벨 `func.AuthLevel.FUNCTION` 설정, 서비스 의존성 초기화 (싱글턴 패턴)                      |           |      |
| TASK-023 | `GET /api/health` 함수 구현: Azure Storage, Cosmos DB, Gemini API 연결 상태를 각각 확인하여 `{"status": "healthy", "checks": {"storage": "ok", "cosmos": "ok", "gemini": "ok"}}` 형태로 응답 |           |      |
| TASK-024 | `POST /api/pdf/upload` 함수 구현: multipart form-data 파싱, MIME 타입 `application/pdf` 검증, UUID 기반 `documentId` 생성, Blob Storage에 `{documentId}.pdf` 이름으로 업로드, Cosmos DB에 `status: "pending"` 문서 레코드 저장, `UploadResponse` 반환 |           |      |
| TASK-025 | `GET /api/pdf/status/{documentId}` 함수 구현: Cosmos DB에서 문서 레코드 조회, `StatusResponse(documentId, status, progress, chunkCount, error)` 반환, 문서 미존재 시 404 응답      |           |      |
| TASK-026 | `POST /api/pdf/process` 내부 처리 함수 구현 (배경 작업용): Blob에서 PDF 다운로드 → `PDFService`로 텍스트 추출 및 청킹 → `EmbeddingService`로 임베딩 생성 → Cosmos DB `chunks` 컨테이너에 저장 → 문서 상태 `completed`로 업데이트 |           |      |
| TASK-027 | `POST /api/chat/query` 함수 구현: `ChatQueryRequest` 파싱, Cosmos DB에서 쿼리 임베딩과 유사한 상위 5개 청크 검색 (코사인 유사도), `LLMService`로 RAG 응답 생성, `ChatQueryResponse(answer, sources, messageId, timestamp)` 반환 |           |      |
| TASK-028 | `GET /api/chat/history` 함수 구현: `sessionId` 쿼리 파라미터로 Cosmos DB `sessions` 컨테이너 조회, `limit`/`offset` 페이지네이션 지원, 세션 메시지 목록 반환                        |           |      |

### Implementation Phase 6: 로컬 개발 환경 설정 및 배포 준비

- GOAL-006: 로컬 Azure Storage 연결 및 `azure.yaml` 배포 설정을 완성한다

| Task     | Description                                                                                                                                                                           | Completed | Date |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-029 | `local.settings.json` 작성 (`.gitignore`로 제외): `AzureWebJobsStorage`를 실제 Azure Storage 연결 문자열로 설정 (Azurite 사용 안 함), Key Vault에서 가져온 값으로 나머지 환경변수 설정 |           |      |
| TASK-030 | `kaist-ai-infra/azure.yaml` 파일에 `kaist-ai-functions` 서비스 정의 추가: `host: function`, `project: ../kaist-ai-functions`, `language: python` 설정                               |           |      |
| TASK-031 | `kaist-ai-infra/infra/modules/functions.bicep`의 `appSettings`에 Key Vault 시크릿 참조 추가: `GOOGLE_API_KEY: @Microsoft.KeyVault(SecretUri=...)`, `GOOGLE_CLOUD_PROJECT: @Microsoft.KeyVault(SecretUri=...)` |           |      |
| TASK-032 | 로컬에서 `func start` 명령으로 함수 앱 기동 확인: 5개 엔드포인트 등록 로그 출력 확인, `GET /api/health` 호출하여 200 응답 확인                                                    |           |      |

### Implementation Phase 7: 단위 테스트 구현

- GOAL-007: 서비스 레이어와 함수 엔드포인트에 대한 단위 테스트를 작성한다

| Task     | Description                                                                                                                                                                           | Completed | Date |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-033 | `tests/test_pdf_service.py` 작성: 샘플 PDF 바이트를 사용한 `extract_text` 및 `chunk_text` 함수 단위 테스트, 엣지 케이스(빈 PDF, 단일 페이지, 대용량 텍스트) 포함                  |           |      |
| TASK-034 | `tests/test_embedding_service.py` 작성: `EmbeddingService.embed_texts`를 `unittest.mock.patch`로 Gemini API 모킹, 반환값 형식(float 배열) 검증                                     |           |      |
| TASK-035 | `tests/test_health.py` 작성: health check 함수에 대한 단위 테스트, Azure 서비스 클라이언트를 모킹하여 정상/비정상 응답 시나리오 각각 검증                                           |           |      |
| TASK-036 | `tests/test_pdf_upload.py` 작성: PDF 업로드 함수 단위 테스트, 유효한 PDF / 잘못된 MIME 타입 / 50MB 초과 파일 시나리오 각각 검증, Storage와 Cosmos 호출 모킹                        |           |      |

## 3. Alternatives

- **ALT-001**: **Azurite(로컬 스토리지 에뮬레이터) 사용** — 로컬 개발 편의성이 높으나, 클라우드 Storage와 동작 차이(SAS 토큰, Managed Identity 미지원)로 인해 통합 테스트 신뢰도가 낮아 배제
- **ALT-002**: **langchain-google-vertexai 사용** — GCP 서비스 계정 JSON 인증이 필요하고 Vertex AI API 활성화가 필요하나, 이 프로젝트는 API 키 기반의 간단한 연동을 선호하므로 `langchain-google-genai`를 선택
- **ALT-003**: **Azure OpenAI 사용** — Azure 네이티브 통합 장점이 있으나, 아키텍처 스펙(REQ-008)에서 Gemini 통합을 명시하므로 배제
- **ALT-004**: **Azure Durable Functions (상태 저장 워크플로)** — PDF 처리 파이프라인에 적합하나, 초기 뼈대 구현 복잡도를 낮추기 위해 1단계에서는 동기 처리 방식으로 구현하고 향후 확장 시 적용 예정
- **ALT-005**: **FastAPI + Azure Container Apps** — 더 풍부한 API 프레임워크를 제공하나, 기존 인프라 Bicep 템플릿이 Azure Functions 기반으로 설계되어 있어 변경 비용이 큼

## 4. Dependencies

- **DEP-001**: `azure-functions>=1.21.0` — Azure Functions Python v2 런타임 SDK
- **DEP-002**: `azure-storage-blob>=12.23.0` — Azure Blob Storage 클라이언트
- **DEP-003**: `azure-cosmos>=4.7.0` — Azure Cosmos DB 클라이언트
- **DEP-004**: `azure-identity>=1.17.0` — `DefaultAzureCredential` 통합 인증
- **DEP-005**: `azure-keyvault-secrets>=4.8.0` — Key Vault 시크릿 조회 (로컬 개발용)
- **DEP-006**: `langchain-google-genai>=2.0.0` — Google Gemini LLM 및 임베딩 LangChain 통합
- **DEP-007**: `langchain>=0.3.0` — LangChain 코어 (프롬프트 템플릿, 체인 구성)
- **DEP-008**: `langchain-community>=0.3.0` — LangChain 커뮤니티 통합 유틸리티
- **DEP-009**: `pymupdf>=1.24.0` — PDF 텍스트 추출 (`fitz` 모듈)
- **DEP-010**: `pydantic>=2.7.0` — 데이터 모델 정의 및 검증
- **DEP-011**: `pydantic-settings>=2.3.0` — 환경변수 기반 설정 관리
- **DEP-012**: `tenacity>=8.3.0` — 외부 API 호출 재시도 로직
- **DEP-013**: `pytest>=8.2.0` — 단위 테스트 프레임워크 (개발 의존성)
- **DEP-014**: `pytest-asyncio>=0.23.0` — 비동기 함수 테스트 지원 (개발 의존성)
- **DEP-015**: Azure Functions Core Tools v4 — 로컬 개발 및 `func start` 실행 (시스템 의존성)
- **DEP-016**: `kaist-ai-infra/` 인프라 — Cosmos DB, Storage, Key Vault, Function App이 `azd up`으로 사전 프로비저닝되어 있어야 함

## 5. Files

- **FILE-001**: `kaist-ai-functions/function_app.py` — Azure Functions 진입점, 모든 HTTP 트리거 함수 등록
- **FILE-002**: `kaist-ai-functions/host.json` — Functions 호스트 설정 (타임아웃, 로그 레벨, 번들 버전)
- **FILE-003**: `kaist-ai-functions/requirements.txt` — Python 패키지 의존성 (버전 고정)
- **FILE-004**: `kaist-ai-functions/local.settings.json.sample` — 로컬 개발 환경변수 템플릿 (`.gitignore` 제외 대상이 아닌 샘플 파일)
- **FILE-005**: `kaist-ai-functions/.funcignore` — Functions 배포 제외 파일 목록
- **FILE-006**: `kaist-ai-functions/shared/__init__.py` — shared 패키지 초기화
- **FILE-007**: `kaist-ai-functions/shared/config.py` — `AppConfig` 설정 클래스 (환경변수 로딩)
- **FILE-008**: `kaist-ai-functions/shared/models.py` — Pydantic v2 데이터 모델 (`DocumentRecord`, `ChunkRecord`, `ChatSession`, API 요청/응답 모델)
- **FILE-009**: `kaist-ai-functions/shared/exceptions.py` — 커스텀 예외 클래스
- **FILE-010**: `kaist-ai-functions/services/__init__.py` — services 패키지 초기화
- **FILE-011**: `kaist-ai-functions/services/storage_service.py` — Azure Blob Storage 서비스 클래스
- **FILE-012**: `kaist-ai-functions/services/cosmos_service.py` — Cosmos DB 리포지터리 클래스
- **FILE-013**: `kaist-ai-functions/services/pdf_service.py` — PDF 텍스트 추출 및 청킹 서비스
- **FILE-014**: `kaist-ai-functions/services/embedding_service.py` — Google Gemini 임베딩 서비스
- **FILE-015**: `kaist-ai-functions/services/llm_service.py` — Google Gemini LLM RAG 서비스
- **FILE-016**: `kaist-ai-functions/tests/__init__.py` — tests 패키지 초기화
- **FILE-017**: `kaist-ai-functions/tests/test_health.py` — health check 함수 단위 테스트
- **FILE-018**: `kaist-ai-functions/tests/test_pdf_service.py` — PDF 서비스 단위 테스트
- **FILE-019**: `kaist-ai-functions/tests/test_embedding_service.py` — 임베딩 서비스 단위 테스트
- **FILE-020**: `kaist-ai-functions/tests/test_pdf_upload.py` — PDF 업로드 함수 단위 테스트
- **FILE-021**: `kaist-ai-infra/infra/modules/functions.bicep` — Key Vault 시크릿 참조 환경변수 추가 (수정)
- **FILE-022**: `kaist-ai-infra/azure.yaml` — `kaist-ai-functions` 서비스 정의 추가 (수정)

## 6. Testing

- **TEST-001**: `GET /api/health` 엔드포인트 — 모든 서비스(Storage, Cosmos, Gemini) 정상 연결 시 HTTP 200 및 `{"status": "healthy"}` 응답 검증
- **TEST-002**: `POST /api/pdf/upload` — 유효한 PDF 파일 업로드 시 HTTP 202와 `documentId`, `status: "pending"` 포함 응답 검증
- **TEST-003**: `POST /api/pdf/upload` — `application/pdf` 외 MIME 타입 파일 업로드 시 HTTP 400 응답 및 `InvalidFileTypeError` 메시지 검증
- **TEST-004**: `GET /api/pdf/status/{documentId}` — 존재하는 documentId 조회 시 Cosmos DB에서 상태 필드 반환 검증
- **TEST-005**: `GET /api/pdf/status/{documentId}` — 존재하지 않는 documentId 조회 시 HTTP 404 응답 검증
- **TEST-006**: `PDFService.extract_text` — 샘플 PDF 바이트 입력 시 페이지별 텍스트 딕셔너리 반환 형식 검증
- **TEST-007**: `PDFService.chunk_text` — 1000자 청크 크기와 200자 오버랩 적용 시 청크 경계 및 수량 검증
- **TEST-008**: `EmbeddingService.embed_texts` — Gemini API 모킹 후 반환 임베딩 배열 차원 형식 검증
- **TEST-009**: `LLMService.generate_rag_answer` — 컨텍스트 청크 목록 입력 시 LangChain 프롬프트 실행 흐름 검증

## 7. Risks & Assumptions

- **RISK-001**: Google Gemini API 응답 지연 — `text-embedding-004` 배치 임베딩 및 LLM 응답이 Azure Functions 타임아웃(10분)을 초과할 수 있음; 완화책: 청킹 크기 조정, 비동기 처리 패턴 도입
- **RISK-002**: Cosmos DB 벡터 검색 제한 — 현재 Bicep 설정이 벡터 인덱스 정책을 포함하지 않을 경우 코사인 유사도 검색 불가; 완화책: `cosmos.bicep`의 `vectorEmbeddingPolicy` 확인 및 필요 시 수정
- **RISK-003**: `langchain-google-genai` 버전 호환성 — LangChain 버전 간 API 변경이 빈번하므로 `requirements.txt`에 버전을 정확히 고정하지 않으면 배포 후 런타임 오류 발생 가능
- **RISK-004**: Azure Functions 콜드 스타트 — 소비 플랜에서 콜드 스타트 시 Gemini API 클라이언트 초기화 지연이 발생할 수 있음; 완화책: 모듈 레벨 싱글턴 초기화 적용
- **RISK-005**: 50MB 이상 PDF 파일 업로드 — Azure Functions HTTP 요청 크기 제한(100MB)과 메모리 제한으로 인해 대용량 파일 처리 실패 가능; 완화책: SAS URL 기반 클라이언트 직접 업로드 방식으로 향후 전환

- **ASSUMPTION-001**: `kaist-ai-infra/`의 Bicep 인프라가 `azd up`으로 이미 배포된 상태에서 이 구현을 시작한다
- **ASSUMPTION-002**: Cosmos DB `chunks` 컨테이너에 벡터 인덱스 정책이 구성되어 있거나, 없는 경우 이 계획 실행 중 추가 Bicep 수정을 허용한다
- **ASSUMPTION-003**: 개발 환경에 Python 3.11, Azure Functions Core Tools v4, Azure CLI가 설치되어 있다
- **ASSUMPTION-004**: `langchain-google-genai`의 `GoogleGenerativeAIEmbeddings`는 Gemini `text-embedding-004` 모델을 지원한다
- **ASSUMPTION-005**: 초기 뼈대 구현에서는 사용자 인증(JWT 토큰 검증) 없이 Functions 키 기반 인증만 적용하며, 완전한 인증은 후속 계획서에서 구현한다

## 8. Related Specifications / Further Reading

- [Architecture Specification: PDF Knowledge Base Chatbot Agent](../spec/spec-architecture-pdf-chatbot-agent.md)
- [Infrastructure Plan: Azure Bicep Deployment](./infrastructure-azure-bicep-1.md)
- [LangChain Google Generative AI Integration Guide](https://docs.langchain.com/oss/python/integrations/providers/google#google-generative-ai)
- [Azure Functions Python v2 Programming Model](https://learn.microsoft.com/azure/azure-functions/functions-reference-python?tabs=get-started%2Casgi%2Capplication-level&pivots=python-mode-decorators)
- [Google AI Studio API Key Management](https://aistudio.google.com/app/apikey)
- [langchain-google-genai PyPI](https://pypi.org/project/langchain-google-genai/)
- [Azure Cosmos DB Python SDK Vector Search](https://learn.microsoft.com/azure/cosmos-db/nosql/vector-search)
