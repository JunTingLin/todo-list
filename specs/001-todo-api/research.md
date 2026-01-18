# Research: 具備可觀測性的 TODO API 服務

**Date**: 2026-01-18
**Feature**: 001-todo-api
**Purpose**: 技術決策研究與最佳實踐調查

## Research Questions

本階段研究以下技術決策點，確保實作選擇符合專案需求與業界最佳實踐：

1. 為何選擇 FastAPI 作為 Web 框架？
2. 如何實作結構化日誌以支援可觀測性？
3. Prometheus 指標最佳實踐（避免高基數標籤）
4. FastAPI 中介層（Middleware）實作 request_id 追蹤
5. 記憶體儲存的資料結構選擇
6. 測試策略：契約測試 vs 整合測試 vs 單元測試

---

## Decision 1: Web Framework - FastAPI

### 選擇：FastAPI 0.100+

### 理由：

1. **原生異步支援（Async/Await）**
   - 基於 Starlette ASGI 框架
   - 高效能處理並發請求（滿足 SC-001: p95 < 100ms）
   - 原生支援 async def 路由處理器

2. **自動 API 文件生成**
   - 自動產生 OpenAPI 3.0 規格（符合憲章契約測試要求）
   - Swagger UI 與 ReDoc 互動式文件
   - 減少手動維護 API 契約的負擔

3. **Pydantic 整合**
   - 資料驗證與序列化
   - 類型安全（Python 3.11+ type hints）
   - 自動錯誤訊息生成（符合 FR-015 友善錯誤訊息）

4. **中介層生態系統**
   - 易於實作 request_id 追蹤中介層
   - 支援結構化日誌整合
   - Prometheus metrics 中介層

5. **測試友善**
   - FastAPI TestClient 基於 Starlette TestClient
   - 完整的異步測試支援
   - 易於編寫契約測試與整合測試

### 替代方案：

| 框架 | 優勢 | 為何未選擇 |
|------|------|-----------|
| Flask | 簡單、成熟生態系 | 同步框架，效能較低；缺少自動 API 文件 |
| Django REST Framework | 完整功能、Admin 介面 | 過於龐大，不符合 YAGNI 原則；學習曲線陡峭 |
| Starlette | 輕量、高效能 | 過於底層，需手動實作許多功能（如資料驗證） |

### 參考資料：
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [FastAPI Performance Benchmarks](https://www.techempower.com/benchmarks/)

---

## Decision 2: 結構化日誌 - Structlog

### 選擇：structlog + Python logging

### 理由：

1. **結構化 JSON 輸出**
   - 原生支援 JSON 格式日誌（符合 FR-012）
   - 易於機器解析與分析
   - 支援任意上下文欄位（request_id、timestamp、latency 等）

2. **上下文綁定（Context Binding）**
   ```python
   log = log.bind(request_id=req_id, user_id=user_id)
   log.info("processing request")  # 自動包含 request_id
   ```
   - 請求級別上下文自動傳遞
   - 避免重複程式碼

3. **處理器鏈（Processor Chain）**
   - 自動添加 timestamp
   - 自動添加日誌等級
   - 自訂處理器格式化輸出

4. **與 FastAPI 整合**
   - 中介層輕鬆整合
   - 異常自動記錄
   - 效能開銷低

### 最佳實踐：

```python
import structlog

# 設定
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

# 使用
log = structlog.get_logger()
log.info("request processed",
         request_id="abc-123",
         method="GET",
         path="/todos",
         status_code=200,
         latency_ms=45.2)
```

### 輸出範例：

```json
{
  "event": "request processed",
  "request_id": "abc-123",
  "method": "GET",
  "path": "/todos",
  "status_code": 200,
  "latency_ms": 45.2,
  "timestamp": "2026-01-18T10:30:45.123456Z",
  "level": "info"
}
```

### 替代方案：

| 方案 | 為何未選擇 |
|------|-----------|
| Python logging (pure) | 結構化支援較弱，需大量自定義 |
| loguru | 較新但生態系統較小，企業採用度較低 |
| JSON logging handlers | 功能有限，缺少上下文綁定特性 |

---

## Decision 3: Prometheus 指標最佳實踐

### 選擇：prometheus-client + 標準指標類型

### 理由：

1. **符合 Prometheus 標準**
   - 使用標準指標類型：Counter、Histogram、Gauge、Summary
   - 遵循 Prometheus 命名慣例
   - 自動 /metrics 端點暴露

2. **避免高基數標籤（Critical）**
   - ❌ 不使用：request_id、user_id、timestamp 作為標籤
   - ✅ 使用：method、path、status_code 作為標籤
   - 符合 FR-020 要求

3. **建議指標設計**：

```python
from prometheus_client import Counter, Histogram

# 請求計數器（符合 FR-018）
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'path', 'status']  # 低基數標籤
)

# 延遲直方圖（符合 FR-019）
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'path'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0)
)
```

### 標籤基數分析：

| 標籤 | 基數 | 是否使用 | 理由 |
|------|------|---------|------|
| method | ~5 | ✅ Yes | HTTP 方法有限（GET、POST、PUT、DELETE 等） |
| path | ~10 | ✅ Yes | API 端點有限（/todos、/todos/{id}、/health、/metrics） |
| status | ~10 | ✅ Yes | HTTP 狀態碼分類有限（2xx、4xx、5xx） |
| request_id | ∞ | ❌ No | 每個請求唯一，導致無限基數 |
| user_id | ∞ | ❌ No | 使用者數量不受限 |

### Bucket 設計（延遲直方圖）：

根據 SC-001（p95 < 100ms）設計 bucket：
- 0.005s (5ms) - 極快回應
- 0.01s (10ms) - 健康檢查目標（SC-005: p99 < 10ms）
- 0.025s (25ms) - 快速回應
- 0.05s (50ms) - 良好回應
- 0.1s (100ms) - p95 目標閾值
- 0.25s、0.5s、1.0s - 較慢回應追蹤

### 參考資料：
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [High Cardinality Issues](https://www.robustperception.io/cardinality-is-key)

---

## Decision 4: Request ID 追蹤實作

### 選擇：FastAPI Middleware + UUID

### 理由：

1. **中介層模式**
   - 統一處理所有請求
   - 自動注入 request_id
   - 傳遞至日誌上下文

2. **UUID v4 格式**
   - 全球唯一性保證
   - 符合 FR-010 要求
   - 易於生成（標準庫 uuid.uuid4()）

3. **實作策略**：

```python
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import uuid
import structlog

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 從標頭讀取或自動產生（FR-009、FR-010）
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        # 綁定至請求狀態
        request.state.request_id = request_id

        # 綁定至日誌上下文
        log = structlog.get_logger().bind(request_id=request_id)
        request.state.log = log

        # 處理請求
        response = await call_next(request)

        # 回傳標頭（FR-011）
        response.headers["X-Request-ID"] = request_id

        return response
```

### 流程：

1. 請求進入 → 檢查 X-Request-ID 標頭
2. 有值 → 使用該值（符合 FR-009）
3. 無值 → 自動產生 UUID（符合 FR-010）
4. 綁定至 request.state 與日誌上下文
5. 回應時添加 X-Request-ID 標頭（符合 FR-011）

---

## Decision 5: 記憶體儲存設計

### 選擇：Python dict + threading.Lock

### 理由：

1. **簡單高效**
   - 符合 YAGNI 原則（FR-007: 記憶體儲存）
   - 無需外部依賴（符合 FR-023）
   - O(1) 查詢效能

2. **執行緒安全**
   - FastAPI 使用執行緒池處理同步路由
   - threading.Lock 保證資料一致性
   - 避免競爭條件（race condition）

3. **實作設計**：

```python
from threading import Lock
from typing import Dict, Optional
from models.todo import Todo

class TodoStore:
    def __init__(self):
        self._todos: Dict[str, Todo] = {}
        self._lock = Lock()
        self._counter = 0

    def create(self, todo: Todo) -> Todo:
        with self._lock:
            self._counter += 1
            todo.id = str(self._counter)
            self._todos[todo.id] = todo
            return todo

    def get(self, todo_id: str) -> Optional[Todo]:
        with self._lock:
            return self._todos.get(todo_id)

    def list_all(self) -> List[Todo]:
        with self._lock:
            return list(self._todos.values())

    def update(self, todo_id: str, todo: Todo) -> Optional[Todo]:
        with self._lock:
            if todo_id in self._todos:
                self._todos[todo_id] = todo
                return todo
            return None

    def delete(self, todo_id: str) -> bool:
        with self._lock:
            return self._todos.pop(todo_id, None) is not None
```

### ID 生成策略：

選擇**遞增整數**（轉字串）而非 UUID：
- ✅ 簡單易讀（測試友善）
- ✅ 順序性（便於測試驗證）
- ✅ 符合展示目的（非生產環境）
- ❌ 不適合分散式環境（但本專案單一實例）

### 替代方案：

| 方案 | 為何未選擇 |
|------|-----------|
| SQLite | 引入外部依賴，過度複雜 |
| Redis | 需要外部服務，違反 FR-023 |
| 單純 list | 查詢效能 O(n)，不適合 |

---

## Decision 6: 測試策略

### 選擇：三層測試金字塔

### 理由：

1. **契約測試（Contract Tests）**
   - **目的**：驗證 API 契約（輸入/輸出格式）
   - **工具**：FastAPI TestClient
   - **範圍**：每個 API 端點
   - **符合**：憲章契約測試要求

```python
def test_create_todo_contract():
    response = client.post("/todos", json={"title": "Test"})
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert "title" in data
    assert "completed" in data
    assert data["title"] == "Test"
    assert data["completed"] == False
```

2. **整合測試（Integration Tests）**
   - **目的**：驗證完整使用者流程
   - **工具**：FastAPI TestClient + 實際元件
   - **範圍**：使用者故事驗收情境
   - **符合**：憲章整合測試要求

```python
def test_todo_full_lifecycle():
    # Create
    response = client.post("/todos", json={"title": "Buy milk"})
    todo_id = response.json()["id"]

    # Read
    response = client.get(f"/todos/{todo_id}")
    assert response.json()["title"] == "Buy milk"

    # Update
    client.put(f"/todos/{todo_id}", json={"completed": True})

    # Verify
    response = client.get(f"/todos/{todo_id}")
    assert response.json()["completed"] == True

    # Delete
    client.delete(f"/todos/{todo_id}")
    response = client.get(f"/todos/{todo_id}")
    assert response.status_code == 404
```

3. **單元測試（Unit Tests）**
   - **目的**：測試單一函式/類別
   - **工具**：Pytest
   - **範圍**：模型驗證、儲存層邏輯
   - **目標**：關鍵邏輯覆蓋率 > 80%

```python
def test_todo_model_validation():
    # Valid todo
    todo = Todo(title="Test", completed=False)
    assert todo.title == "Test"

    # Invalid todo (missing title)
    with pytest.raises(ValidationError):
        Todo(completed=False)
```

### 測試組織：

```
tests/
├── contract/       # 35+ API 契約測試
├── integration/    # 15+ 整合測試
└── unit/           # 20+ 單元測試
```

### 測試覆蓋率目標：

- **契約測試**：100% API 端點覆蓋
- **整合測試**：100% 使用者故事覆蓋
- **單元測試**：80%+ 業務邏輯覆蓋
- **整體覆蓋率**：85%+

### 參考資料：
- [Testing FastAPI](https://fastapi.tiangolo.com/tutorial/testing/)
- [Pytest Documentation](https://docs.pytest.org/)

---

## Summary

### 技術決策總結表

| 決策領域 | 選擇 | 主要理由 |
|---------|------|---------|
| Web Framework | FastAPI 0.100+ | 高效能、自動 API 文件、Pydantic 整合 |
| 結構化日誌 | structlog | 原生 JSON 支援、上下文綁定、處理器鏈 |
| 指標系統 | prometheus-client | Prometheus 標準、低基數標籤設計 |
| Request ID | Middleware + UUID v4 | 統一處理、全球唯一性 |
| 儲存層 | dict + Lock | 簡單高效、執行緒安全 |
| 測試策略 | 三層金字塔 | 契約 + 整合 + 單元完整覆蓋 |

### 風險與緩解

| 風險 | 緩解措施 |
|------|---------|
| 記憶體儲存資料遺失 | 明確文件說明（Out of Scope），僅限展示用途 |
| 執行緒鎖效能瓶頸 | 小規模資料量，影響可忽略；生產環境改用資料庫 |
| 無驗證機制安全性 | Out of Scope 明確排除，僅限本地 demo |

### 下一步

所有技術決策已明確，可進入 Phase 1：
1. 定義資料模型（data-model.md）
2. 生成 API 契約（contracts/openapi.yaml）
3. 撰寫快速開始指南（quickstart.md）
