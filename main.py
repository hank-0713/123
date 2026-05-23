import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from agent import ask

tg_app = None


@asynccontextmanager
async def lifespan(app_: FastAPI):
    global tg_app
    token = os.getenv("TELEGRAM_TOKEN", "")
    public_url = os.getenv("PUBLIC_URL", "").rstrip("/")
    if token:
        from telegram_bot import build_app
        tg_app = build_app(token)
        await tg_app.initialize()
        if public_url:
            webhook_url = f"{public_url}/telegram/webhook"
            await tg_app.bot.set_webhook(webhook_url)
    yield
    if tg_app:
        await tg_app.shutdown()


app = FastAPI(
    title="ERP 智能查詢 API",
    description="讓主管用口語化方式查詢 ERP 資料",
    version="1.0.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="static"), name="static")


class QueryRequest(BaseModel):
    question: str
    session_id: Optional[str] = None


class QueryResponse(BaseModel):
    answer: str
    session_id: Optional[str] = None


@app.get("/")
def index():
    return FileResponse("static/index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", response_model=QueryResponse)
def query(req: QueryRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="問題不能為空")
    try:
        answer = ask(req.question)
        return QueryResponse(answer=answer, session_id=req.session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    if tg_app is None:
        raise HTTPException(status_code=503, detail="Telegram bot 未設定")
    from telegram import Update
    data = await request.json()
    update = Update.de_json(data, tg_app.bot)
    await tg_app.process_update(update)
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
