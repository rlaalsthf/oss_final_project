from pydantic import BaseModel
from typing import List


# 사용자 입력 
class RecommendRequest(BaseModel):
    mood: List[str]         # 원하는 분위기 (여러 개 선택 가능)
    difficulty: str         # 난이도: 쉬움 / 보통 / 어려움
    length: str             # 길이: 짧음 / 보통 / 길음
    translation_style: str  # 번역 스타일: 가독성 / 원문충실 / 상관없음
    max_price: int          # 최대 예산 (원)


# 추천된 책 한 권의 정보
class BookResult(BaseModel):
    rank: int
    title: str
    author: str
    publisher: str
    translator: str
    description: str
    recommend_point: str
    price: int
    score: int
    mood: str


# 전체 응답 - BookResult 여러 개
class RecommendResponse(BaseModel):
    recommendations: List[BookResult]
    total_checked: int
    user_mood: List[str]