# Tasks: 具備可觀測性的 TODO API 服務

**輸入文件**: `/specs/001-todo-api/` 目錄下的設計文件
**前置需求**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml, quickstart.md

**測試**: 本專案遵循憲章定義的 TDD 原則。所有測試都是必要的，且必須在實作前先撰寫。

**組織方式**: 任務按使用者故事分組，以實現每個故事的獨立實作與測試。

## 格式: `[ID] [P?] [Story] 描述`

- **[P]**: 可並行執行 (不同檔案、無相依性)
- **[Story]**: 任務所屬的使用者故事 (例如: US1, US2, US3)
- 描述中包含明確的檔案路徑

## 路徑慣例

此專案為 **單一專案** 結構 (依據 plan.md):
- 原始碼: 根目錄的 `src/`
- 測試: 根目錄的 `tests/`
- 配置: 根目錄的 `config/`
- Docker: 根目錄的 `docker/`

---

## 階段 1: 初始設定 (共用基礎設施)

**目的**: 專案初始化與基本結構建立

- [x] T001 建立專案目錄結構: src/, tests/, config/, docker/
- [x] T002 使用 Poetry 初始化 Python 專案: 建立 pyproject.toml 並指定 Python 3.11+ 需求
- [x] T003 [P] 設定 Poetry 虛擬環境於專案內: poetry config virtualenvs.in-project true
- [x] T004 [P] 新增核心依賴套件至 pyproject.toml: fastapi, uvicorn, pydantic, prometheus-client, structlog
- [x] T005 [P] 新增測試依賴套件至 pyproject.toml: pytest, pytest-cov, pytest-asyncio, httpx
- [x] T006 安裝所有依賴套件: poetry install
- [x] T007 建立 pytest 配置檔 pytest.ini，包含測試探索與覆蓋率設定
- [x] T008 建立 .gitignore 檔案，包含 Python、Poetry 與 IDE 忽略模式

---

## 階段 2: 基礎設施 (阻塞性前置需求)

**目的**: 必須在任何使用者故事實作前完成的核心基礎設施

**⚠️ 關鍵**: 此階段完成前，無法開始任何使用者故事的工作

- [x] T009 建立 Todo Pydantic 模型於 src/models/todo.py: TodoCreate, TodoUpdate, TodoResponse 及驗證規則
- [x] T010 [P] 建立請求 ID 中介軟體於 src/middleware/request_id.py: 產生或提取 X-Request-ID 標頭
- [x] T011 [P] 設定 structlog 於 src/middleware/logging.py: JSON 格式化器、時間戳記、request_id 綁定
- [x] T012 [P] 設定 Prometheus 指標於 src/middleware/metrics.py: http_requests_total 計數器與 http_request_duration_seconds 直方圖
- [x] T013 建立記憶體儲存於 src/storage/memory.py: TodoStore 類別，使用執行緒安全的 dict 與 Lock
- [x] T014 建立 FastAPI 應用程式入口點於 src/main.py: 應用程式初始化與中介軟體註冊
- [x] T015 建立基本測試固件於 tests/conftest.py: FastAPI TestClient 固件與儲存重置固件

**檢查點**: 基礎設施就緒 - 使用者故事實作現在可以並行開始

---

## 階段 3: User Story 1 - 待辦事項基本管理 (Priority: P1) 🎯 MVP

**目標**: 提供完整的待辦事項 CRUD 操作,包括建立、查詢、更新與刪除功能

**獨立測試**: 透過 HTTP 請求 (POST、GET、PUT、DELETE) 驗證待辦事項的完整生命週期操作

### User Story 1 測試 (TDD - 先寫測試) ⚠️

> **憲章要求: 測試先行** - 以下測試必須在實作前撰寫,並驗證測試失敗(紅燈階段)

- [x] T016 [P] [US1] 撰寫 POST /todos 契約測試於 tests/contract/test_todo_api.py: 驗證 201 狀態、回應架構、預設 completed=false
- [x] T017 [P] [US1] 撰寫 GET /todos 契約測試於 tests/contract/test_todo_api.py: 驗證 200 狀態、陣列回應、無待辦事項時回傳空陣列
- [x] T018 [P] [US1] 撰寫 GET /todos/{id} 契約測試於 tests/contract/test_todo_api.py: 驗證 200 狀態、單一待辦事項回應、不存在時回傳 404
- [x] T019 [P] [US1] 撰寫 PUT /todos/{id} 契約測試於 tests/contract/test_todo_api.py: 驗證 200 狀態、更新後回應、不存在時回傳 404
- [x] T020 [P] [US1] 撰寫 DELETE /todos/{id} 契約測試於 tests/contract/test_todo_api.py: 驗證 204 狀態、不存在時回傳 404
- [x] T021 [P] [US1] 撰寫完整待辦事項生命週期整合測試於 tests/integration/test_todo_lifecycle.py: 建立 → 讀取 → 更新 → 刪除流程
- [x] T022 [P] [US1] 撰寫 TodoStore 單元測試於 tests/unit/test_storage.py: create, get, list_all, update, delete 方法
- [x] T023 [P] [US1] 撰寫 Todo 模型單元測試於 tests/unit/test_models.py: 驗證規則 (標題必填、最小/最大長度、空字串)

**TDD 檢查點**: 執行 pytest - 所有測試應該失敗 (紅燈)。這證明測試是有效的。

### User Story 1 實作

- [x] T024 [US1] 實作 TodoStore.create() 於 src/storage/memory.py: 執行緒安全的 ID 產生與儲存
- [x] T025 [US1] 實作 TodoStore.get() 於 src/storage/memory.py: 透過 ID 取得待辦事項，具備執行緒安全
- [x] T026 [US1] 實作 TodoStore.list_all() 於 src/storage/memory.py: 回傳所有待辦事項，具備執行緒安全
- [x] T027 [US1] 實作 TodoStore.update() 於 src/storage/memory.py: 更新現有待辦事項，具備執行緒安全
- [x] T028 [US1] 實作 TodoStore.delete() 於 src/storage/memory.py: 移除待辦事項，具備執行緒安全
- [x] T029 建立待辦事項 API 路由器於 src/api/todos.py: 初始化 APIRouter 並指定 /todos 前綴
- [x] T030 [US1] 實作 POST /todos 端點於 src/api/todos.py: 驗證 TodoCreate、呼叫儲存、回傳 201 與 TodoResponse
- [x] T031 [US1] 實作 GET /todos 端點於 src/api/todos.py: 取得所有待辦事項、回傳 200 與陣列
- [x] T032 [US1] 實作 GET /todos/{id} 端點於 src/api/todos.py: 取得單一待辦事項、回傳 200 或 404
- [x] T033 [US1] 實作 PUT /todos/{id} 端點於 src/api/todos.py: 更新待辦事項、回傳 200 或 404
- [x] T034 [US1] 實作 DELETE /todos/{id} 端點於 src/api/todos.py: 刪除待辦事項、回傳 204 或 404
- [x] T035 [US1] 註冊待辦事項路由器於 src/main.py: app.include_router(todos.router)
- [x] T036 [US1] 新增待辦事項端點錯誤處理於 src/api/todos.py: 針對 400、404、500 使用 HTTPException
- [x] T037 [US1] 驗證 Pydantic 驗證錯誤於 src/api/todos.py: 確保無效輸入回傳友善的錯誤訊息

**TDD 檢查點**: 執行 pytest - 所有 User Story 1 測試應該通過 (綠燈)。測試覆蓋率應 >85%。

**User Story 1 驗證**: 此時您應該能夠執行 quickstart.md 步驟 4 的指令 (建立、查詢、更新、刪除待辦事項) 並驗證 CRUD 操作正確運作。

---

## 階段 4: User Story 2 - 請求追蹤與日誌記錄 (Priority: P1)

**目標**: 為每個 API 請求提供完整的追蹤與結構化日誌記錄能力

**獨立測試**: 發送任意 API 請求後,檢查日誌輸出是否包含 request_id、method、path、status_code、latency_ms 等必要資訊

### User Story 2 測試 (TDD - 先寫測試) ⚠️

> **憲章要求: 測試先行** - 以下測試必須在實作前撰寫,並驗證測試失敗(紅燈階段)

- [ ] T038 [P] [US2] 撰寫 X-Request-ID 標頭契約測試於 tests/contract/test_request_id.py: 驗證回應包含 X-Request-ID 標頭
- [ ] T039 [P] [US2] 撰寫自訂 request_id 契約測試於 tests/contract/test_request_id.py: 送出自訂 X-Request-ID，驗證回傳相同 ID
- [ ] T040 [P] [US2] 撰寫自動產生 request_id 契約測試於 tests/contract/test_request_id.py: 不送出 X-Request-ID，驗證回傳 UUID 格式
- [ ] T041 [P] [US2] 撰寫日誌記錄整合測試於 tests/integration/test_logging_integration.py: 擷取標準輸出，驗證 JSON 日誌格式包含所有必要欄位
- [ ] T042 [P] [US2] 撰寫 request_id 追蹤整合測試於 tests/integration/test_logging_integration.py: 驗證 request_id 同時出現於日誌與回應中

**TDD 檢查點**: 執行 pytest - 所有 US2 測試應該失敗 (紅燈)。

### User Story 2 實作

- [ ] T043 [US2] 實作請求 ID 產生於 src/middleware/request_id.py: 從標頭提取或產生 UUID v4
- [ ] T044 [US2] 實作請求 ID 回應標頭於 src/middleware/request_id.py: 新增 X-Request-ID 至回應標頭
- [ ] T045 [US2] 綁定 request_id 至請求狀態於 src/middleware/request_id.py: request.state.request_id 供處理器存取
- [ ] T046 [US2] 設定 structlog 處理器於 src/middleware/logging.py: add_log_level、TimeStamper(fmt="iso")、JSONRenderer
- [ ] T047 [US2] 實作日誌中介軟體於 src/middleware/logging.py: 記錄請求開始、完成、錯誤及所有必要欄位
- [ ] T048 [US2] 綁定 request_id 至 structlog 上下文於 src/middleware/logging.py: 自動在所有日誌中包含 request_id
- [ ] T049 [US2] 註冊 request_id 中介軟體於 src/main.py: 新增至中介軟體堆疊 (在路由之前)
- [ ] T050 [US2] 註冊日誌中介軟體於 src/main.py: 新增至中介軟體堆疊 (在 request_id 之後)
- [ ] T051 [US2] 新增錯誤日誌記錄於 src/middleware/logging.py: 捕捉例外、以錯誤層級記錄、包含堆疊追蹤
- [ ] T052 [US2] 驗證日誌輸出格式於 src/middleware/logging.py: 確保 JSON 格式包含 event、request_id、timestamp、method、path、status_code、latency_ms

**TDD 檢查點**: 執行 pytest - 所有 User Story 2 測試應該通過 (綠燈)。

**User Story 2 驗證**: 此時您應該能夠執行 quickstart.md 步驟 5 的指令 (檢查可觀測性功能) 並驗證結構化日誌出現且包含 request_id 追蹤。

---

## 階段 5: User Story 3 - 系統健康檢查與指標暴露 (Priority: P2)

**目標**: 提供健康檢查端點與 Prometheus 格式的系統指標,支援外部監控系統

**獨立測試**: 存取 /health 端點驗證服務狀態,存取 /metrics 端點驗證 Prometheus 指標格式

### User Story 3 測試 (TDD - 先寫測試) ⚠️

> **憲章要求: 測試先行** - 以下測試必須在實作前撰寫,並驗證測試失敗(紅燈階段)

- [ ] T053 [P] [US3] 撰寫 GET /health 契約測試於 tests/contract/test_health_api.py: 驗證 200 狀態、status="healthy"、timestamp 欄位
- [ ] T054 [P] [US3] 撰寫 GET /metrics 契約測試於 tests/contract/test_metrics_api.py: 驗證 200 狀態、text/plain 內容類型、Prometheus 格式
- [ ] T055 [P] [US3] 撰寫指標收集整合測試於 tests/integration/test_metrics_integration.py: 發送請求，驗證計數器遞增
- [ ] T056 [P] [US3] 撰寫直方圖桶整合測試於 tests/integration/test_metrics_integration.py: 驗證延遲直方圖記錄請求
- [ ] T057 [P] [US3] 撰寫低基數標籤整合測試於 tests/integration/test_metrics_integration.py: 驗證標籤中不包含 request_id 或 user_id

**TDD 檢查點**: 執行 pytest - 所有 US3 測試應該失敗 (紅燈)。

### User Story 3 實作

- [ ] T058 [P] [US3] 建立健康檢查路由器於 src/api/health.py: 實作 GET /health 端點回傳狀態與時間戳記
- [ ] T059 [P] [US3] 建立指標端點於 src/api/metrics.py: 透過 GET /metrics 暴露 Prometheus 指標
- [ ] T060 [US3] 初始化 Prometheus 計數器於 src/middleware/metrics.py: http_requests_total 帶標籤 (method, path, status)
- [ ] T061 [US3] 初始化 Prometheus 直方圖於 src/middleware/metrics.py: http_request_duration_seconds 帶標籤 (method, path) 與自訂桶
- [ ] T062 [US3] 實作指標中介軟體於 src/middleware/metrics.py: 記錄每個請求的計數與延遲
- [ ] T063 [US3] 設定直方圖桶於 src/middleware/metrics.py: (0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0)
- [ ] T064 [US3] 正規化路徑標籤於 src/middleware/metrics.py: 將 {id} 替換為佔位符以避免高基數
- [ ] T065 [US3] 註冊健康檢查路由器於 src/main.py: app.include_router(health.router)
- [ ] T066 [US3] 註冊指標路由器於 src/main.py: app.include_router(metrics.router)
- [ ] T067 [US3] 註冊指標中介軟體於 src/main.py: 新增至中介軟體堆疊

**TDD 檢查點**: 執行 pytest - 所有 User Story 3 測試應該通過 (綠燈)。

**User Story 3 驗證**: 此時您應該能夠執行 quickstart.md 步驟 5.3 的指令 (查看 Prometheus 指標) 並驗證指標端點回傳正確的 Prometheus 格式。

---

## 階段 6: 優化與跨領域關注點

**目的**: 影響多個使用者故事的改進與最終驗證

- [ ] T068 [P] 新增 API 文件於 src/main.py: 從 contracts/openapi.yaml 設定 OpenAPI 標題、描述、版本
- [ ] T069 [P] 設定 CORS (如需要) 於 src/main.py: 為本機開發新增 CORSMiddleware
- [ ] T070 建立 Dockerfile 於 docker/Dockerfile: 使用 Poetry 的多階段建置，暴露 8000 埠
- [ ] T071 建立 docker-compose.yml 於 docker/docker-compose.yml: API 服務 + Prometheus + Grafana 設定
- [ ] T072 建立 Prometheus 配置於 docker/prometheus.yml: API /metrics 端點的抓取配置
- [ ] T073 [P] 更新 README.md: 新增專案概覽、快速開始參考、技術堆疊
- [ ] T074 執行完整測試套件: pytest --cov=src --cov-report=html --cov-report=term
- [ ] T075 驗證測試覆蓋率 >85%: 檢查覆蓋率報告，如需要則新增測試
- [ ] T076 執行 quickstart.md 驗證: 執行 quickstart.md 中的所有步驟並驗證預期結果
- [ ] T077 驗證所有驗收情境: 驗證 spec.md User Stories 1-3 的所有情境
- [ ] T078 效能驗證: 驗證 CRUD 操作的 p95 延遲 <100ms (SC-001)
- [ ] T079 效能驗證: 驗證健康檢查的 p99 <10ms (SC-005)
- [ ] T080 安全驗證: 驗證日誌不包含敏感資訊 (SC-007)
- [ ] T081 [P] 程式碼清理與格式化: 對所有 Python 檔案執行 black/ruff 格式化器
- [ ] T082 最終整合測試: 使用 docker-compose 啟動伺服器，執行 quickstart.md 中的所有 curl 指令

---

## 相依性與執行順序

### 階段相依性

- **初始設定 (階段 1)**: 無相依性 - 可立即開始
- **基礎設施 (階段 2)**: 相依於初始設定 (階段 1) 完成 - 阻塞所有使用者故事
- **使用者故事 (階段 3-5)**: 全部相依於基礎設施 (階段 2) 完成
  - User Story 1 (P1): 待辦事項基本管理 - 不相依於其他故事
  - User Story 2 (P1): 請求追蹤與日誌記錄 - 不相依於其他故事 (可與 US1 並行)
  - User Story 3 (P2): 系統健康檢查與指標暴露 - 不相依於其他故事 (可與 US1/US2 並行)
- **優化 (階段 6)**: 相依於所有使用者故事 (階段 3-5) 完成

### 使用者故事相依性

- **User Story 1 (P1)**: 基礎設施 (階段 2) 完成後可開始 - 可獨立測試
- **User Story 2 (P1)**: 基礎設施 (階段 2) 完成後可開始 - 可獨立測試
- **User Story 3 (P2)**: 基礎設施 (階段 2) 完成後可開始 - 可獨立測試

**重要**: 所有三個 User Stories 都是獨立的,完成基礎設施階段後可以並行開發

### 每個使用者故事內部

- **TDD 原則**: 測試必須先撰寫並失敗後才實作
- 模型 → 服務 → 端點
- 契約測試在實作之前
- 整合測試驗證端到端流程
- 單元測試驗證隔離元件
- 所有測試通過後才視為故事完成

### 並行機會

#### 初始設定階段 (階段 1)
- T003, T004, T005, T007 可並行 (不同檔案)

#### 基礎設施階段 (階段 2)
- T010, T011, T012 可並行 (不同檔案)

#### User Story 1 測試 (階段 3)
- T016, T017, T018, T019, T020, T021, T022, T023 可並行 (不同測試檔案)

#### User Story 2 測試 (階段 4)
- T038, T039, T040, T041, T042 可並行 (不同測試檔案)

#### User Story 3 測試 (階段 5)
- T053, T054, T055, T056, T057 可並行 (不同測試檔案)
- T058, T059 可並行 (不同 API 檔案)

#### 優化階段 (階段 6)
- T068, T069, T072, T073, T081 可並行 (不同檔案或獨立任務)

#### 跨故事並行化
- **完成階段 2 後**: User Story 1, 2, 3 可由不同開發者並行開發

---

## 並行範例: User Story 1

```bash
# 1. 一起啟動 User Story 1 的所有測試檔案 (TDD - 紅燈階段):
Task T016: "撰寫 POST /todos 契約測試於 tests/contract/test_todo_api.py"
Task T017: "撰寫 GET /todos 契約測試於 tests/contract/test_todo_api.py"
Task T018: "撰寫 GET /todos/{id} 契約測試於 tests/contract/test_todo_api.py"
Task T019: "撰寫 PUT /todos/{id} 契約測試於 tests/contract/test_todo_api.py"
Task T020: "撰寫 DELETE /todos/{id} 契約測試於 tests/contract/test_todo_api.py"
Task T021: "撰寫完整待辦事項生命週期整合測試於 tests/integration/test_todo_lifecycle.py"
Task T022: "撰寫 TodoStore 單元測試於 tests/unit/test_storage.py"
Task T023: "撰寫 Todo 模型單元測試於 tests/unit/test_models.py"

# 2. 驗證測試失敗 (紅燈)
執行: pytest

# 3. 實作儲存方法 (可循序執行，因為同一檔案)
Task T024-T028: TodoStore 實作於 src/storage/memory.py

# 4. 實作 API 端點 (必須循序執行，因為同一檔案)
Task T030-T034: Todos API 端點於 src/api/todos.py

# 5. 驗證測試通過 (綠燈)
執行: pytest --cov=src/api/todos.py --cov=src/storage/memory.py
```

---

## 實作策略

### MVP 優先 (僅 User Story 1 - 最快展示路徑)

1. **完成階段 1**: 初始設定 (T001-T008) - ~30 分鐘
2. **完成階段 2**: 基礎設施 (T009-T015) - ~1 小時
3. **完成階段 3**: User Story 1 (T016-T037) - ~2-3 小時
4. **停下來驗證**:
   - 執行 pytest - 所有測試應該通過
   - 啟動伺服器: `uvicorn src.main:app --reload`
   - 使用 quickstart.md 中的 curl 指令測試 CRUD 操作
   - 驗證測試覆蓋率 >85%
5. **MVP 就緒**: 您現在擁有具備基本 CRUD 操作的可運作 TODO API

**MVP 總時間**: ~4-5 小時

### 完整功能交付 (所有使用者故事)

1. **階段 1**: 初始設定 (T001-T008) - ~30 分鐘
2. **階段 2**: 基礎設施 (T009-T015) - ~1 小時
3. **階段 3**: User Story 1 - 待辦事項基本管理 (T016-T037) - ~2-3 小時
   - **檢查點**: 獨立測試 CRUD
4. **階段 4**: User Story 2 - 請求追蹤與日誌記錄 (T038-T052) - ~1-2 小時
   - **檢查點**: 獨立測試日誌與 request_id 追蹤
5. **階段 5**: User Story 3 - 系統健康檢查與指標暴露 (T053-T067) - ~1-2 小時
   - **檢查點**: 獨立測試健康與指標端點
6. **階段 6**: 優化與驗證 (T068-T082) - ~1-2 小時
   - Docker 設定、文件、完整驗證
7. **最終驗證**: 執行完整的 quickstart.md 指南

**完整功能總時間**: ~8-12 小時

### 漸進式交付 (建議)

1. **里程碑 1 (MVP)**: 初始設定 + 基礎設施 + US1 → 展示 CRUD API
2. **里程碑 2**: 新增 US2 → 展示可觀測性 (日誌、請求追蹤)
3. **里程碑 3**: 新增 US3 → 展示監控 (健康檢查、指標)
4. **里程碑 4**: 優化 + Docker → 可生產部署的展示

每個里程碑都可獨立部署與展示。

### 並行團隊策略

基礎設施階段完成後，由 3 位開發者分工:

- **開發者 A**: User Story 1 (T016-T037) - CRUD 操作
- **開發者 B**: User Story 2 (T038-T052) - 日誌與請求追蹤
- **開發者 C**: User Story 3 (T053-T067) - 健康檢查與指標

所有故事獨立整合。個別驗證後，整合在一起進行最終測試。

**團隊完成時間**: ~3-4 小時 (基礎設施後) + 1-2 小時 (優化)

---

## 總結

- **總任務數**: 82
- **User Story 1** (待辦事項基本管理): 22 個任務 (T016-T037)
- **User Story 2** (請求追蹤與日誌記錄): 15 個任務 (T038-T052)
- **User Story 3** (系統健康檢查與指標暴露): 15 個任務 (T053-T067)
- **初始設定 + 基礎設施**: 15 個任務 (T001-T015)
- **優化與驗證**: 15 個任務 (T068-T082)

**並行機會**:
- 17 個標記 [P] 的任務可並行執行
- 基礎設施階段完成後，3 個使用者故事可並行開發
- 每個故事內的測試檔案都可並行撰寫

**獨立測試條件達成**:
- ✅ User Story 1: CRUD 操作可透過 HTTP 請求測試
- ✅ User Story 2: 日誌可透過標準輸出擷取與標頭驗證測試
- ✅ User Story 3: 健康檢查/指標可透過專用端點測試

**MVP 範圍**: 階段 1 + 階段 2 + 階段 3 (僅 User Story 1) = ~4-5 小時

**測試先行合規性**: 所有 3 個使用者故事都包含在實作任務之前的測試任務，遵循憲章的 TDD 原則

---

## 注意事項

- **[P]** = 可並行任務 (不同檔案、無相依性)
- **[Story]** = 任務所屬的使用者故事 (US1, US2, US3)
- **TDD 原則**: 所有測試必須在實作前撰寫並失敗,證明測試有效
- 每個使用者故事都可獨立完成與測試
- 在每個檢查點停下來驗證測試通過
- 遵循憲章「測試先行」原則:紅燈(測試失敗) → 綠燈(實作通過) → 重構
- 避免: 模糊任務、同一檔案衝突、破壞獨立性的跨故事依賴
- 參考 quickstart.md 中的驗收步驟來驗證每個使用者故事
