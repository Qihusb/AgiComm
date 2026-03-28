from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.modules.media_inquiring.inquiry_engine import InquiryEngine

app = FastAPI(title="AgiComm Media Inquiring API")

# 初始化引擎
engine = InquiryEngine("data/processed/media_science_generalized.csv")

class EventRequest(BaseModel):
    event_text: str
    media_count: int = 3

@app.post("/simulate/inquiry")
async def run_inquiry(request: EventRequest):
    try:
        data = engine.simulate_press_conference(request.event_text, request.media_count)
        return {"status": "success", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)