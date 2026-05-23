from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from agent import ask

app = FastAPI(
    title="ERP 智能查詢 API",
    description="讓主管用口語化方式查詢 ERP 資料",
    version="1.0.0",
)


class QueryRequest(BaseModel):
    question: str
    session_id: Optional[str] = None  # 預留給未來多輪對話


class QueryResponse(BaseModel):
    answer: str
    session_id: Optional[str] = None


@app.get("/")
def root():
    return {"status": "ok", "message": "ERP 智能查詢服務運行中"}


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
