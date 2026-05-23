from pydantic import BaseModel, Field
from typing import Optional
from db import query_db


class GoodsReceiptInput(BaseModel):
    date_from: Optional[str] = Field(None, description="進貨日期起 YYYYMMDD")
    date_to: Optional[str] = Field(None, description="進貨日期迄 YYYYMMDD")
    vendor_code: Optional[str] = Field(None, description="廠商編號")
    vendor_name: Optional[str] = Field(None, description="廠商名稱關鍵字")
    product_code: Optional[str] = Field(None, description="產品編號")
    product_name: Optional[str] = Field(None, description="產品名稱關鍵字")


TOOL_DEF = {
    "name": "query_goods_receipts",
    "description": (
        "查詢進貨明細表。顯示實際進貨記錄，包含廠商名稱、產品、數量、單價與金額。"
        "適用於：查詢特定廠商進貨情況、期間進貨統計、進貨金額分析。"
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "date_from": {"type": "string", "description": "進貨日期起 YYYYMMDD"},
            "date_to": {"type": "string", "description": "進貨日期迄 YYYYMMDD"},
            "vendor_code": {"type": "string", "description": "廠商編號"},
            "vendor_name": {"type": "string", "description": "廠商名稱關鍵字（模糊比對）"},
            "product_code": {"type": "string", "description": "產品編號"},
            "product_name": {"type": "string", "description": "產品名稱關鍵字（模糊比對）"},
        },
        "required": [],
    },
}


def run(inputs: dict) -> dict:
    p = GoodsReceiptInput(**inputs)
    conditions, args = ["1=1"], []

    if p.date_from:
        conditions.append("採購日期 >= %s"); args.append(p.date_from)
    if p.date_to:
        conditions.append("採購日期 <= %s"); args.append(p.date_to)
    if p.vendor_code:
        conditions.append("廠商編號 LIKE %s"); args.append(f"%{p.vendor_code}%")
    if p.vendor_name:
        conditions.append("廠商名稱 LIKE %s"); args.append(f"%{p.vendor_name}%")
    if p.product_code:
        conditions.append("產品編號 LIKE %s"); args.append(f"%{p.product_code}%")
    if p.product_name:
        conditions.append("產品名稱 LIKE %s"); args.append(f"%{p.product_name}%")

    sql = f"SELECT TOP 200 * FROM [進貨明細表] WHERE {' AND '.join(conditions)} ORDER BY 採購日期 DESC"
    rows = query_db(sql, args)
    total_amount = sum(r.get("金額", 0) or 0 for r in rows)
    return {"筆數": len(rows), "合計金額": round(total_amount, 2), "資料": rows}
