import streamlit as st
import requests
import os
import random
from urllib.parse import quote


# FastAPI 주소 (환경변수로 받음 - EC2 배포 대응)
FASTAPI_URL = os.environ.get("FASTAPI_URL", "http://localhost:8000")

# 분위기 목록
MOODS = [
    "성장/철학", "불안/부조리", "낭만/비극", "고독/의지",
    "어둠/철학", "풍자/환상", "낭만/사회", "철학/사랑"
]

# 페이지 설정
st.set_page_config(
    page_title="📚 고전문학 출판사 추천기",
    page_icon="📚",
    layout="centered",
)

# 제목, 소개
st.title("📚 고전문학 출판사 추천")
st.markdown(
    """
    같은 책이라도 **어떤 출판사 번역본**을 읽느냐에 따라 경험이 달라져요.  
    나의 독서 스타일을 입력하면, 딱 맞는 **책 + 출판사 조합**을 추천해드려요!
    """
)

st.divider()

# 사용자 입력 폼
st.subheader("🔍 나의 독서 스타일을 알려주세요")

# 랜덤 버튼 - session_state 초기화
if "mood" not in st.session_state:
    st.session_state["mood"] = []

col_mood, col_random = st.columns([3, 1])
with col_mood:
    st.write("**원하는 분위기** (최대 3개)")
with col_random:
    if st.button("🎲 분위기 랜덤"):
        random_mood = random.choice(MOODS)
        if random_mood not in st.session_state["mood"]:
            if len(st.session_state["mood"]) < 3:
                st.session_state["mood"].append(random_mood)
            else:
                # 3개 이미 선택된 경우 하나 교체
                st.session_state["mood"][-1] = random_mood

mood = st.multiselect(
    "분위기를 선택하세요",
    options=MOODS,
    default=st.session_state["mood"],
    max_selections=3,
    label_visibility="collapsed",
)

# 선택 안 한 경우 경고
if len(mood) == 0:
    st.warning("분위기를 최소 1개 이상 선택해주세요!")

col1, col2 = st.columns(2)

with col1:
    difficulty = st.radio(
        "선호 난이도",
        options=["쉬움", "보통", "어려움"],
        horizontal=True,
    )

with col2:
    length = st.radio(
        "선호 길이",
        options=["짧음", "보통", "길음"],
        horizontal=True,
        help="짧음: ~200p, 보통: 200~400p, 길음: 400p~",
    )

translation_style = st.radio(
    "번역 스타일",
    options=["가독성", "원문충실", "상관없음"],
    horizontal=True,
    help="가독성: 술술 읽힘 / 원문충실: 원작 뉘앙스 살림",
)

max_price = st.slider(
    "💰 최대 예산 (원)",
    min_value=8000,
    max_value=30000,
    value=15000,
    step=1000,
    format="%d원",
)

st.divider()

# 추천 요청 버튼
if st.button("📖 나에게 맞는 책 추천받기", type="primary", use_container_width=True):

    if len(mood) == 0:
        st.error("분위기를 최소 1개 이상 선택해주세요!")
        st.stop()

    # 로딩 스피너
    with st.spinner("최적의 책과 출판사를 찾는 중..."):
        try:
            # FastAPI에 POST 요청
            response = requests.post(
                f"{FASTAPI_URL}/recommend",
                json={
                    "mood": mood,
                    "difficulty": difficulty,
                    "length": length,
                    "translation_style": translation_style,
                    "max_price": max_price,
                },
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()

        except requests.exceptions.ConnectionError:
            st.error("❌ FastAPI 서버에 연결할 수 없어요. 서버가 실행 중인지 확인해주세요.")
            st.stop()
        except requests.exceptions.Timeout:
            st.error("❌ 요청 시간이 초과됐어요. 잠시 후 다시 시도해주세요.")
            st.stop()
        except Exception as e:
            st.error(f"❌ 오류가 발생했어요: {e}")
            st.stop()

    # 결과 출력
    st.success(f"✅ {data['total_checked']}개 판본 중 최적의 조합을 찾았어요!")

    # 입력 조건 expander
    with st.expander("📋 내가 입력한 조건 보기"):
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            st.write(f"**분위기:** {', '.join(mood)}")
            st.write(f"**난이도:** {difficulty}")
            st.write(f"**길이:** {length}")
        with col_e2:
            st.write(f"**번역 스타일:** {translation_style}")
            st.write(f"**최대 예산:** {max_price:,}원")


    recommendations = data["recommendations"]

    if not recommendations:
        st.warning("조건에 맞는 책을 찾지 못했어요. 조건을 조금 완화해보세요.")
    else:
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]

        for i, book in enumerate(recommendations):
            medal = medals[i] if i < len(medals) else f"{i+1}."

            with st.container():
                st.markdown(f"### {medal} {book['title']} — **{book['publisher']}**")

                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.write("**작가**")
                    st.write(book["author"])
                with col_b:
                    st.write("**역자**")
                    st.write(book["translator"])
                with col_c:
                    st.write("**가격**")
                    st.write(f"{book['price']:,}원")

                st.info(f"📝 **번역 특징:** {book['description']}")
                st.success(f"💡 **이런 분께 추천:** {book['recommend_point']}")

                # 네이버 검색 링크
                search_url = f"https://search.naver.com/search.naver?where=book&query={quote(book['title']+' '+book['publisher'])}"
                st.link_button("🔍 네이버에서 검색하기", search_url)

                st.divider()

    # 하단 안내
    st.caption(
        f"💬 총 {data['total_checked']}개 판본을 비교했어요. "
        "같은 책이라도 출판사마다 번역이 달라 전혀 다른 독서 경험이 될 수 있답니다!"
    )

# 사이드바 — 출판사 소개
with st.sidebar:
    st.header("🏢 출판사별 특징")
    st.markdown(
        """
        **민음사 세계문학전집**  
        - 1998년부터 시작된 국내 최장수 세계문학 시리즈  
        - 원문에 충실한 번역, 고풍스러운 문체  
        - 책등에 작가 사진이 인쇄된 것으로 유명  

        ---

        **문학동네 세계문학전집**  
        - 현대적이고 세련된 번역 스타일  
        - 가독성이 좋아 고전 입문자에게 추천  
        - 감각적인 표지 디자인

        ---

        **열린책들 세계문학**  
        - 원문 충실성과 가독성의 균형  
        - 편집 품질이 안정적  
        - 러시아 문학 번역에 특히 강점  
        """
    )
    st.divider()
    st.caption("📌 데이터 기준: 교보문고 판매 중인 판본")