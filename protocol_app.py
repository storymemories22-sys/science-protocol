import streamlit as st
from google import genai
from google.genai import types
import json
import urllib.parse

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
st.caption("Gemini 3.6이 융합 주제와 검증 가능한 학술 근거를 제시하고, 학생 주도로 실험 타당성을 검증합니다.")

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
            help="Google AI Studio(aistudio.google.com)에서 발급받은 키를 입력합니다."
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
            paper = st.text_area("사전 관심 메모 (선택)", placeholder="평소 관심 있던 현상이나 수업 때 배운 개념을 적어주세요.", key=f"paper_{i}")
            current_team.append({"name": name, "major": major, "keyword": keyword, "paper": paper})
    
    st.divider()
    if st.button("Gemini 3.6 정밀 탐구 및 근거 자료 생성 ➔", type="primary"):
        if not st.session_state.api_key:
            st.error("상단에 개인 Gemini API Key를 먼저 입력해 주세요!")
        elif all(member["name"].strip() and member["major"].strip() for member in current_team):
            st.session_state.team_info = current_team
            
            with st.spinner("Gemini 3.6이 융합 실험 모델과 학술 자료를 분석 및 설계하고 있습니다..."):
                try:
                    client = genai.Client(api_key=st.session_state.api_key)
                    
                    prompt = f"""
                    당신은 고등학교 2학년 '과학과제연구' 수석 지도교사이자 학술 연구 멘토입니다.
                    다음 학생들의 관심사를 바탕으로 고교 실험실 환경에서 100% 실행 가능한 '융합 실험 탐구 주제 2가지'를 설계하세요.
                    학생들이 신뢰할 수 있도록 해당 탐구의 이론적 근거가 되는 대표 선행 연구 논문/출품작 2편을 명시하세요.

                    [모둠원 정보]
                    {json.dumps(current_team, ensure_ascii=False, indent=2)}

                    [중요: 학술 자료 지침]
                    - 절대로 임의의 가짜 DOI나 존재하지 않는 웹 링크 URL을 지어내지 마십시오.
                    - 대신 실제 학술 DB(RISS, DBpia, Google Scholar)에서 즉시 검색되는 '정확한 연구 주제명/학술지명'과 '핵심 검색 키워드(search_keyword)'를 정확히 제공하십시오.

                    [JSON 응답 포맷]
                    {{
                      "topics": [
                        {{
                          "title": "가설 중심의 구체적인 연구 제목",
                          "desc": "융합 원리 및 핵심 과학적 메커니즘 (2~3줄)",
                          "roles": "학생별 구체적 역할 분담",
                          "independent_var": "독립변인 (조작 조건)",
                          "dependent_var": "종속변인 (숫자로 측정할 물리량 및 단위)",
                          "controlled_var": "통제변인 (일정하게 유지할 조건)",
                          "tools": "준비 장비 및 재료 목록",
                          "duration": "소요 기간 및 주간 세부 일정",
                          "reference_materials": [
                            {{
                              "title": "선행 연구 논문/보고서 제목 (실제 학술지나 전람회 수준의 대표적 주제)",
                              "author_org": "저자 또는 발행 학회/기관 (예: 한국환경생태학회, 국립산림과학원 등)",
                              "search_keyword": "이 논문이나 유사 원문을 찾기 위한 핵심 검색어 2~3개",
                              "why_selected": "이 연구의 근거로 선정한 구체적 이유",
                              "summary": "논문의 핵심 내용 메모 및 고교 간이 실험 착안점"
                            }},
                            {{
                              "title": "두 번째 선행 연구 제목",
                              "author_org": "저자 또는 발행 학회/기관",
                              "search_keyword": "핵심 검색어",
                              "why_selected": "선정 이유",
                              "summary": "핵심 요약 메모"
                            }}
                          ],
                          "protocol": [
                            {{"phase": "1단계: 시료 준비 및 간이 장치 제작", "detail": "상세 설명"}},
                            {{"phase": "2단계: 예비 측정 및 캘리브레이션", "detail": "상세 설명"}},
                            {{"phase": "3단계: 본실험 수행 및 변인별 반복 측정", "detail": "상세 설명"}},
                            {{"phase": "4단계: 데이터 정량화 및 영상/통계 분석", "detail": "상세 설명"}}
                          ],
                          "diagnosis_guide": {{
                            "quantification": "종속변인을 숫자로 재는 도구/앱/공식",
                            "time_management": "방과후 1~2시간 내 끝내는 시간 관리법",
                            "reproducibility": "오차를 줄이고 3~5회 재현성을 확보하는 요령",
                            "procurement": "주변(학교/다이소/인터넷)에서 재료를 1주일 내 구하는 경로",
                            "scale_down_hint": "장비 부족 시 즉시 다운사이징할 수 있는 대체 실험법"
                          }},
                          "pitfalls_and_tips": "가장 흔한 오차 요인과 극복 팁",
                          "search_query": "DBpia/RISS 검색용 불리언 검색식"
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
                    st.error(f"Gemini 연동 중 오류가 발생했습니다: {e}")
        else:
            st.warning("모든 학생의 이름과 희망 진로를 입력해 주세요.")

# ==========================================
# STEP 2: Gemini가 생성한 융합 주제 선택
# ==========================================
elif st.session_state.step == 2:
    st.header("Step 2. 다학제 융합 연구 가설 선택")
    st.info("Gemini 3.6이 학술 선행 연구와 실험 가능성을 종합 분석하여 2가지 최적 모델을 도출했습니다.")
    
    members_summary = " + ".join([f"**{m['name']}**({m['major']})" for m in st.session_state.team_info])
    st.markdown(f"**현재 모둠:** {members_summary}")
    
    for idx, opt in enumerate(st.session_state.generated_topics):
        with st.container(border=True):
            st.subheader(opt['title'])
            st.write(f"**융합 원리:** {opt['desc']}")
            st.caption(f"**역할 분담:** {opt['roles']}")
            
            refs = opt.get("reference_materials", [])
            if refs:
                ref_titles = " / ".join([f"📄 {r.get('title')}" for r in refs])
                st.caption(f"**기반 근거 논문:** {ref_titles}")
                
            if st.button("이 주제로 상세 실험 프로토콜 및 근거 자료 확인", key=f"choose_{idx}", type="primary"):
                st.session_state.selected_topic = opt
                st.session_state.step = 3
                st.rerun()
                
    st.divider()
    if st.button("⬅ 처음(Step 1)으로 돌아가기"):
        st.session_state.step = 1
        st.rerun()

# ==========================================
# STEP 3 & 4: 상세 실험 프로토콜, 타당성 진단, 실제 학술 검색 링크
# ==========================================
elif st.session_state.step == 3:
    topic = st.session_state.selected_topic
    diag = topic.get("diagnosis_guide", {})
    protocols = topic.get("protocol", [])
    refs = topic.get("reference_materials", [])
    
    st.success(f"🎯 **선택한 연구 주제:** {topic['title']}")
    st.write(f"**연구 개요:** {topic.get('desc', '')}")
    st.info(f"👥 **모둠 역할 분담:** {topic.get('roles', '')}")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔬 상세 실험 프로토콜",
        "📚 근거 논문 및 다이렉트 검색",
        "⚖️ 타당성 자가진단 및 솔루션",
        "⚠️ 오차 통제 & 계획서 정리"
    ])
    
    # TAB 1: 단계별 실험 프로토콜
    with tab1:
        st.subheader("📋 단계별 구체적 실험 절차")
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
                
        st.markdown(f"**🧰 필요 장비 및 재료:** {topic.get('tools', '-')}")
        st.markdown(f"**⏱️ 예상 소요 기간:** {topic.get('duration', '-')}")
        st.write("")
        
        for p in protocols:
            with st.expander(f"📌 {p.get('phase', '실험 단계')}", expanded=True):
                st.markdown(p.get("detail", "세부 내용이 없습니다."))

    # TAB 2: 가짜 DOI 대신 실제 작동하는 학술 검색 링크 제공
    with tab2:
        st.subheader("📚 이 연구의 학술 근거 논문 및 원문 탐색")
        st.caption("AI가 가설 수립에 참고한 학술 자료입니다. 링크를 클릭하면 실제 학술 검색 결과로 즉시 연결됩니다.")
        
        student_notes = []
        for i, ref in enumerate(refs):
            title = ref.get('title', '제목 없음')
            author_org = ref.get('author_org', '기관 미상')
            search_term = ref.get('search_keyword', title)
            
            # 실제 작동하는 안전한 학술 DB 검색 URL 생성
            scholar_url = f"https://scholar.google.com/scholar?q={urllib.parse.quote(title)}"
            dbpia_url = f"https://www.dbpia.co.kr/search/topSearch?searchQuery={urllib.parse.quote(search_term)}"
            
            with st.container(border=True):
                st.markdown(f"### 📄 근거 논문 {i+1}: {title}")
                st.markdown(f"**🏛️ 저자 / 발행 학회:** `{author_org}`")
                
                # 오류 없는 실제 다이렉트 검색 버튼 2종
                b_col1, b_col2 = st.columns(2)
                with b_col1:
                    st.link_button("🌐 Google Scholar에서 원문 검색", scholar_url, use_container_width=True)
                with b_col2:
                    st.link_button("📑 DBpia에서 관련 연구 검색", dbpia_url, use_container_width=True)
                
                st.write("")
                st.markdown(f"**💡 이 자료를 근거로 선정한 이유:**\n> {ref.get('why_selected', '-')}")
                st.markdown(f"**📝 논문 핵심 요약 및 실험 착안점:**\n{ref.get('summary', '-')}")
                
                note = st.text_input(
                    f"👉 [모둠 토의] 우리 실험에 이 논문의 어떤 점을 반영할까요?",
                    key=f"note_{i}",
                    placeholder="예: 논문에 제시된 농도 조건과 이미지 처리 기법을 참고하기로 함."
                )
                student_notes.append({"ref": ref, "student_note": note, "scholar_url": scholar_url})
                
        st.markdown("---")
        st.markdown("**🔍 추가 탐색을 위한 통합 불리언 검색식:**")
        st.code(topic.get('search_query', ''), language="text")

    # TAB 3: 타당성 자가진단
    with tab3:
        st.subheader("⚖️ 모둠 주도 타당성 자가진단 및 해결 가이드")
        col_check, col_sol = st.columns([1, 1])
        
        with col_check:
            st.markdown("#### 📝 학생 자가진단 체크리스트")
            q1 = st.checkbox("1. 종속변인을 숫자로 측정 가능한가?", value=True)
            q2 = st.checkbox("2. 주말 방치 없이 방과후 시간 내 관리가 가능한가?", value=True)
            q3 = st.checkbox("3. 3~5회 이상 반복 측정이 가능한가?", value=True)
            q4 = st.checkbox("4. 재료를 1주일 내 안전하게 조달할 수 있는가?", value=False)
            
            score = sum([q1, q2, q3, q4])
            st.divider()
            st.markdown("#### 🚦 실시간 판정 결과")
            if score == 4:
                st.success("🟢 **Green Light (탐구 즉시 착수 권장)**\n학교 환경에서 완벽히 실행 가능합니다!")
            elif score == 3:
                st.warning("🟡 **Yellow Light (스케일다운 필요)**\n오른쪽 맞춤 솔루션을 참고하여 간소화하세요.")
            else:
                st.error("🔴 **Red Light (설계 재검토 권장)**\n가설을 수정하거나 대체 실험법을 검토하세요.")
                
        with col_sol:
            st.markdown("#### 💡 이 실험 맞춤형 진단 해설")
            with st.container(border=True):
                st.markdown("**1. 정량적 측정 솔루션:**")
                st.caption(diag.get("quantification", "-"))
                st.markdown("**2. 방과후 시간 관리 팁:**")
                st.caption(diag.get("time_management", "-"))
                st.markdown("**3. 반복 측정 및 재현성 요령:**")
                st.caption(diag.get("reproducibility", "-"))
                st.markdown("**4. 현실적 재료 조달 경로:**")
                st.caption(diag.get("procurement", "-"))
                if score < 4:
                    st.info(f"🛠️ **스케일다운 대안:** {diag.get('scale_down_hint', '-')}")

    # TAB 4: 계획서 정리
    with tab4:
        st.subheader("⚠️ 오차 통제 & 최종 연구 계획서 자동 생성")
        st.markdown(f"**주요 오차 요인 및 극복 팁:**\n{topic.get('pitfalls_and_tips', '-')}")
        
        st.divider()
        st.subheader("📑 연구 계획서 제출용 종합본")
        
        ref_text_block = ""
        for idx, item in enumerate(student_notes):
            r = item["ref"]
            ref_text_block += f"""
[{idx+1}] {r.get('title')} ({r.get('author_org')})
  - 검색 출처: {item['scholar_url']}
  - 근거 선정 이유: {r.get('why_selected')}
  - 논문 핵심 요약: {r.get('summary')}
  - 모둠 적용 아이디어: {item['student_note'] or '선행 논문의 기본 조건을 벤치마킹함'}"""

        full_plan_text = f"""[과학과제연구 계획서]

1. 연구 제목: {topic['title']}
2. 연구 목적 및 가설: {topic.get('desc', '')}
3. 모둠원 및 역할 분담: {topic.get('roles', '')}

4. 변인 설계
- 독립변인: {topic.get('independent_var', '')}
- 종속변인: {topic.get('dependent_var', '')}
- 통제변인: {topic.get('controlled_var', '')}
- 사용 장비 및 재료: {topic.get('tools', '')}
- 총 소요 기간: {topic.get('duration', '')}

5. 학술적 근거 자료 및 선행 연구 분석:{ref_text_block}

6. 상세 실험 프로토콜
- 1단계: {protocols[0]['detail'] if len(protocols)>0 else ''}
- 2단계: {protocols[1]['detail'] if len(protocols)>1 else ''}
- 3단계: {protocols[2]['detail'] if len(protocols)>2 else ''}
- 4단계: {protocols[3]['detail'] if len(protocols)>3 else ''}

7. 오차 요인 및 극복 방안:
{topic.get('pitfalls_and_tips', '')}
"""
        st.text_area("활동지나 연구 계획서에 복사하여 제출하세요:", value=full_plan_text, height=350)

    st.divider()
    if st.button("⬅ 다른 주제 선택하기"):
        st.session_state.step = 2
        st.rerun()