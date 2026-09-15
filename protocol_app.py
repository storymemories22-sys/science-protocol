import streamlit as st

st.set_page_config(page_title="모둠 융합 탐구 프로토콜", layout="wide")

# 세션 상태 초기화
if "step" not in st.session_state:
    st.session_state.step = 1
if "team_info" not in st.session_state:
    st.session_state.team_info = []
if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = None

st.title("🔬 과학과제연구: 모둠 융합 탐구 및 자가진단 프로토콜")
st.caption("2~3명의 관심사를 결합하고, 실험 가능 여부를 학생 주도로 검증합니다.")

# ==========================================
# STEP 1: 모둠원 정보 및 논문 입력 ('응 1', '응 2' 제목 완전 삭제)
# ==========================================
if st.session_state.step == 1:
    st.header("Step 1. 모둠원 구성 및 사전 탐색 입력")
    
    # 2명 또는 3명 선택
    team_size = st.radio("모둠 참여 인원을 선택하세요", [2, 3], horizontal=True)
    
    cols = st.columns(team_size)
    current_team = []
    
    for i in range(team_size):
        with cols[i]:
            # [응 1, 응 2 제목을 삭제하고 바로 입력창부터 시작]
            name = st.text_input("이름/닉네임", value=f"학생 {chr(65+i)}", key=f"name_{i}")
            major = st.text_input("희망 진로/전공", placeholder="예: 인공지능, 환경공학, 생명과학", key=f"maj_{i}")
            keyword = st.text_input("관심분야", placeholder="예: 컴퓨터비전, 기공개폐", key=f"key_{i}")
            paper = st.text_area("연구논문/자료 요약", placeholder="논문이나 핵심 실험 내용을 2~3줄로 부탁드립니다.", key=f"paper_{i}")
            
            current_team.append({"name": name, "major": major, "keyword": keyword, "paper": paper})
    
    st.divider()
    if st.button("융합 가설 도출 단계로 이동 ➔", type="primary"):
        if all(member["name"].strip() and member["major"].strip() for member in current_team):
            st.session_state.team_info = current_team
            st.session_state.step = 2
            st.rerun()
        else:
            st.warning("모든 학생의 이름과 희망 진로를 입력해 주세요.")

# ==========================================
# STEP 2: 융합 연구 주제 제안
# ==========================================
elif st.session_state.step == 2:
    st.header("Step 2. 다학제 융합 연구 가설 선택")
    st.info("입력된 관심사와 논문을 바탕으로 모둠원 전원이 참여할 수 있는 융합 모델을 도출했습니다.")
    
    members_summary = " + ".join([f"**{m['name']}**({m['major']})" for m in st.session_state.team_info])
    st.markdown(f"**현재 모둠:** {members_summary}")
    
    options = [
        {
            "title": "도심 수종별 엽면 미세입자 흡착 패턴 영상 분석 및 정화 효율 정량화",
            "desc": "생명과학(잎 표면 생리) + 환경(대기질 데이터) + IT(ImageJ 영상 픽셀 분석) 융합 모델",
            "roles": "역할 분담: 잎 시료 채취/분석(생명), 대기 데이터 대조(환경), 픽셀 수치화(IT)"
        },
        {
            "title": "천연 바이오차(Biochar) 투입에 따른 수질 내 오염물질 흡착능 및 센서 기반 모니터링",
            "desc": "화학(흡착 메커니즘) + 환경(수질 정화) + 전자/IT(아두이노 센서 계측) 융합 모델",
            "roles": "역할 분담: 바이오차 활성화(화학), 수질 오염원 제조(환경), 실시간 MBL 측정(IT)"
        }
    ]
    
    for idx, opt in enumerate(options):
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
    st.success(f"선택한 연구 주제: **{st.session_state.selected_topic['title']}**")
    
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.subheader("📋 탐구 구성 요소 전수 분해")
        st.markdown("""
        * **독립변인 (조작):** 도로 이격 거리(1m, 5m, 10m), 수종 2종 (침엽수/활엽수)
        * **종속변인 (측정 수치):** 잎 표면 단위면적($cm^2$)당 미세입자 픽셀 점유율(%)
        * **통제변인:** 잎 채취 높이(지상 1.5m 통일), 강우 후 경과일(동일 강우 5일 차 일괄 채취)
        * **측정 도구:** 스마트폰 접사 렌즈, 일반 광학현미경, ImageJ(오픈소스 무료 툴)
        * **예상 소요 시간:** 시료 채취 1회(2시간), 이미지 촬영 및 픽셀 분석 2주 (주 2회 방과후)
        """)
        
        st.markdown("---")
        st.markdown("**🔍 선행 연구 탐색용 검색식 (DBpia / ScienceON / RISS):**")
        st.code('("수종" OR "가로수") AND ("미세먼지" OR "입자상물질") AND ("이미지 분석" OR "ImageJ")', language="text")

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