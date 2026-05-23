from pydantic import BaseModel, Field
from typing import Optional
from db import query_db


class AccountsReceivableInput(BaseModel):
    customer_code: Optional[str] = Field(None, description="客戶代碼")
    customer_name: Optional[str] = Field(None, description="客戶名稱關鍵字")
    month_from: Optional[str] = Field(None, description="帳款月份起 YYYYMM")
    month_to: Optional[str] = Field(None, description="帳款月份迄 YYYYMM")
    outstanding_only: Optional[bool] = Field(False, description="只顯示應收餘額 > 0")


TOOL_DEF = {
    "name": "query_accounts_receivable",
    "description": (
        "查詢應收明細表。顯示客戶應收帳款、已收款金額與應收餘額。"
        "適用於：查詢特定客戶帳款、未收款餘額統計、帳款月份分析。"
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "customer_code": {"type": "string", "description": "客戶代碼"},
            "customer_name": {"type": "string", "description": "客戶名稱關鍵字（模糊比對）"},
            "month_from": {"type": "string", "description": "帳款月份起 YYYYMM"},
            "month_to": {"type": "string", "description": "帳款月份迄 YYYYMM"},
            "outstanding_only": {"type": "boolean", "description": "true=只顯示應收餘額>0"},
        },
        "required": [],
    },
}


def run(inputs: dict) -> dict:
    p = AccountsReceivableInput(**inputs)
    conditions, args = ["1=1"], []

    if p.customer_code:
        conditions.append("客戶代碼 LIKE %s"); args.append(f"%{p.customer_code}%")
    if p.customer_name:
        conditions.append("客戶名稱 LIKE %s"); args.append(f"%{p.customer_name}%")
    if p.month_from:
        conditions.append("帳款月份 >= %s"); args.append(p.month_from)
    if p.month_to:
        conditions.append("帳款月份 <= %s"); args.append(p.month_to)
    if p.outstanding_only:
        conditions.append("應收餘額 > 0")

    sql = f"SELECT TOP 200 * FROM [應收明細表] WHERE {' AND '.join(conditions)} ORDER BY 立帳日期 DESC"
    try:
        rows = query_db(sql, args)
        total_receivable = sum(r.get("應收金額", 0) or 0 for r in rows)
        total_collected = sum(r.get("收款金額", 0) or 0 for r in rows)
        total_outstanding = sum(r.get("應收餘額", 0) or 0 for r in rows)
        return {
            "筆數": len(rows),
            "應收合計": round(total_receivable, 2),
            "已收合計": round(total_collected, 2),
            "餘額合計": round(total_outstanding, 2),
            "資料": rows,
        }
    except Exception as e:
        return {"error": f"查詢應收明細表失敗：{e}"}
