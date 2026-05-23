import asyncio
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from agent import ask

WELCOME = (
    "👋 您好！我是 ERP 智能查詢助手\n\n"
    "直接輸入問題即可查詢，例如：\n"
    "• 銀行帳戶目前有多少錢？\n"
    "• 下周有哪些採購單到期？\n"
    "• 本年度銷售收入是多少？\n"
    "• 目前有幾張未核准傳票？\n\n"
    "輸入 /help 查看完整查詢範圍 ✍️"
)

HELP = (
    "📚 可查詢範圍\n\n"
    "💰 科目餘額 — 銀行存款、現金餘額\n"
    "📦 採購/進貨 — 訂單狀態、廠商進貨\n"
    "💳 應收帳款 — 客戶帳款、收款餘額\n"
    "📈 損益表 — 收入費用、銷售分析\n"
    "📋 傳票 — 未核准傳票數量\n\n"
    "直接輸入問題即可查詢！"
)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME)


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action=ChatAction.TYPING
    )
    try:
        answer = await asyncio.to_thread(ask, question)
    except Exception as e:
        answer = f"查詢失敗：{e}"

    # Telegram Markdown 不支援表格，出錯時改純文字
    try:
        await update.message.reply_text(answer, parse_mode="Markdown")
    except Exception:
        await update.message.reply_text(answer)


def build_app(token: str) -> Application:
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    return app
