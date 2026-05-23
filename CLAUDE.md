# ERP 智能查詢系統

## 專案簡介
讓公司主管以口語化方式查詢 SQL Server ERP 資料庫（gemio）。
後端：FastAPI + Claude API（tool use）；前端：純 HTML 聊天介面；部署：Zeabur。

## 技術架構
```
主管瀏覽器 (Web)
    ↓
FastAPI (main.py)  ←→  static/index.html (前端)
    ↓
agent.py  →  Claude API claude-haiku-4-5-20251001 (tool use)
    ↓
tools/  (6 個 tool，各對應一個 SQL View)
    ↓
SQL Server (43.153.159.36:30147 / gemio)
```

## 檔案結構
```
├── main.py            FastAPI 入口，掛載靜態檔、/ask 端點
├── agent.py           Claude API 對話循環（多輪 tool use）
├── config.py          讀取環境變數（os.getenv，有啟動時驗證）
├── db.py              pymssql 連線與 Decimal/str 序列化
├── static/
│   └── index.html     聊天前端（marked.js 渲染 Markdown）
├── tools/
│   ├── __init__.py    TOOL_DEFINITIONS 列表 + execute_tool 路由
│   ├── purchase.py    採購明細表
│   ├── receipts.py    進貨明細表
│   ├── receivable.py  應收明細表
│   ├── balances.py    科目餘額表
│   ├── income.py      損益表
│   └── vouchers.py    未核准傳票
├── zbpack.json        Zeabur 啟動指令
├── requirements.txt
└── .env               本機開發用（已加入 .gitignore，勿 commit）
```

## 本機開發

```bash
pip install -r requirements.txt
# 建立 .env（參考下方環境變數）
python main.py
# 開啟 http://localhost:8000
```

## 環境變數
| 變數 | 說明 |
|------|------|
| `DB_SERVER` | SQL Server IP |
| `DB_PORT` | 連接埠 |
| `DB_NAME` | 資料庫名稱 |
| `DB_USER` | 帳號 |
| `DB_PASSWORD` | 密碼 |
| `CLAUDE_API_KEY` | Anthropic API Key |
| `CLAUDE_MODEL` | 預設 `claude-haiku-4-5-20251001` |

## 資料庫 Views（gemio）
| View | 用途 |
|------|------|
| 採購明細表 | PO 訂單、預定交期、未交量（無廠商欄位） |
| 進貨明細表 | 實際進貨、廠商名稱、金額 |
| 應收明細表 | 客戶應收、已收、餘額（含外部 function，有時報錯） |
| 科目餘額表 | 所有科目餘額（銀行=110006） |
| 損益表 | 傳票收入/費用明細（科目大類 4=收入，5=費用） |
| 未核准傳票 | 回傳單一 cnt 欄位 |

## 日期格式
- 日期欄位：`YYYYMMDD`（char）
- 月份欄位：`YYYYMM`（varchar）

## 新增 Tool 方式
1. 在 `tools/` 新增 `xxx.py`，定義 `TOOL_DEF` dict 與 `run(inputs)` 函式
2. 在 `tools/__init__.py` import 並加入 `TOOL_DEFINITIONS` 與 `_TOOL_MAP`

## 部署（Zeabur）
Push 到 GitHub 後 Zeabur 自動部署，啟動指令來自 `zbpack.json`：
```
uvicorn main:app --host 0.0.0.0 --port $PORT
```
環境變數在 Zeabur Dashboard → Variables 設定。
