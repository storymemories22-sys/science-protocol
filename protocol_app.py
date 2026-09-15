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
st.caption("Google Gemini 3.6 기반 실시간 다학제 융합, 상세 실험 프로토콜 및 타당성 진단 시스템")

# ==========================================
# STEP 1: 개인 API 키 입력 + 모둠원 정보 입력
# ==========================================
if st.session_state.step == 1:
    st.header("Step 1. 모둠원 구성 및 사전 탐색 입력")
    
    with st.container(border=True):
        st.subheader("🔑 개인 Gemini API 키 입력")
        user_key = st.text_input(
            "발급받은 개인 API 키를 입력하세요 (Google AI Studio 발급)",
            type="password",
            value=st.session_state.api_key,
            placeholder="AIzaSy...",
            help="Google AI Studio(aistudio.google.com)에서 무료 발급받은 본인 키를 입력합니다."
        )
        if user_key:
            st.session_state.api_key = user_key.strip()
    
    st.write("")
    
    team_size = st.radio("모둠 참여 인원을 선택하세요", [2, 3], horizontal=True)
    
    cols = st.columns(team_size)
    current_team = []
    
    for i in range(team_size):
        with cols[i]:
            name = st.text_input("이름/닉네임", value=f"학생 {chr(65+i)}", key=f"name_{i}")
            major = st.text_input("희망 진로/전공", placeholder="예: 인공지능, 환경공학, 생명과학", key=f"maj_{i}")
            keyword = st.text_input("관심분야", placeholder="예: 컴퓨터비전, 미세먼지, 기공개폐", key=f"key_{i}")
            paper = st.text_area("연구논문/자료 요약", placeholder="논문이나 핵심 실험 내용을 2~3줄로 적어주세요.", key=f"paper_{i}")
            current_team.append({"name": name, "major": major, "keyword": keyword, "paper": paper})
    
    st.divider()
    if st.button("Gemini 3.6 정밀 융합 탐구 설계하기 ➔", type="primary"):
        if not st.session_state.api_key:
            st.error("상단에 개인 Gemini API Key를 먼저 입력해 주세요!")
        elif all(member["name"].strip() and member["major"].strip() for member in current_team):
            st.session_state.team_info = current_team
            
            with st.spinner("Gemini 3.6이 상세 실험 절차와 타당성 진단 솔루션을 심층 설계하고 있습니다..."):
                try:
                    client = genai.Client(api_key=st.session_state.api_key)
                    
                    prompt = f"""
                    당신은 고등학교 2학년 '과학과제연구' 전문 수석 지도교사입니다.
                    다음 학생들의 관심사와 사전 조사 내용을 바탕으로, 모둠원 전원이 명확한 역할을 분담하고 일반 고교 과학실 및 일상 도구로 100% 실행 가능한 '구체적 실험 탐구 모델 2가지'를 제안하세요.

                    [모둠원 정보]
                    {json.dumps(current_team, ensure_ascii=False, indent=2)}

                    [작성 원칙 - 매우 구체적이어야 함]
                    1. 단순 개요가 아닌, 학생들이 보고 그대로 따라 할 수 있는 상세 실험 절차(Step 1~4)를 작성할 것.
                    2. 타당성 진단 가이드(diagnosis_guide)에는 이 특정 주제에 맞춰 재료를 어디서 사는지, 수치는 어떤 무료 앱/장비로 재는지, 주말 방치 없이 어떻게 관리하는지 구체적 솔루션을 줄 것.
                    3. 학생들이 실패하기 쉬운 오차 원인과 통제 팁을 명시할 것.
                    4. 반드시 아래 JSON 형식으로만 응답할 것.

                    [JSON 응답 포맷]
                    {{
                      "topics": [
                        {{
                          "title": "가설 중심의 구체적인 연구 제목",
                          "desc": "융합 구조 및 핵심 과학적 원리 설명 (2~3줄)",
                          "roles": "학생별 구체적 역할 분담 (누가 시료를 준비하고, 측정하고, 코딩/분석하는지)",
                          "independent_var": "독립변인 (우리가 조작할 구체적 조건 및 단계)",
                          "dependent_var": "종속변인 (숫자로 측정할 물리량 및 단위)",
                          "controlled_var": "통제변인 (일정하게 유지해야 하는 핵심 조건들)",
                          "tools": "필요 장비 및 재료 목록 (학교 비치품 + 일상 대체품)",
                          "duration": "총 소요 기간 및 주간 세부 시간표",
                          "protocol": [
                            {{
                              "phase": "1단계: 시료 준비 및 간이 실험 장치 제작",
                              "detail": "시료를 어떻게 규격화하고 간이 챔버/장치를 어떻게 조립하는지 구체적 설명"
                            }},
                            {{
                              "phase": "2단계: 예비 실험 및 측정 기준선(캘리브레이션) 설정",
                              "detail": "본실험 전 센서 영점 조절, 조명/배경 통제 세팅 방법"
                            }},
                            {{
                              "phase": "3단계: 본실험 수행 및 변인별 반복 측정",
                              "detail": "독립변인 조건별 시료 투입, 측정 주기, 최소 반복 횟수(3~5회) 절차"
                            }},
                            {{
                              "phase": "4단계: 데이터 추출 및 통계/영상 분석",
                              "detail": "측정 데이터 정리법, 무료 소프트웨어(ImageJ/파이썬/엑셀) 활용 분석 절차"
                            }}
                          ],
                          "diagnosis_guide": {{
                            "quantification": "종속변인을 숫자로 정량 측정하는 구체적 방법 (추천 무료 앱, 센서, 공식)",
                            "time_management": "수업 및 방과후(1~2시간) 내에 완료할 수 있는 시간 관리 요령 (야간/주말 관리 배제법)",
                            "reproducibility": "최소 3~5회 반복 실험 시 동일한 결과를 얻기 위한 통제 요령",
                            "procurement": "필요 재료를 주변(학교 과학실, 다이소, 문구점, 인터넷 쇼핑)에서 1주일 내 안전하게 구하는 방법",
                            "scale_down_hint": "장비나 시약 조달에 문제가 생겼을 때 즉시 다운사이징할 수 있는 대체 실험법"
                          }},
                          "pitfalls_and_tips": "이 실험에서 가장 발생하기 쉬운 오차 원인 및 이를 극복하는 핵심 노하우",
                          "search_query": "DBpia/ScienceON/RISS 검색용 불리언 검색식"
                        }}
                      ]
                    }}
                    """
                    
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
            st.write(f"**융합 원리:** {opt['desc']}")
            st.caption(f"**역할 분담:** {opt['roles']}")
            if st.button("이 주제로 상세 실험 프로토콜 및 진단 열기", key=f"choose_{idx}", type="primary"):
                st.session_state.selected_topic = opt
                st.session_state.step = 3
                st.rerun()
                
    st.divider()
    if st.button("⬅ 처음(Step 1)으로 돌아가기"):
        st.session_state.step = 1
        st.rerun()

# ==========================================
# STEP 3 & 4: 상세 실험 프로토콜 및 심층 타당성 진단
# ==========================================
elif st.session_state.step == 3:
    topic = st.session_state.selected_topic
    diag = topic.get("diagnosis_guide", {})
    protocols = topic.get("protocol", [])
    
    st.success(f"🎯 **선택한 연구 주제:** {topic['title']}")
    st.write(f"**연구 개요:** {topic.get('desc', '')}")
    st.info(f"👥 **모둠 역할 분담:** {topic.get('roles', '')}")
    
    # 4개의 탭으로 구성하여 깊이 있는 정보를 제공
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔬 상세 실험 프로토콜 (단계별 가이드)",
        "⚖️ 타당성 자가진단 및 맞춤 솔루션",
        "⚠️ 오차 통제 & 실패 예방 팁",
        "🔍 선행 연구 탐색 & 계획서 정리"
    ])
    
    # -------------------------------------------------------------
    # TAB 1: 단계별 실험 프로토콜
    # -------------------------------------------------------------
    with tab1:
        st.subheader("📋 단계별 구체적 실험 절차 (Step-by-Step Protocol)")
        st.caption("학생들이 과학실에서 바로 실행할 수 있는 실천 지침입니다.")
        
        # 기본 변인 요약 카드
        with st.container(border=True):
            v_col1, v_col2, v_col3 = st.columns(3)
            with v_col1:
                st.markdown("**🔧 독립변인 (조작 조건)**")
                st.write(topic.get("independent_var", "-"))
            with v_col2:
                st.markdown("**📊 종속변인 (측정 수치)**")
                st.write(topic.get("dependent_var", "-"))
            with v_col3:
                st.markdown("**🔒 핵심 통제변인**")
                st.write(topic.get("controlled_var", "-"))
                
        st.markdown(f"**🧰 준비 장비 및 재료:** {topic.get('tools', '-')}")
        st.markdown(f"**⏱️ 권장 소요 기간 및 일정:** {topic.get('duration', '-')}")
        st.write("")
        
        # 4단계 세부 프로토콜
        for p in protocols:
            with st.expander(f"📌 {p.get('phase', '실험 단계')}", expanded=True):
                st.markdown(p.get("detail", "세부 내용이 없습니다."))
                
    # -------------------------------------------------------------
    # TAB 2: 타당성 자가진단 및 맞춤 솔루션
    # -------------------------------------------------------------
    with tab2:
        st.subheader("⚖️ 모둠 주도 타당성 자가진단 및 해결 가이드")
        st.write("각 항목을 체크하면서, AI가 제공한 **이 주제 맞춤형 솔루션**을 확인하고 토의하세요.")
        
        col_check, col_sol = st.columns([1, 1])
        
        with col_check:
            st.markdown("#### 📝 학생 자가진단 체크리스트")
            q1 = st.checkbox("1. 종속변인을 눈대중이 아닌 숫자로 측정 가능한가?", value=True)
            q2 = st.checkbox("2. 주말/24시간 방치 없이 방과후 시간 내 관리가 가능한가?", value=True)
            q3 = st.checkbox("3. 실패에 대비해 최소 3~5회 반복 측정이 가능한가?", value=True)
            q4 = st.checkbox("4. 필요한 재료를 1주일 내 안전하게 조달할 수 있는가?", value=False)
            
            score = sum([q1, q2, q3, q4])
            st.divider()
            st.markdown("#### 🚦 실시간 판정 결과")
            if score == 4:
                st.success("🟢 **Green Light (탐구 즉시 착수 권장)**\n학교 환경에서 완벽히 실행 가능합니다!")
            elif score == 3:
                st.warning("🟡 **Yellow Light (스케일다운 필요)**\n체크되지 않은 항목의 맞춤 솔루션을 참고하여 조정하세요.")
            else:
                st.error("🔴 **Red Light (설계 재검토 권장)**\n제약 사항이 많습니다. 아래 대체 실험법을 검토하거나 가설을 수정하세요.")
                
        with col_sol:
            st.markdown("#### 💡 이 실험 맞춤형 진단 해설")
            with st.container(border=True):
                st.markdown("**1. 정량적 측정 솔루션:**")
                st.caption(diag.get("quantification", "센서 및 앱을 활용해 수치화합니다."))
                
                st.markdown("**2. 방과후 시간 관리 팁:**")
                st.caption(diag.get("time_management", "방과후 1~2시간 내로 측정이 완료되는 구조입니다."))
                
                st.markdown("**3. 반복 측정 및 재현성 요령:**")
                st.caption(diag.get("reproducibility", "시료를 3개 이상 동시 배치하여 표준편차를 구합니다."))
                
                st.markdown("**4. 현실적 재료 조달 경로:**")
                st.caption(diag.get("procurement", "학교 과학실과 생활용품점에서 쉽게 조달 가능합니다."))
                
                if score < 4:
                    st.info(f"🛠️ **즉시 스케일다운 대안:** {diag.get('scale_down_hint', '간소화된 일상 대체재를 활용하세요.')}")

    # -------------------------------------------------------------
    # TAB 3: 오차 통제 및 실패 예방
    # -------------------------------------------------------------
    with tab3:
        st.subheader("⚠️ 실험 실패 방지: 오차 요인 및 극복 노하우")
        st.markdown(topic.get("pitfalls_and_tips", "오차를 줄이기 위해 암실 환경과 동일 시료군 통제가 필수적입니다."))
        st.write("")
        st.info("💡 **지도교사 Tip:** 과학과제연구 평가에서는 '가설이 맞았는가'보다 '오차 요인을 얼마나 과학적으로 분석하고 통제하려 노력했는가'가 훨씬 높은 점수를 받습니다.")

    # -------------------------------------------------------------
    # TAB 4: 선행 연구 및 정리
    # -------------------------------------------------------------
    with tab4:
        st.subheader("🔍 선행 연구 탐색 & 계획서 작성 지원")
        st.markdown("**학술 DB(DBpia / ScienceON / RISS) 검색용 불리언 검색식:**")
        st.code(topic.get('search_query', ''), language="text")
        
        st.divider()
        st.subheader("📑 연구 계획서 제출용 텍스트 요약")
        plan_text = f"""[연구 제목] {topic['title']}
[연구 목적] {topic.get('desc', '')}
[모둠 역할] {topic.get('roles', '')}
[변인 설정]
- 독립변인: {topic.get('independent_var', '')}
- 종속변인: {topic.get('dependent_var', '')}
- 통제변인: {topic.get('controlled_var', '')}
[실험 절차]
1단계: {protocols[0]['detail'] if len(protocols)>0 else ''}
2단계: {protocols[1]['detail'] if len(protocols)>1 else ''}
3단계: {protocols[2]['detail'] if len(protocols)>2 else ''}
4단계: {protocols[3]['detail'] if len(protocols)>3 else ''}
[오차 통제 방안] {topic.get('pitfalls_and_tips', '')}
"""
        st.text_area("활동지나 연구계획서에 그대로 복사해 붙여넣으세요:", value=plan_text, height=220)

    st.divider()
    if st.button("⬅ 다른 주제 선택하기"):
        st.session_state.step = 2
        st.rerun()