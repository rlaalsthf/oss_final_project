from fastapi import APIRouter
from model import RecommendRequest, RecommendResponse, BookResult
import json

recommend_router = APIRouter()


#책 데이터 로드
def load_books() -> list:
    with open("books.json", "r", encoding="utf-8") as f:
        return json.load(f)

BOOKS = load_books()


# 추천 점수 계산 함수
def calculate_score(book: dict, req: RecommendRequest) -> int:
    score = 0

    # 분위기 일치 
    if book["mood"] in req.mood:
        score += 5

    if book["difficulty"] == req.difficulty:
        score += 3
    elif (book["difficulty"] == "쉬움" and req.difficulty == "보통") or \
         (book["difficulty"] == "보통" and req.difficulty in ["쉬움", "어려움"]):
        score += 1

    if book["length"] == req.length:
        score += 2

    if req.translation_style == "상관없음":
        score += 1
    elif book["translation_style"] == req.translation_style:
        score += 3

    if book["price"] <= req.max_price:
        score += 2
    elif book["price"] <= req.max_price * 1.2:
        score += 1

    return score


@recommend_router.get("/health")
async def health_check() -> dict:
    """EC2 실행 상태 확인용"""
    return {"status": "ok", "message": "고전문학 출판사 추천기 API 정상 작동 중"}


@recommend_router.post("/recommend", response_model=RecommendResponse)
async def recommend(req: RecommendRequest) -> RecommendResponse:
    """사용자 입력을 받아 출판사별 책 TOP 5 추천"""

    scored = []
    for book in BOOKS:
        score = calculate_score(book, req)
        if score > 0:
            scored.append({**book, "score": score})

    scored.sort(key=lambda x: (-x["score"], x["price"]))
    top = scored[:5]

    results = [
        BookResult(
            rank=i + 1,
            title=item["title"],
            author=item["author"],
            publisher=item["publisher"],
            translator=item["translator"],
            description=item["description"],
            recommend_point=item["recommend_point"],
            price=item["price"],
            score=item["score"],
            mood=item["mood"],
        )
        for i, item in enumerate(top)
    ]

    return RecommendResponse(
        recommendations=results,
        total_checked=len(BOOKS),
        user_mood=req.mood,
    )