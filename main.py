import os
import requests
import time
import random
import re
import base64
from datetime import datetime

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# 로컬 환경을 위한 dotenv
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ====================== 환경 변수 설정 ======================
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
HF_TOKEN = os.environ.get("HF_TOKEN")
IMGBB_API_KEY = os.environ.get("IMGBB_API_KEY")

GEMINI_TEXT_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"


# ====================== 2026년 3월 기준 가장 터지는 Vibe Coding Fallback 풀 (60개) ======================
# 🚨 주의: 파이썬은 이 부분의 줄 맞춤(들여쓰기)에 엄청 예민합니다. 아래와 같이 똑같이 맞춰야 합니다.
FALLBACK_TOPICS = [
    "Claude Code Opus 4.6으로 하루 만에 MVP 만들기: Agent Teams 실전 가이드",
    "Cursor IDE 2026 완전 정복: Composer 모드로 3배 빠른 풀스택 개발",
    "Windsurf AI IDE vs Cursor: 2026년 어떤 걸 골라야 할까? 가격·성능 비교",
    "Lovable.dev로 코드 없이 SaaS 앱 30분 만에 뚝딱 만드는 법",
    "Google Antigravity 무료로 Claude Opus 4.6까지 쓰는 실전 팁",
    "Claude Code vs Windsurf: Agentic 워크플로우 누가 더 강할까?",
    "2026 AI 코딩 도구 가격 총정리: 월 2만원으로 최고 성능 내는 조합",
    "Cursor Composer로 대형 코드베이스 리팩토링 없이 정리하는 법",
    "Vibe Coding 초보자 로드맵: 챗봇 → AI Agent까지 5단계",
    "Gemini Code Assist 실전 가이드: Google Cloud에서 가장 강력한 코딩 도구",
    "Claude Opus 4.6 1M 컨텍스트로 대형 프로젝트 관리하는 실전 팁",
    "Windsurf Arena Mode로 여러 AI 모델 동시에 비교하며 코딩하기",
    "Lovable + Supabase + Vercel로 완전 무코드 MVP 배포하는 방법",
    "AI 코딩 도구로 기술 부채 쌓이지 않게 하는 7가지 실전 방법",
    "Claude Code vs OpenAI Codex: 2026년 코딩 에이전트 대전",
    "2026 개발자 생산성 5배 높이는 Vibe Coding 워크플로우 구축법",
    "Cursor vs GitHub Copilot X: 2026년 진짜 승자는?",
    "Claude Code Agent로 버그 자동 수정하고 테스트까지 끝내는 법",
    "Antigravity 초보자 추천 설정: 완전 무 AI 코딩 시작하기",
    "Vibe Coding으로 Micro-SaaS, Standalone 앱, Remix 템플릿 만들기",
    "Windsurf Plan Mode로 복잡한 멀티파일 작업 자동화하는 실전 가이드",
    "Claude 4.6 Sonnet vs Opus: 비용 절감하면서 성능 내는 선택법",
    "Lovable.dev 2026 가격 비교: 진짜 돈 값 하는가?",
    "AI Agent로 20시간 걸리는 작업을 50% 성공률로 끝내는 방법",
    "Cursor IDE에서 Claude Opus 4.6 쓰는 최고의 프롬프트 템플릿 10개",
    "2026 Agentic Coding 트렌드: Orchestration과 Multi-Agent 완전 정리",
    "Gemini 3.1 Pro Code Assist로 Google Cloud 풀스택 앱 빠르게 만들기",
    "Vibe Coding에서 Production 코드로 넘어가기: 보안·아키텍처 실전 팁",
    "Windsurf Cascade AI Agent로 병렬 개발하는 실전 워크플로우",
    "Claude Code로 기술 부채 없이 빠르게 MVP 출시하는 단계별 가이드",
    "Antigravity + Claude Opus 조합으로 무로 최고 성능 내는 법",
    "Cursor에서 AI로 전체 리팩토링 하는 단계별 실전 가이드",
    "2026년 개발자 필수 AI 스택: Cursor + Claude Code + Lovable 조합",
    "Lovable로 만든 앱을 실제 수익 나는 Micro-SaaS로 키우는 법",
    "AI 코딩 도구 보안 가이드: 취약점 자동 검사와 방어 전략",
    "Claude Code Agent Skills 2026 최신 기능 완전 정복",
    "Windsurf Wave 업데이트 후 달라진 점과 실전 활용법",
    "Vibe Coding으로 게임·웹앱·SaaS 3개 동시 제작하기",
    "Gemini vs Claude Code: 2026 코딩 성능·가격·속도 비교표",
    "Cursor IDE Pro vs Free: 과연 돈 주고 쓸 가치가 있을까?",
    "AI로 10배 빠른 개발하면서 코드 품질 유지하는 비법",
    "Lovable.dev vs Bolt.new vs v0: 2026년 최고의 Vibe 플랫폼 비교",
    "Claude Code로 대형 리팩토링 1시간 만에 끝내는 단계별 가이드",
    "Antigravity 무료 플랜 한계와 극복하는 실전 팁",
    "2026 AI IDE 전쟁: Cursor · Windsurf · Claude Code 승자 예측",
    "Vibe Coding 초보자를 위한 첫 프로젝트 5가지 추천",
    "Windsurf로 멀티 에이전트 동시에 작업하는 실전 팁",
    "Claude Opus 4.6 128K 출력 토큰을 제대로 활용하는 사례 모음",
    "AI 코딩 도구로 월 500만원 버는 Micro-SaaS 만드는 실전 가이드",
    "Cursor Composer + Claude Code 최고의 협업 워크플로우",
    "2026년 AI 코딩 도구로 기술 부채 없이 지속 가능한 개발하기",
    "Lovable 노코드 → 실제 코드로 넘어가기 실전 전환 가이드",
    "Gemini Code Assist + Google Cloud로 풀스택 앱 1시간 제작하기",
    "Vibe Coding의 미래: Agentic Coding이 가져올 개발자 역할 변화",
    "Claude Code vs Antigravity: 대형 코드베이스 작업 비교 2026",
    "Windsurf vs Cursor: Agentic 개발 속도와 안정성 비교",
    "2026 AI 코딩 트렌드: Human-in-the-Loop vs Fully Agentic",
    "Claude Code로 SWE-bench 고득점 내는 실전 프롬프트 전략",
    "Lovable로 빠른 프로토타입 검증 후 Cursor로 프로덕션 전환하기",
    "2026 개발자 생산성 도구 스택: Claude Code + Cursor + Lovable 조합"
    # --- 1. 일반인을 위한 AI 사용법 (Daily AI & Life Hacks) ---
    "2026년 필수 AI 비서 세팅 가이드: 제미나이 3.1과 클로드 완벽 비교",
    "코딩 1도 모르는 직장인을 위한 엑셀 AI 완전 자동화 실전 팁",
    "하루 1시간 아껴주는 마법의 AI 프롬프트 작성 공식 5가지",
    "GPT-5 시대, 질문만 잘해도 상위 1% 기획자가 되는 방법",
    "영알못도 당장 가능한 AI 실시간 번역·통역 툴 200% 활용법",
    "우리 아이 AI 교육, 의미 없는 유튜브 대신 이걸로 시작하세요",
    "50대도 쉽게 따라하는 스마트폰 AI 비서 100% 실전 활용법",
    "복잡한 연말정산과 세금 계산, AI로 3분 만에 끝내는 완벽 가이드",
    "AI로 나만의 맞춤형 다이어트 식단과 운동 루틴 1분 만에 짜기",
    "해외여행 준비 끝! AI로 완벽한 3박 4일 일정표 자동 생성하기",
    "대학생 필수! 복잡한 논문 요약부터 PPT 초안까지 AI로 끝내기",
    "똥손도 금손되는 무료 AI 이미지 생성 툴 추천 TOP 5 (2026년판)",
    "말만 하면 영상이 뚝딱? 2026년 텍스트-투-비디오(T2V) AI 완전 정복",
    "노션(Notion) AI로 개인 일정부터 가계부까지 완벽하게 관리하는 법",
    "내 목소리만 10분 학습시켜서 AI 오디오북 만드는 초간단 가이드",
    "구글 워크스페이스 코파일럿(Copilot) 실무 200% 활용 백서",

    # --- 2. AI 활용 블로그 자동화 및 수익화 (Monetization & Automation) ---
    "AI로 워드프레스 무인 자동화 수익형 블로그 세팅하기: A to Z",
    "하루 10분 투자로 월 100만원 버는 AI 뉴스레터 자동화 수익 모델",
    "제미나이 3.1 Pro로 구글 SEO 1위 먹는 상위 노출 블로그 포스팅 비법",
    "핀터레스트 + AI 이미지 자동화로 해외 트래픽 무한대로 끌어오는 법",
    "유튜브 쇼츠 무한 생성 AI 파이프라인 구축 실전 가이드 (얼굴 없는 채널)",
    "티스토리 vs 워드프레스 vs 블로거: AI 포스팅에 가장 유리한 플랫폼은?",
    "구글 애드센스 승인률 99% 달성하는 치명적인 AI 글쓰기 프롬프트",
    "잘 팔리는 전자책(e-book), AI로 하루 만에 쓰고 크몽에서 수익 내기",
    "미드저니 v7 + 엣시(Etsy) 연동으로 디지털 파일 자동 수익 창출하기",
    "인스타그램 릴스 대본부터 영상 편집까지 AI로 완전 무인 자동화",
    "API 비용 걱정 없는 로컬 LLM 기반 블로그 자동 포스팅 시스템 구축",
    "쿠팡 파트너스 자동 포스팅, AI로 저품질(Ban) 안 당하고 롱런하는 법",
    "AI가 자동으로 찾아주는 수익형 블로그 황금 키워드 100개 발굴 노하우",
    "뉴스 API와 AI 요약을 결합한 실시간 트래픽 폭발 뉴스 블로그 만들기",
    "슬립코딩(Sleep Coding): 내가 자는 동안에도 돈 버는 AI 에이전트 세팅",
    "브런치 작가 승인 프리패스: AI로 감성 에세이 초안 완벽하게 잡는 법",
    "블로그 썸네일, 더 이상 그리지 말고 AI로 10초 만에 대량 생성하세요",
    "어필리에이트 마케팅 + AI 자동 리뷰로 수동적 수익(Passive Income) 극대화하기",
    "내 웹사이트에 AI 챗봇 붙여서 CS 줄이고 구매 전환율 3배 높이는 법",

    # --- 3. Vibe Coding & No-code (자연어 코딩) ---
    "프롬프트가 곧 코드다! 2026년 Vibe Coding 필수 용어 완전 정복",
    "기획자도 앱을 만든다? 자연어 코딩으로 Todo 앱 10분 만에 배포하기",
    "마우스만 딸깍! Cursor IDE에서 자연어로 복잡한 버그 수정하는 법",
    "디자인 시안(Figma) 넣으면 React 코드가 쏟아지는 Vibe 워크플로우",
    "Vibe Coding의 핵심, '맥락(Context)'을 AI에게 완벽하게 먹이는 프롬프팅",
    "코드 한 줄 안 짜고 나만의 실시간 주식 포트폴리오 대시보드 만들기",
    "윈드서프(Windsurf) AI 에이전트와 대화하며 풀스택 서비스 배포하기",
    "\"에러 로그만 붙여넣으세요\" AI가 알아서 분석하고 고치는 디버깅의 마법",
    "Vibe Coding으로 엑셀 매크로(VBA) 완벽 대체하는 파이썬 스크립트 짜기",
    "초등학생도 하는 자연어 코딩: 파이썬 거북이 말고 AI 에이전트 다루기",
    "영어 못해도 괜찮아! 완벽한 한글 프롬프트로 깔끔한 C++ 코드 뽑아내는 법",
    "Vibe Coding 한계 돌파: 복잡한 기업용 비즈니스 로직 AI에게 이해시키기",
    "프롬프트 엔지니어링이 코딩 실력을 이기는 2026년 새로운 개발 생태계",
    "크롤링부터 데이터 시각화까지, 말로 지시해서 완성하는 데이터 분석 가이드",
    "AI가 짠 코드, 보안 취약점은 없을까? Vibe Coding 보안 검증 실전 팁",
    "GitHub Copilot을 넘어선 차세대 Vibe Coding 툴 3대장 비교 분석",
    "리액트 네이티브 모바일 앱 개발, 이제 프롬프트 3번이면 스토어 등록까지 끝납니다",
    "복잡한 백엔드 API 설계, 자연어로 DB 스키마부터 스웨거(Swagger)까지 자동 생성",

    # --- 4. 최신 개발자 트렌드 & 오픈소스 툴 (Developer & Open Source) ---
    "2026년 깃허브 스타 1위! 로컬 AI 모델 구동기 Ollama 2.0 실전 가이드",
    "vLLM과 SGLang: GPU 서버 터질 걱정 없는 초고속 오픈소스 추론 엔진 세팅법",
    "ComfyUI 워크플로우 완전 정복: 노드 기반 AI 이미지 생성의 끝판왕",
    "Qwen 2.5 로컬 설치부터 파인튜닝까지: 무료 오픈소스 LLM 실전 활용 백서",
    "LangChain은 잊어라! 차세대 Agent 프레임워크 LlamaIndex 실전 가이드",
    "Docker로 나만의 프라이빗 AI 챗봇 서버 5분 만에 깔끔하게 띄우기",
    "Supabase: 파이어베이스를 완벽히 대체할 최강의 오픈소스 BaaS 활용법",
    "Tailwind CSS와 AI의 만남: v0.dev로 1분 만에 화려한 랜딩 페이지 찍어내기",
    "오픈소스 RAG 파이프라인 구축: 우리 회사 기밀 문서만 학습한 사내 AI 만들기",
    "브라우저에서 바로 도는 WebGPU 기반 초경량 오픈소스 AI 모델 추천 TOP 3",
    "Rust 기반 초고속 터미널 툴 총정리: 2026년 개발자 힙스터 필수 아이템",
    "오픈소스 Hugging Face Transformers 라이브러리 실무 200% 활용 실전 가이드",
    "GitHub Actions로 복잡한 LLM 평가(Eval) 파이프라인 완전 자동화하기",
    "프론트엔드 대통합의 시대: 2026년 React vs Vue vs Svelte, 진짜 승자는?",
    "인터넷 없이 로컬에서 돌리는 무료 코딩 AI: DeepSeek Coder 완벽 세팅법",
    "오픈소스 벡터 DB (Chroma, Milvus, Qdrant) 성능 비교 및 실전 구축 가이드",
    "Nginx의 강력한 대체재로 떠오르는 Traefik과 Caddy 실전 라우팅 구축",
    "무거운 일렉트론(Electron)은 가라! Tauri로 초경량 데스크톱 앱 만들기",
    "개발자 포트폴리오 사이트, 오픈소스 정적 생성기(Astro)로 하루 만에 끝내기",

    # --- 5. AI 기술 트렌드 & 딥다이브 (Deep Dive into AI Tech) ---
    "멀티 에이전트 시스템(Multi-Agent): AI끼리 토론해서 최고의 결과물 도출하는 법",
    "오토 GPT(AutoGPT) 그 후 3년, 자율형 AI 에이전트는 지금 어디까지 왔나?",
    "RAG(검색 증강 생성) 초보자 가이드: AI가 헛소리(할루시네이션) 안 하게 만들기",
    "텍스트를 넘어 멀티모달(Multimodal) AI 시대로: 시각과 청각을 완벽히 이해하는 AI",
    "슬랙, 팀즈에 나만의 커스텀 AI 비서 연동해서 팀 업무 효율 10배 올리기",
    "AI가 내 메일을 읽고 답장까지? 지메일 자동화로 인박스 제로(Inbox Zero) 달성",
    "엣지 AI(Edge AI) 란? 데이터센터가 아닌 스마트폰 안에서 도는 AI 혁명",
    "브레인스토밍의 끝판왕: 마인드맵 AI로 죽은 아이디어 무한 확장하기",
    "메타(Meta) Llama 4 오픈소스 생태계가 쏘아올린 글로벌 AI 시장의 지각변동",
    "프롬프트 인젝션(Prompt Injection): AI 챗봇을 노리는 신종 해킹 공격과 방어 기법",
    "딥페이크 판별 기술: 진짜와 가짜를 구별하는 AI 창과 방패의 전쟁",
    "B2B AI 솔루션 도입 실패 사례로 알아보는 성공적인 기업 AI 전환 전략",
    "감성 AI의 시대: 사람의 마음을 읽고 깊이 공감하는 차세대 멘탈 케어 AI 기술"
]


def convert_markdown_to_html(text):
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'_(.+?)_', r'<em>\1</em>', text)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    return text

def get_blogger_service():
    creds = Credentials(
        None, 
        refresh_token=os.environ["G_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["G_CLIENT_ID"],
        client_secret=os.environ["G_CLIENT_SECRET"],
        scopes=['https://www.googleapis.com/auth/blogger']
    )
    return build('blogger', 'v3', credentials=creds)

def get_published_titles():
    try:
        service = get_blogger_service()
        blog_id = os.environ["BLOGGER_BLOG_ID"]
        request = service.posts().list(blogId=blog_id, maxResults=50, fetchBodies=False)
        response = request.execute()
        return [item.get('title', '').lower() for item in response.get('items', [])]
    except Exception as e:
        print(f"⚠️ 기존 발행 글 목록 가져오기 실패: {e}")
        return []

def get_vibe_coding_topic():
    published_titles = get_published_titles()
    random.shuffle(FALLBACK_TOPICS)
    for topic in FALLBACK_TOPICS:
        topic_lower = topic.lower()
        is_duplicate = any(topic_lower in pub or pub in topic_lower for pub in published_titles if pub)
        if not is_duplicate:
            return topic
    return "2026 AI Coding Trends"

# ====================== Hugging Face 이미지 생성 ======================
def generate_image_hf(prompt):
    """Hugging Face API를 사용하되, 로딩(503) 에러와 타임아웃을 방어하는 강력한 재시도 로직 적용"""
    print(f"🎨 Hugging Face 이미지 생성 시작...")
    
    if not HF_TOKEN:
        print("❌ HF_TOKEN이 없습니다. 환경변수(.env 또는 Github Secrets)를 확인해주세요.")
        return None

    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": prompt}
    
    # 허깅페이스 최신 API 라우터 주소로 업데이트
    models = [
        "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell",
        "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
    ]
    
    for model_url in models:
        model_name = model_url.split('/')[-1]
        print(f"📍 시도 중인 모델: {model_name}")
        max_retries = 6
        
        for attempt in range(max_retries):
            try:
                response = requests.post(model_url, headers=headers, json=payload, timeout=40)
                
                if response.status_code == 200:
                    image_bytes = response.content
                    print(f"✅ 이미지 생성 성공! (크기: {len(image_bytes)//1024}KB)")
                    return image_bytes
                elif response.status_code == 503:
                    try:
                        estimated_time = response.json().get('estimated_time', 10)
                    except:
                        estimated_time = 10
                    wait_time = min(estimated_time, 15)
                    print(f"   ⏳ 모델 로딩 중... {wait_time:.1f}초 대기 후 재시도 ({attempt+1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"   ⚠️ API 에러 ({response.status_code}): {response.text}")
                    break
            except requests.exceptions.Timeout:
                print(f"   ⏰ 타임아웃 발생. 재시도 중... ({attempt+1}/{max_retries})")
                time.sleep(5)
            except Exception as e:
                print(f"   ❌ 예기치 않은 오류: {e}")
                break
                
    print("❌ 모든 모델에서 이미지 생성에 실패했습니다.")
    return None

# ====================== ImgBB 이미지 업로드 ======================
def upload_image_to_imgbb(image_bytes):
    """생성된 이미지를 ImgBB에 업로드하고 짧은 URL을 반환합니다."""
    print("☁️ ImgBB에 이미지 업로드 중...")
    if not IMGBB_API_KEY:
        print("❌ IMGBB_API_KEY가 없습니다.")
        return None
        
    try:
        url = "https://api.imgbb.com/1/upload"
        payload = {
            "key": IMGBB_API_KEY,
            "image": base64.b64encode(image_bytes).decode('utf-8')
        }
        response = requests.post(url, data=payload, timeout=30)
        response.raise_for_status()
        
        img_url = response.json()["data"]["url"]
        print(f"✅ ImgBB 업로드 성공: {img_url}")
        return img_url
    except Exception as e:
        print(f"❌ ImgBB 업로드 실패: {e}")
        return None

# ====================== (완벽 통합) 이미지 생성 및 다이렉트 업로드 래퍼 함수 ======================
def generate_and_upload_image(image_prompt):
    # HF 모델이 Vibe Coding 블로그 스타일에 맞게 잘 그리도록 프롬프트 강화
    safe_prompt = re.sub(r'[^a-zA-Z0-9\s,]', '', image_prompt).strip()
    enhanced_prompt = f"A high-quality, vibrant flat design illustration for a tech blog. {safe_prompt}. Modern tech aesthetic, clean lines, highly detailed."
    print(f"🎨 이미지 프롬프트: {enhanced_prompt[:80]}...")
    
    # 1. HF로 이미지 바이트 생성
    image_bytes = generate_image_hf(enhanced_prompt)
    
    # 2. ImgBB로 업로드
    if image_bytes:
        img_url = upload_image_to_imgbb(image_bytes)
        if img_url:
            return img_url
            
    # 실패 시 깨지지 않는 깔끔한 기본 IT 이미지 주소 반환
    print("⚠️ 커스텀 이미지 생성/업로드 실패로 기본 이미지를 사용합니다.")
    return "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=1024&q=80"

# ====================== 콘텐츠 생성 ======================
def generate_content(topic):
    print(f"✍️ 글, 태그, 프롬프트 동시 생성 중: {topic}...")

    # AI Coding Lab & Vibe Coding Schools 스타일에 맞춘 고도화된 프롬프트
    prompt = f"""
    당신은 2026년 최신 AI 코딩 트렌드를 이끄는 'AI 코딩 랩(AI Coding Lab)' 및 'Vibe Coding Schools'의 수석 테크 에디터입니다.
    주제: "{topic}" 에 대해 독자들이 실무에 바로 적용할 수 있는 **고퀄리티 실전 기술 블로그 글**을 작성해주세요.
    
    --- WRITING STYLE & TONE ---
    1. 도입부: 독자의 문제 상황(Pain point)이나 호기심을 먼저 짚어주고, 이 글을 읽어야 하는 확실한 이유와 가치를 제시하세요. 
    2. 본문 전개: 겉핥기식 설명은 철저히 배제하세요. 윈도우 환경, 실제 개발 워크플로우 등 구체적인 유즈케이스와 인사이트 위주로 작성하세요.
    3. 어투: 전문가다운 신뢰감을 주면서도 가독성이 높은 '~합니다', '~해보겠습니다' 체를 사용하세요. (불필요하게 과도한 이모지는 자제하고, 섹션 구분을 위해 깔끔하게만 사용)
    4. 가독성: 문단은 짧고 호흡을 빠르게 가져가며, 핵심 키워드나 명령어는 굵게(Strong) 또는 코드로 처리하세요.
    
    --- CRITICAL REQUIREMENTS ---
    1. Image Prompt: 썸네일 생성을 위해 이 글을 완벽히 표현하는 영단어 나열. (예: futuristic developer, glowing AI code, ultra detailed, dark mode IDE)
    2. Tags: 이 글과 관련된 최신 트렌드 키워드 3~4개. (예: ClaudeCode, AI자동화, 개발생산성)
    3. Formatting: ONLY HTML tags (<h2>, <h3>, <p>, <ul>, <li>, <strong>, <code>, <br> 등). DO NOT use Markdown.
    
    --- Structure your response EXACTLY like this ---
    
    [FEATURED_IMAGE_PROMPT: (여기에 영어 단어 프롬프트 삽입)]
    [TAGS: 태그1, 태그2, 태그3]
    
    <article>
    <header><h1>[직관적이고 클릭을 유도하는 제목]</h1></header>
    <section class="introduction"><p>[시선을 사로잡는 날카로운 도입부]</p></section>
    <section><h2>핵심 인사이트 💡</h2><ul><li>[핵심 포인트 1]</li><li>[핵심 포인트 2]</li></ul></section>
    <section><h2>실전 적용 가이드 🛠️</h2>
    <h3>[구체적인 소제목 1]</h3><p>[상세 설명 및 실무 노하우]</p>
    <h3>[구체적인 소제목 2]</h3><p>[상세 설명 및 실무 노하우]</p>
    </section>
    <section class="conclusion"><h2>마치며 🎯</h2><p>[핵심 요약 및 독자에게 제안하는 다음 액션 플랜]</p></section>
    </article>
    """

    try:
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        response = requests.post(GEMINI_TEXT_URL, json=payload, timeout=90)
        response.raise_for_status()
        content = response.json()['candidates'][0]['content']['parts'][0]['text']
        content = convert_markdown_to_html(content.replace('```html', '').replace('```', ''))

        image_prompt, dynamic_tags = "", []

        img_match = re.search(r'\[FEATURED_IMAGE_PROMPT:\s*(.*?)\]', content)
        if img_match: image_prompt = img_match.group(1).strip()

        tag_match = re.search(r'\[TAGS:\s*(.*?)\]', content)
        if tag_match: dynamic_tags = [t.strip() for t in tag_match.group(1).split(',')]

        article_start = content.find('<article>')
        body = content[article_start:].strip() if article_start != -1 else content
        title = body[body.find('<h1>')+4 : body.find('</h1>')].strip() if '<h1>' in body else topic

        return title, body, image_prompt, dynamic_tags

    except Exception as e:
        print(f"❌ 텍스트 생성 오류: {e}")
        return None, None, "", []

# ====================== 블로거 포스팅 ======================
def post_to_blogger(title, content, image_url, dynamic_tags):
    if not title or not content: return

    service = get_blogger_service()
    blog_id = os.environ["BLOGGER_BLOG_ID"]
    
    labels = ["AI Coding", "VibeCoding"] + dynamic_tags
    labels = list(dict.fromkeys(labels))[:6]
    
    # 🎯 700 ~ 4898점 랜덤 스코어링 로직 적용
    score = random.randint(700, 4898)
    
    # ====================== (디자인 혁신) 가독성 극대화 CSS & 블로거 레이아웃 처리 ======================
    styled_content = f"""
    <style>
      .vibe-content {{ font-family: 'Noto Sans KR', sans-serif; color: #222; line-height: 1.8; letter-spacing: -0.3px; }}
      .vibe-content h2 {{ margin-top: 60px; margin-bottom: 20px; font-size: 1.6em; border-bottom: 2px solid #333; padding-bottom: 10px; font-weight: 800; }}
      .vibe-content h3 {{ margin-top: 45px; margin-bottom: 15px; font-size: 1.3em; color: #1a73e8; font-weight: bold; }}
      .vibe-content p {{ margin-bottom: 20px; font-size: 16px; word-break: keep-all; }}
      .vibe-content ul {{ margin-bottom: 35px; background-color: #f8f9fa; padding: 20px 20px 20px 40px; border-radius: 8px; }}
      .vibe-content li {{ margin-bottom: 10px; font-size: 16px; }}
      .vibe-content code {{ background-color: #e9ecef; padding: 2px 6px; border-radius: 4px; font-family: 'Courier New', Courier, monospace; color: #d63384; font-size: 0.95em; }}
      
      /* 스코어링 디자인 (심플하고 전문가 느낌 나게) */
      .vibe-rating {{ text-align: right; margin-top: 70px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 1.1em; color: #555; }}
      .score-highlight {{ font-size: 1.6em; font-weight: 900; color: #1a73e8; margin-left: 8px; }}
    </style>
    
    <div class="vibe-content">
      <div style="text-align: center; margin-bottom: 45px;">
        <img src="{image_url}" alt="{title}" style="max-width: 100%; height: auto; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);"/>
      </div>
      {content}
      
      <div class="vibe-rating">
        <strong>Vibe Score</strong>: <span class="score-highlight">{score}</span> 점
      </div>
    </div>
    """
    
    body = {"kind": "blogger#post", "title": title[:100], "content": styled_content, "labels": labels}
    
    try:
        service.posts().insert(blogId=blog_id, body=body, isDraft=False).execute()
        print(f"✅ 포스팅 성공! 태그: {labels} | Vibe Score: {score}")
    except Exception as e:
        print(f"❌ Blogger 포스팅 실패: {e}")

if __name__ == "__main__":
    print(f"\n{'='*70}\n🚀 Vibe Coding Auto Post 시작\n{'='*70}\n")
    topic = get_vibe_coding_topic()
    title, body, image_prompt, dynamic_tags = generate_content(topic)
    
    if title and body:
        # 이미지 생성 및 다이렉트 호스팅 업로드 (가장 확실한 방법)
        final_image_url = generate_and_upload_image(image_prompt)
        post_to_blogger(title, body, final_image_url, dynamic_tags)
    else:
        print("\n❌ 콘텐츠 생성에 실패했습니다.")