import json
from datetime import datetime
import anthropic
from config import CLAUDE_API_KEY, CLAUDE_MODEL
from tools import TOOL_DEFINITIONS, execute_tool

client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

SYSTEM_PROMPT = """你是一個 ERP 智能查詢助手，幫助公司主管用口語化方式查詢 ERP 資料。
今天的日期是 {today}（{weekday}）。

你可以查詢的資料：
- 採購明細表：採購訂單狀態、預定交期、未交量（無廠商資訊）
- 進貨明細表：實際進貨記錄，含廠商名稱、數量、金額
- 應收明細表：客戶應收帳款與收款情況
- 科目餘額表：所有會計科目餘額，包含現金與銀行存款
- 損益表：收入費用明細（科目大類4=收入，5=費用）
- 未核准傳票：待審核傳票數量

重要規則：
1. 資料庫日期為 YYYYMMDD 格式，月份為 YYYYMM 格式
2. 計算「下周」= 下星期一到下星期日的日期範圍
3. 「本年度」= {year}01 到 {year}12
4. 「本月」= {yearmonth}
5. 金額回答請加千分位（例如 1,234,567 元）
6. 若有多個 tool 可用，選最合適的；複雜問題可呼叫多個 tool
7. 回答要簡潔有重點，必要時列出明細表格
"""


def _get_today_info():
    now = datetime.now()
    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    return {
        "today": now.strftime("%Y年%m月%d日"),
        "weekday": weekdays[now.weekday()],
        "year": now.strftime("%Y"),
        "yearmonth": now.strftime("%Y%m"),
    }


def ask(question: str, history: list = None) -> str:
    info = _get_today_info()
    system = SYSTEM_PROMPT.format(**info)
    messages = list(history or []) + [{"role": "user", "content": question}]

    for _ in range(10):  # max 10 rounds of tool use
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4096,
            system=system,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return "無法取得回應"

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = execute_tool(block.name, block.input)
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result, ensure_ascii=False, default=str),
                        }
                    )
            messages.append({"role": "user", "content": tool_results})
        else:
            break

    return "查詢逾時，請重試"
