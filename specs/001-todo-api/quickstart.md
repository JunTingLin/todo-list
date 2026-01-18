# Quick Start: 具備可觀測性的 TODO API 服務

**Feature**: 001-todo-api
**Purpose**: 快速開始指南，協助開發者快速建立、測試與驗證系統

## 目標

本指南將引導您完成以下步驟：
1. ✅ 環境準備與依賴安裝
2. ✅ 執行測試（TDD 測試先行）
3. ✅ 啟動開發伺服器
4. ✅ 驗證 API 端點
5. ✅ 檢查可觀測性功能（日誌、指標）
6. ✅ 本地 demo 環境（Docker Compose）

預計完成時間：**15 分鐘**

---

## 前置需求

- Python 3.11 或更新版本
- Poetry (Python 套件管理工具)
- Docker & Docker Compose (可選，用於本地 demo)
- curl 或 HTTPie (用於 API 測試)

### 檢查環境

```bash
# 檢查 Python 版本
python --version  # 應顯示 3.11.x 或更高

# 檢查 Poetry
poetry --version  # 應顯示 1.7.x 或更高

# 檢查 Docker（可選）
docker --version
docker compose version
```

---

## Step 1: 環境準備

### 1.1 Clone 專案（如尚未 clone）

```bash
cd /path/to/todo-list
git checkout 001-todo-api
```

### 1.2 安裝依賴

```bash
# 使用 Poetry 安裝所有依賴（包含開發依賴）
poetry install

# 啟動虛擬環境
poetry shell
```

### 1.3 驗證安裝

```bash
# 檢查已安裝的套件
poetry show

# 應該看到以下關鍵套件：
# - fastapi
# - uvicorn
# - pydantic
# - pytest
# - structlog
# - prometheus-client
```

---

## Step 2: 執行測試（TDD 測試先行）

**重要**：根據專案憲章「測試先行」原則，我們先執行測試（預期失敗），然後再實作功能。

### 2.1 執行所有測試

```bash
# 執行所有測試
pytest

# 預期結果：測試失敗（因為尚未實作功能）
# 這證明測試有效（紅燈階段）
```

### 2.2 執行特定測試層級

```bash
# 執行契約測試
pytest tests/contract/

# 執行整合測試
pytest tests/integration/

# 執行單元測試
pytest tests/unit/
```

### 2.3 查看測試覆蓋率

```bash
# 執行測試並生成覆蓋率報告
pytest --cov=src --cov-report=html --cov-report=term

# 在瀏覽器中查看詳細報告
open htmlcov/index.html  # macOS
# 或
xdg-open htmlcov/index.html  # Linux
```

**目標覆蓋率**：85%+

---

## Step 3: 啟動開發伺服器

### 3.1 啟動 FastAPI 開發伺服器

```bash
# 使用 Uvicorn 啟動（開發模式，自動重載）
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 預期輸出：
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete.
```

### 3.2 驗證服務啟動

```bash
# 在另一個終端機測試健康檢查
curl http://localhost:8000/health

# 預期回應：
# {"status":"healthy","timestamp":"2026-01-18T10:30:45.123456Z"}
```

### 3.3 存取 API 文件

開啟瀏覽器，前往：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

這些是 FastAPI 自動生成的互動式 API 文件。

---

## Step 4: 驗證 API 端點

### 4.1 建立待辦事項

```bash
# 使用 curl
curl -X POST http://localhost:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "購買牛奶"}'

# 預期回應（201 Created）：
# {
#   "id": "1",
#   "title": "購買牛奶",
#   "completed": false
# }

# 使用 HTTPie（更友善的輸出）
http POST http://localhost:8000/todos title="購買牛奶"
```

### 4.2 查詢所有待辦事項

```bash
curl http://localhost:8000/todos

# 預期回應（200 OK）：
# [
#   {
#     "id": "1",
#     "title": "購買牛奶",
#     "completed": false
#   }
# ]
```

### 4.3 查詢單一待辦事項

```bash
curl http://localhost:8000/todos/1

# 預期回應（200 OK）：
# {
#   "id": "1",
#   "title": "購買牛奶",
#   "completed": false
# }
```

### 4.4 更新待辦事項

```bash
# 標記為已完成
curl -X PUT http://localhost:8000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'

# 預期回應（200 OK）：
# {
#   "id": "1",
#   "title": "購買牛奶",
#   "completed": true
# }
```

### 4.5 刪除待辦事項

```bash
curl -X DELETE http://localhost:8000/todos/1

# 預期回應（204 No Content）：
# （無 body 內容）

# 驗證刪除
curl http://localhost:8000/todos/1

# 預期回應（404 Not Found）：
# {"detail": "待辦事項不存在"}
```

---

## Step 5: 檢查可觀測性功能

### 5.1 驗證結構化日誌

在伺服器終端機中，應該看到類似以下的 JSON 格式日誌：

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

**驗證項目**：
- ✅ 日誌為 JSON 格式
- ✅ 包含 request_id
- ✅ 包含 timestamp（ISO 8601 格式）
- ✅ 包含 method、path、status_code、latency_ms

### 5.2 驗證 Request ID 追蹤

```bash
# 提供自訂 request_id
curl -X GET http://localhost:8000/todos \
  -H "X-Request-ID: my-custom-request-123"

# 檢查回應標頭
curl -I http://localhost:8000/todos

# 應該看到：
# X-Request-ID: <UUID 或你提供的值>
```

**驗證項目**：
- ✅ 提供 X-Request-ID 時，系統使用該值
- ✅ 未提供時，系統自動產生 UUID
- ✅ 回應標頭包含 X-Request-ID

### 5.3 查看 Prometheus 指標

```bash
curl http://localhost:8000/metrics

# 預期回應（Prometheus 格式）：
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
# http_requests_total{method="GET",path="/todos",status="2xx"} 5
#
# HELP http_request_duration_seconds HTTP request latency
# TYPE http_request_duration_seconds histogram
# http_request_duration_seconds_bucket{method="GET",path="/todos",le="0.1"} 5
# ...
```

**驗證項目**：
- ✅ 暴露 http_requests_total 計數器
- ✅ 暴露 http_request_duration_seconds 直方圖
- ✅ 標籤僅包含低基數值（method, path, status）
- ✅ 無高基數標籤（request_id, user_id）

---

## Step 6: 本地 Demo 環境（Docker Compose）

### 6.1 啟動完整 Demo 環境

```bash
# 啟動 API + Prometheus + Grafana
docker compose -f docker/docker-compose.yml up

# 或在背景執行
docker compose -f docker/docker-compose.yml up -d
```

### 6.2 存取服務

| 服務 | URL | 說明 |
|------|-----|------|
| TODO API | http://localhost:8000 | API 服務 |
| Swagger UI | http://localhost:8000/docs | API 文件 |
| Prometheus | http://localhost:9090 | 指標查詢介面 |
| Grafana | http://localhost:3000 | 視覺化儀表板（預設帳密：admin/admin） |

### 6.3 Prometheus 查詢範例

在 Prometheus UI (http://localhost:9090)，執行以下查詢：

```promql
# 每秒請求數（QPS）
rate(http_requests_total[1m])

# P95 延遲
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# 錯誤率
rate(http_requests_total{status=~"4xx|5xx"}[1m])
```

### 6.4 Grafana 儀表板

1. 登入 Grafana (http://localhost:3000)
2. 新增 Prometheus 資料源
   - URL: http://prometheus:9090
3. 匯入預設儀表板（如有提供）

### 6.5 停止 Demo 環境

```bash
docker compose -f docker/docker-compose.yml down

# 同時清除 volumes（重置資料）
docker compose -f docker/docker-compose.yml down -v
```

---

## 驗收檢查清單

完成以上步驟後，確認以下項目：

### 功能驗收

- [ ] 所有測試通過（綠燈）
- [ ] API 端點正常運作（CRUD 操作）
- [ ] 健康檢查端點回應正常

### 可觀測性驗收

- [ ] 結構化日誌正確輸出（JSON 格式）
- [ ] Request ID 追蹤正常（提供/自動產生）
- [ ] Prometheus 指標正確暴露
- [ ] 指標無高基數標籤問題

### 效能驗收

- [ ] p95 延遲 < 100ms（CRUD 操作）
- [ ] p99 健康檢查 < 10ms
- [ ] 測試覆蓋率 > 85%

### 文件驗收

- [ ] Swagger UI 正確顯示 API 文件
- [ ] OpenAPI 規格完整且可用

---

## 常見問題

### Q1: Poetry 安裝失敗

```bash
# 解決方案：使用 pip 安裝 Poetry
pip install poetry

# 或使用官方安裝腳本
curl -sSL https://install.python-poetry.org | python3 -
```

### Q2: 測試失敗

```bash
# 確認虛擬環境已啟動
poetry shell

# 重新安裝依賴
poetry install --no-cache

# 清除 __pycache__
find . -type d -name __pycache__ -exec rm -rf {} +
```

### Q3: Docker Compose 啟動失敗

```bash
# 檢查 port 是否被占用
lsof -i :8000
lsof -i :9090
lsof -i :3000

# 停止衝突的服務或修改 docker-compose.yml 的 port 映射
```

### Q4: Prometheus 無法抓取指標

```bash
# 檢查 Prometheus 設定
cat docker/prometheus.yml

# 確認 API 服務可從 Prometheus 容器存取
docker exec -it prometheus wget -O- http://api:8000/metrics
```

---

## 下一步

完成快速開始後，您可以：

1. **閱讀詳細文件**
   - [spec.md](spec.md) - 功能規格
   - [data-model.md](data-model.md) - 資料模型
   - [contracts/openapi.yaml](contracts/openapi.yaml) - API 契約

2. **執行測試案例**
   - [testcase.md](testcase.md) - 35 個測試案例

3. **開始實作**
   - 遵循 TDD 流程（測試先行）
   - 參考 [research.md](research.md) 了解技術決策

4. **生成任務清單**
   ```bash
   /speckit.tasks
   ```

---

## 支援

如遇到問題，請檢查：
- 專案 README.md
- 規格文件 (specs/001-todo-api/)
- 專案憲章 (.specify/memory/constitution.md)

---

**祝您開發順利！** 🚀
