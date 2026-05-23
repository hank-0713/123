from pydantic import BaseModel, Field
from typing import Optional
from db import query_db


class PurchaseOrderInput(BaseModel):
    date_from: Optional[str] = Field(None, description="採購日期起 YYYYMMDD")
    date_to: Optional[str] = Field(None, description="採購日期迄 YYYYMMDD")
    delivery_date_from: Optional[str] = Field(None, description="預定交期起 YYYYMMDD")
    delivery_date_to: Optional[str] = Field(None, description="預定交期迄 YYYYMMDD")
    product_name: Optional[str] = Field(None, description="產品名稱關鍵字")
    product_code: Optional[str] = Field(None, description="產品編號")
    pending_only: Optional[bool] = Field(False, description="只顯示未交量 > 0 的訂單")


TOOL_DEF = {
    "name": "query_purchase_orders",
    "description": (
        "查詢採購明細表。顯示採購訂單的預定交期、採購量、已進貨量與未交量。"
        "適用於：查詢特定期間到期的採購單、產品採購狀況、未結案訂單統計。"
        "注意：此表無廠商資訊，廠商資訊請使用 query_goods_receipts。"
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "date_from": {"type": "string", "description": "採購日期起 YYYYMMDD"},
            "date_to": {"type": "string", "description": "採購日期迄 YYYYMMDD"},
            "delivery_date_from": {"type": "string", "description": "預定交期起 YYYYMMDD"},
            "delivery_date_to": {"type": "string", "description": "預定交期迄 YYYYMMDD"},
            "product_name": {"type": "string", "description": "產品名稱關鍵字（模糊比對）"},
            "product_code": {"type": "string", "description": "產品編號（模糊比對）"},
            "pending_only": {"type": "boolean", "description": "true=只顯示未交量>0的訂單"},
        },
        "required": [],
    },
}


def run(inputs: dict) -> dict:
    p = PurchaseOrderInput(**inputs)
    conditions, args = ["1=1"], []

    if p.date_from:
        conditions.append("採購日期 >= %s"); args.append(p.date_from)
    if p.date_to:
        conditions.append("採購日期 <= %s"); args.append(p.date_to)
    if p.delivery_date_from:
        conditions.append("預定交期 >= %s"); args.append(p.delivery_date_from)
    if p.delivery_date_to:
        conditions.append("預定交期 <= %s"); args.append(p.delivery_date_to)
    if p.product_name:
        conditions.append("產品名稱 LIKE %s"); args.append(f"%{p.product_name}%")
    if p.product_code:
        conditions.append("產品編號 LIKE %s"); args.append(f"%{p.product_code}%")
    if p.pending_only:
        conditions.append("未交量 > 0")

    sql = f"SELECT TOP 200 * FROM [採購明細表] WHERE {' AND '.join(conditions)} ORDER BY 預定交期"
    rows = query_db(sql, args)
    return {"筆數": len(rows), "資料": rows}
