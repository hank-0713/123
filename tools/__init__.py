from . import purchase, receipts, receivable, balances, income, vouchers

TOOL_DEFINITIONS = [
    purchase.TOOL_DEF,
    receipts.TOOL_DEF,
    receivable.TOOL_DEF,
    balances.TOOL_DEF,
    income.TOOL_DEF,
    vouchers.TOOL_DEF,
]

_TOOL_MAP = {
    "query_purchase_orders": purchase.run,
    "query_goods_receipts": receipts.run,
    "query_accounts_receivable": receivable.run,
    "query_account_balances": balances.run,
    "query_income_statement": income.run,
    "query_unapproved_vouchers": vouchers.run,
}


def execute_tool(name: str, inputs: dict) -> dict:
    fn = _TOOL_MAP.get(name)
    if not fn:
        return {"error": f"未知工具：{name}"}
    try:
        return fn(inputs)
    except Exception as e:
        return {"error": str(e)}
