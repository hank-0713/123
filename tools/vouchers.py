from db import query_db

TOOL_DEF = {
    "name": "query_unapproved_vouchers",
    "description": (
        "查詢未核准傳票數量。回傳目前尚未審核通過的會計傳票總筆數。"
        "適用於：了解待審核傳票狀況、提醒主管需要審核的事項。"
    ),
    "input_schema": {
        "type": "object",
        "properties": {},
        "required": [],
    },
}


def run(inputs: dict) -> dict:
    rows = query_db("SELECT cnt FROM [未核准傳票]")
    count = rows[0]["cnt"] if rows else 0
    return {"未核准傳票數量": count}
