from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from recommend import recommend_router
import uvicorn
 
app = FastAPI(title="고전문학 출판사 추천기 API")
 
# CORS 설정 (Streamlit에서 호출 가능하도록)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
 
# 라우터 등록
app.include_router(recommend_router)
 
@app.get("/")
async def welcome() -> dict:
    return {
        "msg": "고전문학 출판사 추천 API"
        }
 
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
 