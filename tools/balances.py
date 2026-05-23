from pydantic import BaseModel, Field
from typing import Optional
from db import query_db


class AccountBalanceInput(BaseModel):
    account_code: Optional[str] = Field(None, description="會計科目代碼（前綴比對）")
    account_name: Optional[str] = Field(None, description="科目名稱關鍵字")


TOOL_DEF = {
    "name": "query_account_balances",
    "description": (
        "查詢科目餘額表。顯示各會計科目的當前餘額，包含現金、銀行存款、應收、應付等所有科目。"
        "適用於：查詢銀行帳戶餘額（科目名稱含『銀行』）、現金部位、資產負債狀況。"
        "科目代碼規則：1=資產(含現金銀行), 2=負債, 3=權益, 4=收入, 5=費用。"
        "銀行存款科目代碼通常為 1101xx，現金為 1100xx。"
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "account_code": {
                "type": "string",
                "description": "會計科目代碼前綴，例如 '11' 查所有現金銀行科目，'1101' 查銀行存款",
            },
            "account_name": {"type": "string", "description": "科目名稱關鍵字，例如 '銀行'、'現金'"},
        },
        "required": [],
    },
}


def run(inputs: dict) -> dict:
    p = AccountBalanceInput(**inputs)
    conditions, args = ["1=1"], []

    if p.account_code:
        conditions.append("會計科目 LIKE %s"); args.append(f"{p.account_code}%")
    if p.account_name:
        conditions.append("科目名稱 LIKE %s"); args.append(f"%{p.account_name}%")

    sql = f"SELECT * FROM [科目餘額表] WHERE {' AND '.join(conditions)} ORDER BY 會計科目"
    rows = query_db(sql, args)
    total = sum(r.get("科目餘額", 0) or 0 for r in rows)
    return {"筆數": len(rows), "餘額合計": round(total, 2), "資料": rows}
