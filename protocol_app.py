import streamlit as st
from google import genai
from google.genai import types
import json

st.set_page_config(page_title="모둠 융합 탐구 프로토콜", layout="wide")

# 세션 상태 초기화
if "step" not in st.session_state:
    st.session_state.step = 1
if "team_info" not in st.session_state:
    st.session_state.team_info = []
if "generated_topics" not in st.session_state:
    st.session_state.generated_topics = []
if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = None
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

st.title("🔬 과학과제연구: 모둠 융합 탐구 및 자가진단 프로토콜")
st.caption("Google Gemini 3.6을 활용하여 2~3명의 관심사를 실시간 융합하고 실험 타당성을 검증합니다.")

# ==========================================
# STEP 1: 개인 API 키 입력 + 모둠원 정보 입력
# ==========================================
if st.session_state.step == 1:
    st.header("Step 1. 모둠원 구성 및 사전 탐색 입력")
    
    # 🔑 학생 개인 Gemini API 키 개별 입력창
    with st.container(border=True):
        st.subheader("🔑 개인 Gemini API 키 입력")
        user_key = st.text_input(
            "발급받은 개인 API 키를 입력하세요 (Google AI Studio 발급)",
            type="password",
            value=st.session_state.api_key,
            placeholder="AIzaSy...",
            help="Google AI Studio(aistudio.google.com)에서 발급받은 본인 키를 입력합니다."
        )
        if user_key:
            st.session_state.api_key = user_key.strip()
    
    st.write("")
    
    # 모둠 참여 인원 (2명 또는 3명)
    team_size = st.radio("모둠 참여 인원을 선택하세요", [2, 3], horizontal=True)
    
    cols = st.columns(team_size)
    current_team = []
    
    for i in range(team_size):
        with cols[i]:
            name = st.text_input("이름/닉네임", value=f"학생 {chr(65+i)}", key=f"name_{i}")
            major = st.text_input("희망 진로/전공", placeholder="예: 인공지능, 환경공학, 생명과학", key=f"maj_{i}")
            keyword = st.text_input("관심분야", placeholder="예: 컴퓨터비전, 미세먼지, 기공개폐", key=f"key_{i}")
            paper = st.text_area("연구논문/자료 요약", placeholder="논문이나 핵심 실험 내용을 2~3줄로 부탁드립니다.", key=f"paper_{i}")
            current_team.append({"name": name, "major": major, "keyword": keyword, "paper": paper})
    
    st.divider()
    if st.button("Gemini 3.6 융합 가설 도출하기 ➔", type="primary"):
        if not st.session_state.api_key:
            st.error("상단에 개인 Gemini API Key를 먼저 입력해 주세요!")
        elif all(member["name"].strip() and member["major"].strip() for member in current_team):
            st.session_state.team_info = current_team
            
            with st.spinner("Gemini 3.6이 모둠원들의 관심사를 분석하여 맞춤형 융합 연구 모델을 생성 중입니다..."):
                try:
                    client = genai.Client(api_key=st.session_state.api_key)
                    
                    prompt = f"""
                    당신은 고등학교 2학년 '과학과제연구' 전문 지도교사입니다.
                    다음 학생들의 관심 분야와 사전 조사 논문을 분석하여, 모둠원 전원이 각자의 전공 역량을 살려 참여할 수 있는 현실적인 고교 수준의 실험 탐구 주제 2가지를 제안하세요.

                    [모둠원 정보]
                    {json.dumps(current_team, ensure_ascii=False, indent=2)}

                    [원칙]
                    1. 대학급 장비 없이 일반 고등학교 과학실, 센서(MBL/스마트폰), 일상 재료로 수행 가능해야 합니다.
                    2. 모든 학생이 명확한 역할 분담을 가져야 합니다.
                    3. 반드시 아래 JSON 형식으로만 응답하세요. 마크다운 코드블록을 제외한 순수 JSON만 출력하세요.

                    [JSON 응답 형식]
                    {{
                      "topics": [
                        {{
                          "title": "가설 중심의 구체적인 연구 제목",
                          "desc": "융합 구조 및 핵심 메커니즘 1줄 설명",
                          "roles": "학생별 구체적 역할 분담 (누가 무엇을 측정하고 분석하는지)",
                          "independent_var": "독립변인 (우리가 바꿀 조작 조건)",
                          "dependent_var": "종속변인 (숫자로 측정할 구체적 물리량)",
                          "controlled_var": "통제변인 (일정하게 유지할 조건들)",
                          "tools": "필요 장비 및 측정 도구",
                          "duration": "예상 소요 기간 및 주기",
                          "search_query": "DBpia/RISS 검색용 불리언 검색식"
                        }}
                      ]
                    }}
                    """
                    
                    # Gemini 3.6 Flash 모델 호출
                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                        ),
                    )
                    
                    raw_text = response.text.strip()
                    if raw_text.startswith("```json"):
                        raw_text = raw_text[7:]
                    if raw_text.endswith("```"):
                        raw_text = raw_text[:-3]
                        
                    result = json.loads(raw_text.strip())
                    st.session_state.generated_topics = result.get("topics", [])
                    st.session_state.step = 2
                    st.rerun()
                except Exception as e:
                    st.error(f"Gemini 연동 중 오류가 발생했습니다. 키가 올바른지 확인해 주세요: {e}")
        else:
            st.warning("모든 학생의 이름과 희망 진로를 입력해 주세요.")

# ==========================================
# STEP 2: Gemini가 생성한 융합 주제 선택
# ==========================================
elif st.session_state.step == 2:
    st.header("Step 2. 다학제 융합 연구 가설 선택")
    st.info("입력된 관심사를 Gemini 3.6이 분석하여 모둠원 전원이 참여할 수 있는 융합 모델을 도출했습니다.")
    
    members_summary = " + ".join([f"**{m['name']}**({m['major']})" for m in st.session_state.team_info])
    st.markdown(f"**현재 모둠:** {members_summary}")
    
    for idx, opt in enumerate(st.session_state.generated_topics):
        with st.container(border=True):
            st.subheader(opt['title'])
            st.write(f"**융합 구조:** {opt['desc']}")
            st.caption(f"**역할 분담:** {opt['roles']}")
            if st.button("이 주제로 탐구 요소 분해하기", key=f"choose_{idx}", type="primary"):
                st.session_state.selected_topic = opt
                st.session_state.step = 3
                st.rerun()
                
    st.divider()
    if st.button("⬅ 처음(Step 1)으로 돌아가기"):
        st.session_state.step = 1
        st.rerun()

# ==========================================
# STEP 3 & 4: 탐구 요소 분해 및 자가진단 루브릭
# ==========================================
elif st.session_state.step == 3:
    st.header("Step 3 & 4. 탐구 요소 분해 및 타당성 자가진단")
    topic = st.session_state.selected_topic
    st.success(f"선택한 연구 주제: **{topic['title']}**")
    
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.subheader("📋 탐구 구성 요소 전수 분해")
        st.markdown(f"""
        * **독립변인 (조작):** {topic.get('independent_var', '-')}
        * **종속변인 (측정 수치):** {topic.get('dependent_var', '-')}
        * **통제변인:** {topic.get('controlled_var', '-')}
        * **측정 도구:** {topic.get('tools', '-')}
        * **예상 소요 시간:** {topic.get('duration', '-')}
        """)
        
        st.markdown("---")
        st.markdown("**🔍 선행 연구 탐색용 검색식 (DBpia / ScienceON / RISS):**")
        st.code(topic.get('search_query', ''), language="text")

    with col_right:
        st.subheader("⚖️ 모둠 주도 타당성 자가진단 루브릭")
        st.write("모둠원들과 상의하여 아래 4개 기준을 직접 체크하세요.")
        
        q1 = st.checkbox("1. 종속변인을 눈대중이 아닌 숫자로 측정 가능한가?", value=True)
        q2 = st.checkbox("2. 주말이나 24시간 방치 없이 수업/방과후 시간 내 관리가 가능한가?", value=True)
        q3 = st.checkbox("3. 1회성이 아닌 최소 3~5회 이상 반복 측정이 가능한가?", value=True)
        q4 = st.checkbox("4. 필요한 재료를 1주일 내 안전하게 학교/일상에서 구할 수 있는가?", value=False)
        
        score = sum([q1, q2, q3, q4])
        
        st.markdown("---")
        st.markdown("### 🚦 자가진단 판정 결과")
        
        if score == 4:
            st.success("🟢 **Green Light (탐구 즉시 착수 권장)**\n모든 실험 요건이 고등학교 환경에 완벽히 부합합니다.")
        elif score == 3:
            st.warning("🟡 **Yellow Light (스케일다운 필요)**\n한 가지 제약이 발견되었습니다. 미흡한 항목의 실험 도구나 프로토콜을 간소화하세요.")
            if not q4:
                st.info("💡 **스케일다운 힌트:** 전문 시약 대신 주변 생활 재료나 학교 과학실 기본 구비 물품으로 대체할 수 있는지 검토하세요.")
        else:
            st.error("🔴 **Red Light (설계 재검토 필요)**\n학교 환경에서 현실적인 변인 통제와 데이터 수집이 어렵습니다. 이전 단계로 돌아가 가설을 수정하세요.")

    st.divider()
    if st.button("⬅ 다른 주제 선택하기"):
        st.session_state.step = 2
        st.rerun()