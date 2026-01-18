# Data Model: 具備可觀測性的 TODO API 服務

**Date**: 2026-01-18
**Feature**: 001-todo-api
**Purpose**: 定義系統資料模型、實體關係與驗證規則

## Overview

本系統包含三個核心實體：
1. **Todo（待辦事項）**：使用者管理的待辦任務
2. **RequestLog（請求日誌）**：API 請求追蹤記錄（非持久化，僅日誌輸出）
3. **Metrics（指標）**：系統效能與健康指標（Prometheus 格式）

所有資料儲存於記憶體中，無需資料庫 schema 設計。

---

## Entity 1: Todo（待辦事項）

### Purpose

代表使用者的單一待辦事項任務。

### Attributes

| 欄位 | 類型 | 必填 | 預設值 | 說明 |
|------|------|------|--------|------|
| `id` | string | 是 | 自動生成 | 唯一識別碼（遞增整數轉字串） |
| `title` | string | 是 | - | 待辦事項標題，長度 1-200 字元 |
| `completed` | boolean | 否 | false | 完成狀態（true=已完成，false=未完成） |

### Pydantic Model Definition

```python
from pydantic import BaseModel, Field, field_validator

class TodoCreate(BaseModel):
    """建立待辦事項的請求模型"""
    title: str = Field(..., min_length=1, max_length=200, description="待辦事項標題")
    completed: bool = Field(default=False, description="完成狀態")

    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('標題不得為空白字串')
        return v.strip()

class TodoUpdate(BaseModel):
    """更新待辦事項的請求模型"""
    title: str | None = Field(None, min_length=1, max_length=200)
    completed: bool | None = None

    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError('標題不得為空白字串')
        return v.strip() if v else None

class TodoResponse(BaseModel):
    """待辦事項回應模型"""
    id: str = Field(..., description="唯一識別碼")
    title: str = Field(..., description="待辦事項標題")
    completed: bool = Field(..., description="完成狀態")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "1",
                "title": "購買牛奶",
                "completed": False
            }
        }
    }
```

### Validation Rules

| 規則 | 說明 | 錯誤回應 |
|------|------|---------|
| **VR-001** | title 必填 | 400 Bad Request: "標題為必填欄位" |
| **VR-002** | title 長度 1-200 字元 | 400 Bad Request: "標題長度必須在 1 到 200 字元之間" |
| **VR-003** | title 不得為空白字串 | 400 Bad Request: "標題不得為空白字串" |
| **VR-004** | completed 必須為布林值 | 400 Bad Request: "completed 必須為 true 或 false" |
| **VR-005** | id 為唯一值 | 系統自動保證（儲存層負責） |

### State Transitions

```
[建立] → completed: false (未完成)
         ↓
     [更新 completed]
         ↓
    completed: true (已完成)
         ↓
     [更新 completed]
         ↓
    completed: false (標記為未完成)
```

**狀態說明**：
- 新建立的待辦事項預設為 `completed: false`
- 可隨時切換 `completed` 狀態（true ↔ false）
- 無其他狀態約束或生命週期限制

### Business Rules

| 規則 | 說明 |
|------|------|
| **BR-001** | 刪除待辦事項後無法復原（記憶體儲存，無軟刪除） |
| **BR-002** | 同一時間可存在多個相同 title 的待辦事項（無唯一性限制） |
| **BR-003** | 更新時只能修改 title 和 completed，id 不可變更 |

---

## Entity 2: RequestLog（請求日誌）

### Purpose

記錄每一次 API 請求的追蹤資訊，用於可觀測性與除錯。

**注意**：此實體僅作為日誌輸出，不儲存於記憶體或資料庫。

### Attributes

| 欄位 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `request_id` | string (UUID) | 是 | 請求唯一識別碼 |
| `timestamp` | string (ISO 8601) | 是 | 請求時間戳記 |
| `method` | string | 是 | HTTP 方法（GET, POST, PUT, DELETE） |
| `path` | string | 是 | API 路徑（如 /todos, /todos/1） |
| `status_code` | integer | 是 | HTTP 回應狀態碼（200, 201, 400, 404, 500） |
| `latency_ms` | float | 是 | 請求處理時間（毫秒） |
| `error` | string | 否 | 錯誤訊息（僅在錯誤情況） |
| `level` | string | 是 | 日誌等級（info, warning, error） |

### JSON Log Format

```json
{
  "event": "request_processed",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-01-18T10:30:45.123456Z",
  "method": "POST",
  "path": "/todos",
  "status_code": 201,
  "latency_ms": 12.34,
  "level": "info"
}
```

**錯誤情境範例**：

```json
{
  "event": "request_error",
  "request_id": "550e8400-e29b-41d4-a716-446655440001",
  "timestamp": "2026-01-18T10:31:00.000000Z",
  "method": "GET",
  "path": "/todos/999",
  "status_code": 404,
  "latency_ms": 5.67,
  "error": "Todo not found",
  "level": "warning"
}
```

### Validation Rules

| 規則 | 說明 |
|------|------|
| **VR-LOG-001** | request_id 必須為有效 UUID v4 格式 |
| **VR-LOG-002** | timestamp 必須為 ISO 8601 格式 |
| **VR-LOG-003** | latency_ms 必須為非負數 |
| **VR-LOG-004** | status_code 必須為有效 HTTP 狀態碼（100-599） |
| **VR-LOG-005** | 日誌不得包含敏感資訊（密碼、token 等） |

---

## Entity 3: Metrics（指標）

### Purpose

暴露系統效能指標供 Prometheus 抓取。

**注意**：此實體為 Prometheus 格式指標，非資料庫實體。

### Metrics Definition

#### 1. HTTP Requests Total (Counter)

**名稱**: `http_requests_total`
**類型**: Counter
**說明**: HTTP 請求總次數
**標籤**:
- `method`: HTTP 方法（GET, POST, PUT, DELETE）
- `path`: API 端點（/todos, /todos/{id}, /health, /metrics）
- `status`: 狀態碼（2xx, 4xx, 5xx）

**範例輸出**:
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",path="/todos",status="2xx"} 1234
http_requests_total{method="POST",path="/todos",status="2xx"} 567
http_requests_total{method="GET",path="/todos/{id}",status="4xx"} 45
```

#### 2. HTTP Request Duration (Histogram)

**名稱**: `http_request_duration_seconds`
**類型**: Histogram
**說明**: HTTP 請求延遲分布
**標籤**:
- `method`: HTTP 方法
- `path`: API 端點
**Buckets**: 0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0

**範例輸出**:
```
# HELP http_request_duration_seconds HTTP request latency
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{method="GET",path="/todos",le="0.005"} 100
http_request_duration_seconds_bucket{method="GET",path="/todos",le="0.01"} 450
http_request_duration_seconds_bucket{method="GET",path="/todos",le="0.1"} 1200
http_request_duration_seconds_sum{method="GET",path="/todos"} 45.67
http_request_duration_seconds_count{method="GET",path="/todos"} 1234
```

### Cardinality Control

**低基數標籤（允許使用）**：
- `method`: ~5 個值（GET, POST, PUT, DELETE, PATCH）
- `path`: ~7 個值（/todos, /todos/{id}, /health, /metrics, 等）
- `status`: ~3 個分類（2xx, 4xx, 5xx）

**高基數標籤（禁止使用）**：
- ❌ `request_id`: 無限基數（每個請求唯一）
- ❌ `user_id`: 無限基數（使用者數量不受限）
- ❌ `todo_id`: 無限基數（待辦事項數量不受限）

---

## Data Flow

### Create Todo Flow

```
Client → POST /todos {"title": "Buy milk"}
         ↓
      [Middleware]
         ↓ (生成 request_id)
      [Validation]
         ↓ (Pydantic model validation)
      [Storage]
         ↓ (生成 id="1", 儲存至記憶體)
      [Logging]
         ↓ (記錄結構化日誌)
      [Metrics]
         ↓ (增加 counter, 記錄 latency)
      [Response]
         ↓
Client ← 201 Created {"id": "1", "title": "Buy milk", "completed": false}
         + Header: X-Request-ID
```

### Error Handling Flow

```
Client → GET /todos/999 (不存在的 ID)
         ↓
      [Middleware]
         ↓ (生成 request_id)
      [Storage]
         ↓ (查詢失敗，返回 None)
      [Error Handler]
         ↓ (產生 404 錯誤)
      [Logging]
         ↓ (記錄錯誤日誌: event="request_error")
      [Metrics]
         ↓ (增加 counter: status="4xx")
      [Response]
         ↓
Client ← 404 Not Found {"detail": "待辦事項不存在"}
         + Header: X-Request-ID
```

---

## Storage Implementation

### In-Memory Store Structure

```python
from threading import Lock
from typing import Dict

class TodoStore:
    def __init__(self):
        self._todos: Dict[str, TodoResponse] = {}
        self._lock = Lock()
        self._counter = 0

    def create(self, todo_data: TodoCreate) -> TodoResponse:
        with self._lock:
            self._counter += 1
            todo = TodoResponse(
                id=str(self._counter),
                title=todo_data.title,
                completed=todo_data.completed
            )
            self._todos[todo.id] = todo
            return todo
```

**特性**：
- 執行緒安全（threading.Lock）
- O(1) 查詢複雜度（dict）
- 遞增整數 ID（易於測試與除錯）

---

## Validation Error Response Format

所有驗證錯誤遵循統一格式：

```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "標題不得為空白字串",
      "type": "value_error"
    }
  ]
}
```

**Pydantic 自動生成**，符合 FastAPI 標準格式。

---

## Summary

### 實體總覽

| 實體 | 儲存位置 | 主要用途 | 生命週期 |
|------|---------|---------|---------|
| Todo | 記憶體（dict） | 業務資料 | 直到系統重啟 |
| RequestLog | stdout（日誌） | 可觀測性 | 即時輸出，不儲存 |
| Metrics | Prometheus | 監控 | 累積統計，Prometheus 儲存 |

### 驗證規則總計

- Todo: 5 項驗證規則（VR-001 至 VR-005）
- RequestLog: 5 項驗證規則（VR-LOG-001 至 VR-LOG-005）
- Metrics: 基數控制（3 項低基數標籤）

### 下一步

資料模型已定義完成，可進入 API 契約設計（contracts/openapi.yaml）。
