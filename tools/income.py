from pydantic import BaseModel, Field
from typing import Optional
from db import query_db


class IncomeStatementInput(BaseModel):
    month_from: Optional[str] = Field(None, description="傳票月份起 YYYYMM")
    month_to: Optional[str] = Field(None, description="傳票月份迄 YYYYMM")
    year: Optional[str] = Field(None, description="查詢整年 YYYY，自動轉為 YYYYMM 區間")
    department: Optional[str] = Field(None, description="部門代碼")
    profit_center: Optional[str] = Field(None, description="利潤中心")
    account_category: Optional[str] = Field(
        None, description="科目大類：4=收入，5=費用，不填=全部"
    )
    account_name: Optional[str] = Field(None, description="科目名稱關鍵字")


TOOL_DEF = {
    "name": "query_income_statement",
    "description": (
        "查詢損益表。顯示收入與費用傳票明細，可按月份、部門、利潤中心篩選。"
        "適用於：本年度/本月銷售收入、費用統計、部門損益分析。"
        "科目大類 4=收入（銷貨收入等），5=費用（成本費用等）。"
        "貸減借欄位：正數=收入/負債增加，負數=資產減少/費用。"
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "month_from": {"type": "string", "description": "傳票月份起 YYYYMM，例如 202601"},
            "month_to": {"type": "string", "description": "傳票月份迄 YYYYMM，例如 202612"},
            "year": {"type": "string", "description": "查整年，例如 2026，會自動展開為 202601~202612"},
            "department": {"type": "string", "description": "部門代碼"},
            "profit_center": {"type": "string", "description": "利潤中心"},
            "account_category": {
                "type": "string",
                "description": "科目大類：4=收入，5=費用，留空=全部",
            },
            "account_name": {"type": "string", "description": "科目名稱關鍵字"},
        },
        "required": [],
    },
}


def run(inputs: dict) -> dict:
    p = IncomeStatementInput(**inputs)
    conditions, args = ["1=1"], []

    month_from = p.month_from
    month_to = p.month_to
    if p.year:
        month_from = month_from or f"{p.year}01"
        month_to = month_to or f"{p.year}12"

    if month_from:
        conditions.append("傳票月份 >= %s"); args.append(month_from)
    if month_to:
        conditions.append("傳票月份 <= %s"); args.append(month_to)
    if p.department:
        conditions.append("部門代碼 LIKE %s"); args.append(f"%{p.department}%")
    if p.profit_center:
        conditions.append("利潤中心 LIKE %s"); args.append(f"%{p.profit_center}%")
    if p.account_category:
        conditions.append("科目大類 = %s"); args.append(p.account_category)
    if p.account_name:
        conditions.append("科目名稱 LIKE %s"); args.append(f"%{p.account_name}%")

    sql = f"SELECT TOP 500 * FROM [損益表] WHERE {' AND '.join(conditions)} ORDER BY 傳票月份, 傳票編號"
    rows = query_db(sql, args)

    revenue = sum(r.get("貸減借", 0) or 0 for r in rows if str(r.get("科目大類", "")) == "4")
    expense = sum(r.get("貸減借", 0) or 0 for r in rows if str(r.get("科目大類", "")) == "5")

    return {
        "筆數": len(rows),
        "收入合計": round(revenue, 2),
        "費用合計": round(expense, 2),
        "損益": round(revenue - expense, 2),
        "資料": rows,
    }
