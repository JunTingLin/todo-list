# Implementation Plan: 具備可觀測性的 TODO API 服務

**Branch**: `001-todo-api` | **Date**: 2026-01-18 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-todo-api/spec.md`

## Summary

本功能實作一個 RESTful API 待辦事項管理系統，重點展示可觀測性最佳實踐。系統提供完整的 CRUD 操作，並內建結構化日誌、請求追蹤（request_id）、Prometheus 指標暴露與健康檢查端點。採用 Python 3.11+ with FastAPI 框架，使用記憶體儲存以簡化部署，專注於可觀測性功能的展示與驗證。

**技術方法**：
- FastAPI 提供高效能的異步 API 端點與自動 OpenAPI 文件生成
- Pydantic 模型確保資料驗證與類型安全
- 結構化 JSON 日誌輸出至 stdout，便於容器環境日誌收集
- Prometheus client 暴露標準指標（請求計數、延遲直方圖）
- Pytest + FastAPI TestClient 支援 TDD 測試先行開發

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**:
- FastAPI 0.100+ (Web framework)
- Uvicorn (ASGI server)
- Pydantic 2.0+ (Data validation)
- prometheus-client (Metrics exposure)
- structlog (Structured logging)

**Storage**: In-memory (Python dict/list)
**Testing**: Pytest + FastAPI TestClient + pytest-cov
**Target Platform**: Linux server (Docker container)
**Project Type**: Single (API-only service)
**Performance Goals**:
- p95 延遲 < 100ms (CRUD operations)
- p99 健康檢查 < 10ms
- 支援基本並發處理（標準 HTTP server 能力）

**Constraints**:
- 無外部依賴（資料庫、快取）
- 無使用者驗證/授權機制
- 資料僅存於記憶體（重啟後遺失）
- 本地運行為主（非生產環境部署）

**Scale/Scope**:
- 小型展示專案
- 3 個核心 API 端點 (CRUD + list)
- 2 個監控端點 (health + metrics)
- 35 個測試案例
- 單一服務架構

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ I. 可觀測性優先

**要求**：
- 結構化日誌（JSON 格式，包含 request_id、timestamp、method、path、status_code、latency）
- 請求追蹤（每個請求唯一 request_id）
- 指標量測（請求次數、延遲分布，避免高基數標籤）
- 錯誤可追溯（完整上下文記錄，對外不洩漏內部細節）
- 健康檢查端點

**驗證**：
- ✅ FR-008 至 FR-013 定義結構化日誌與 request_id 追蹤機制
- ✅ FR-017 至 FR-021 定義健康檢查與指標暴露需求
- ✅ FR-014 至 FR-016 定義錯誤處理與日誌記錄
- ✅ SC-002、SC-003 要求 100% 日誌完整性與追蹤準確率
- ✅ 技術選型：structlog（結構化日誌）+ prometheus-client（指標）

**狀態**：✅ 通過（規格完全符合可觀測性優先原則）

---

### ✅ II. 測試先行

**要求**：
- 測試必須先於實作撰寫（TDD）
- 測試必須先失敗（紅燈），證明測試有效
- 實作必須讓測試通過（綠燈）
- 違反此原則的程式碼不得合併

**驗證**：
- ✅ testcase.md 包含 35 個測試案例，涵蓋所有功能需求
- ✅ 技術選型：Pytest + FastAPI TestClient 支援 TDD
- ✅ 測試案例組織：契約測試、整合測試、單元測試分層
- ✅ 所有使用者故事都有對應的驗收情境測試

**狀態**：✅ 通過（測試案例已完整準備，支援 TDD 流程）

---

### ✅ III. 契約測試與整合測試

**要求**：
- 每個對外 API 端點必須有契約測試
- 每個使用者故事至少一個整合測試

**驗證**：
- ✅ TC-001 系列（16 個測試）：涵蓋所有 CRUD API 端點
- ✅ TC-002 系列（5 個測試）：驗證日誌與追蹤功能整合
- ✅ TC-004 系列（5 個測試）：驗證健康檢查與指標端點
- ✅ 3 個使用者故事各有完整驗收情境測試

**狀態**：✅ 通過（測試覆蓋率 100%，契約與整合測試完整）

---

### ✅ IV. 微服務單一職責

**要求**：
- 服務職責明確
- 可獨立部署、擴展、失敗
- 資料所有權明確

**驗證**：
- ✅ 單一服務：TODO API 管理 + 可觀測性展示
- ✅ 獨立部署：無外部依賴（FR-023）
- ✅ 資料所有權：待辦事項資料完全由本服務管理（記憶體儲存）
- ✅ 明確界線：Out of Scope 清楚排除驗證、持久化、分散式追蹤等

**狀態**：✅ 通過（單一職責清晰，範圍界線明確）

---

### ✅ V. 程式碼簡潔性（Simplicity）

**要求**：
- 從簡單開始，遵循 YAGNI 原則
- 避免過度設計
- 複雜性必須有充分理由

**驗證**：
- ✅ 簡化資料模型：Todo 僅 3 個欄位（id, title, completed）
- ✅ 記憶體儲存：避免資料庫複雜性
- ✅ 無驗證/授權：專注核心功能展示
- ✅ 標準 RESTful 設計：無自定義協議或複雜抽象

**狀態**：✅ 通過（設計簡潔，符合 YAGNI 原則）

---

### ✅ VI. 版本管理與破壞性變更

**要求**：
- API 版本明確管理（MAJOR.MINOR.PATCH）
- 破壞性變更需遷移指南

**驗證**：
- ✅ SC-009 要求指標格式穩定（無破壞性變更）
- ✅ API 契約將透過 OpenAPI 規格明確定義
- ⚠️ 初始版本（v1.0.0），暫無版本演進需求

**狀態**：✅ 通過（初始版本，已規劃版本管理機制）

---

### Constitution Check 總結

**結果**：✅ 全部通過，無違規需要解釋

所有核心原則都在規格與設計中得到體現：
- 可觀測性優先：完整的日誌、追蹤、指標機制
- 測試先行：35 個測試案例完整準備
- 契約與整合測試：100% API 端點覆蓋
- 單一職責：清晰的服務界線
- 簡潔性：最小化設計，專注核心功能
- 版本管理：OpenAPI 契約明確定義

## Project Structure

### Documentation (this feature)

```text
specs/001-todo-api/
├── spec.md              # 功能規格（已完成）
├── testcase.md          # 測試案例（已完成）
├── checklists/
│   └── requirements.md  # 規格品質檢查清單（已完成）
├── plan.md              # 本檔案（實作計畫）
├── research.md          # Phase 0 輸出（技術研究）
├── data-model.md        # Phase 1 輸出（資料模型）
├── quickstart.md        # Phase 1 輸出（快速開始指南）
└── contracts/           # Phase 1 輸出（API 契約）
    └── openapi.yaml     # OpenAPI 3.0 規格
```

### Source Code (repository root)

```text
src/
├── models/              # Pydantic 資料模型
│   └── todo.py          # Todo 實體定義
├── api/                 # FastAPI 路由與端點
│   ├── todos.py         # CRUD 端點
│   ├── health.py        # 健康檢查端點
│   └── metrics.py       # 指標端點
├── storage/             # 記憶體儲存層
│   └── memory.py        # In-memory store 實作
├── middleware/          # 中介層
│   ├── logging.py       # 請求日誌中介層
│   └── request_id.py    # Request ID 處理
└── main.py              # FastAPI 應用程式進入點

tests/
├── contract/            # 契約測試
│   ├── test_todo_api.py             # Todo API 契約
│   ├── test_health_api.py           # 健康檢查契約
│   └── test_metrics_api.py          # 指標端點契約
├── integration/         # 整合測試
│   ├── test_todo_lifecycle.py      # 完整 CRUD 流程
│   ├── test_logging_integration.py # 日誌整合測試
│   └── test_metrics_integration.py # 指標整合測試
└── unit/                # 單元測試
    ├── test_models.py               # 模型驗證測試
    └── test_storage.py              # 儲存層測試

config/
├── logging.yaml         # Structlog 設定
└── prometheus.yml       # Prometheus 抓取設定（local demo）

docker/
├── Dockerfile           # API 服務容器
└── docker-compose.yml   # 本地 demo 環境（API + Prometheus + Grafana）

pyproject.toml           # Python 專案設定（Poetry）
pytest.ini               # Pytest 設定
.gitignore
README.md
```

**Structure Decision**:

選擇 **Option 1: Single project** 結構，理由：
1. 單一 API 服務，無前端或多服務需求
2. 簡化專案結構，符合 YAGNI 原則
3. FastAPI 應用程式自然適合單一專案結構
4. 測試組織清晰：contract / integration / unit 三層分離

**目錄說明**：
- `src/`: 應用程式原始碼，按功能分層（models, api, storage, middleware）
- `tests/`: 測試程式碼，按測試類型分層（符合憲章測試標準）
- `config/`: 設定檔（日誌、監控）
- `docker/`: 容器化與本地 demo 環境

## Complexity Tracking

> **本專案無憲章違規，此區塊留空**

無複雜性需要額外解釋。所有設計決策都符合簡潔性原則。
