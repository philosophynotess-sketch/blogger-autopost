import os
import json
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

# ====================== 데이터 로드 ======================
def load_topics(filepath="topics.json"):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("topics", [])
    except Exception as e:
        print(f"⚠️ 주제 파일 로드 실패: {e}")
        return ["Claude Code 2026 실전 활용 가이드"]

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
    except:
        return []

def get_vibe_coding_topic(available_topics):
    published_titles = get_published_titles()
    random.shuffle(available_topics)
    for topic in available_topics:
        if topic.lower() not in published_titles:
            return topic
    return "2026 Vibe Coding Tech Stack"

# ====================== 콘텐츠 생성 (UI 특화 HTML 구조 강제) ======================
def generate_content(topic):
    print(f"✍️ 디자인 최적화 고퀄리티 콘텐츠 생성 중: {topic}...")

    prompt = f"""
    당신은 2026년 최신 AI 코딩 트렌드를 이끄는 테크 블로그의 수석 에디터입니다.
    주제: "{topic}"에 대해 독자가 한눈에 읽기 편한 **세련된 UI의 테크 블로그 가이드**를 작성하세요.

    --- STRICT HTML STRUCTURE REQUIREMENTS (CRITICAL) ---
    CSS가 완벽하게 적용되도록 반드시 아래의 지정된 태그와 클래스명을 그대로 사용하세요. Markdown(##, ** 등)은 절대 금지합니다.

    1. [핵심 포인트 박스]: 글 시작 시 가장 먼저 작성
       <div class="vibe-keypoint">
         <div class="vibe-keypoint-title">💡 핵심 포인트</div>
         <p>[핵심 요약 1~2줄]</p>
       </div>

    2. [서론]: 일반 <p> 태그 사용

    3. [아코디언 목차 (TOC)]:
       <details class="vibe-toc" open>
         <summary><span class="toc-icon">📑</span> Contents</summary>
         <div class="toc-list">
           <a href="#sec1">1. [첫번째 H2 제목]</a>
           <a href="#sec2">2. [두번째 H2 제목]</a>
           </div>
       </details>

    4. [대제목 (H2)]: 반드시 목차의 링크와 일치하는 id 부여
       <h2 id="sec1">1. [제목 내용]</h2>

    5. [단계별 가이드 (카드 디자인)]: 이 클래스는 숫자가 자동으로 매겨지는 카드 UI로 변환됩니다.
       <ol class="vibe-steps">
         <li><strong>[단계명 예: Claude 설치]</strong><p>[상세 설명]</p></li>
         <li><strong>[단계명 예: 환경 구성]</strong><p>[상세 설명]</p></li>
       </ol>

    6. [예시/결과물 박스]:
       <ul class="vibe-examples">
         <li><strong>🎯 결과물 1: [이름]</strong><p>[설명]</p></li>
         <li><strong>🎯 결과물 2: [이름]</strong><p>[설명]</p></li>
       </ul>

    7. [기타 본문 내용]: <h3>, <p>, <strong> 등을 적절히 섞어 가독성 높게 작성.

    --- STRATEGY ---
    - 도입부에서 독자의 이목을 끌고, 단계별 가이드는 구체적이고 실전적인 내용으로 5~6단계를 구성하세요.
    - 문체는 전문적이면서도 친근한 블로거의 말투(~해요, ~거든요, ~보세요)를 사용하세요.

    [FEATURED_IMAGE_PROMPT: (Thumbnail prompt in English, flat tech illustration style)]
    [TAGS: Tag1, Tag2, Tag3, Tag4]
    
    <article>
    [위 구조를 엄격히 준수한 본문 내용 전체 (Markdown 금지, 오직 HTML만)]
    </article>
    """

    try:
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        response = requests.post(GEMINI_TEXT_URL, json=payload, timeout=120)
        response.raise_for_status()
        
        full_text = response.json()['candidates'][0]['content']['parts'][0]['text']
        
        image_prompt = re.search(r'\[FEATURED_IMAGE_PROMPT:\s*(.*?)\]', full_text)
        image_prompt = image_prompt.group(1).strip() if image_prompt else topic
        
        tags_match = re.search(r'\[TAGS:\s*(.*?)\]', full_text)
        dynamic_tags = [t.strip() for t in tags_match.group(1).split(',')] if tags_match else []

        article_start = full_text.find('<article>')
        body = full_text[article_start:].strip() if article_start != -1 else full_text
        
        # 만약 AI가 <h1>을 넣었다면 제거 (Blogger 제목과 중복 방지)
        body = re.sub(r'<h1>.*?</h1>', '', body, flags=re.DOTALL).replace('<article>', '').replace('</article>', '').strip()
        
        return topic, body, image_prompt, dynamic_tags
    except Exception as e:
        print(f"❌ 콘텐츠 생성 오류: {e}")
        return None, None, "", []

# ====================== 이미지 처리 ======================
def generate_and_upload_image(image_prompt):
    safe_prompt = re.sub(r'[^a-zA-Z0-9\s,]', '', image_prompt).strip()
    enhanced_prompt = f"Modern flat vector illustration, tech blog banner, UI UX design, clean lines, futuristic, {safe_prompt}, 8k"
    
    print("🎨 썸네일 이미지 생성 중...")
    if not HF_TOKEN: return "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=1024"
    
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    try:
        url = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
        res = requests.post(url, headers=headers, json={"inputs": enhanced_prompt}, timeout=60)
        if res.status_code == 200:
            return upload_image_to_imgbb(res.content)
    except:
        pass
    return "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=1024"

def upload_image_to_imgbb(image_bytes):
    try:
        url = "https://api.imgbb.com/1/upload"
        payload = {"key": IMGBB_API_KEY, "image": base64.b64encode(image_bytes).decode('utf-8')}
        response = requests.post(url, data=payload, timeout=30)
        return response.json()["data"]["url"]
    except:
        return "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=1024"

# ====================== 포스팅 (CSS 주입) ======================
def post_to_blogger(title, content, image_url, dynamic_tags):
    if not title or not content: return
    service = get_blogger_service()
    blog_id = os.environ["BLOGGER_BLOG_ID"]
    
    rating_val = round(random.uniform(4.7, 5.0), 1)
    rates_count = random.randint(1100, 4500)
    
    # 스크린샷과 동일한 UI를 렌더링하는 핵심 CSS
    styled_content = f"""
    <style>
      html {{ scroll-behavior: smooth; }}
      .vibe-container {{ font-family: 'Pretendard', 'Noto Sans KR', sans-serif; color: #333; line-height: 1.7; font-size: 16px; word-break: keep-all; }}
      
      /* 대표 이미지 */
      .vibe-hero-img {{ width: 100%; border-radius: 12px; margin-bottom: 25px; object-fit: cover; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
      
      /* 핵심 포인트 박스 (보라색) */
      .vibe-keypoint {{ background-color: #f5f3ff; border: 1px solid #ede9fe; border-radius: 10px; padding: 20px 25px; margin-bottom: 35px; }}
      .vibe-keypoint-title {{ color: #6d28d9; font-weight: 800; font-size: 1.1em; margin-bottom: 8px; }}
      .vibe-keypoint p {{ margin: 0; color: #4c1d95; font-size: 0.95em; }}
      
      /* 아코디언 목차 (베이지색) */
      .vibe-toc {{ background-color: #fffaf0; border: 1px solid #feebc8; border-radius: 10px; padding: 20px 25px; margin: 40px 0; }}
      .vibe-toc summary {{ font-weight: 800; font-size: 1.2em; color: #2d3748; cursor: pointer; list-style: none; outline: none; }}
      .vibe-toc summary::-webkit-details-marker {{ display: none; }}
      .vibe-toc .toc-list {{ margin-top: 15px; padding-top: 15px; border-top: 1px solid #fbd38d; }}
      .vibe-toc a {{ display: block; text-decoration: none; color: #3182ce; font-weight: 600; padding: 6px 0; transition: 0.2s; }}
      .vibe-toc a:hover {{ color: #2b6cb0; text-decoration: underline; }}
      
      /* H2 대제목 (하단 파란선) */
      .vibe-container h2 {{ font-size: 1.4em; font-weight: 800; color: #1a202c; border-bottom: 1px solid #3182ce; padding-bottom: 12px; margin-top: 60px; margin-bottom: 25px; scroll-margin-top: 80px; }}
      .vibe-container h3 {{ font-size: 1.2em; font-weight: 700; color: #2d3748; margin-top: 40px; margin-bottom: 15px; }}
      
      /* 단계별 가이드 (카드 리스트) */
      .vibe-steps {{ list-style: none; padding: 0; counter-reset: step-counter; margin-bottom: 40px; }}
      .vibe-steps li {{ position: relative; background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 20px 25px 20px 65px; margin-bottom: 16px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }}
      .vibe-steps li::before {{ counter-increment: step-counter; content: counter(step-counter); position: absolute; left: 18px; top: 22px; background-color: #5a67d8; color: #fff; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.9em; }}
      .vibe-steps li strong {{ display: block; color: #434190; font-size: 1.1em; margin-bottom: 8px; }}
      .vibe-steps li p {{ margin: 0; color: #4a5568; font-size: 0.95em; line-height: 1.6; }}
      
      /* 결과물 예시 박스 (연한 파란색) */
      .vibe-examples {{ list-style: none; padding: 0; margin-bottom: 40px; }}
      .vibe-examples li {{ background-color: #ebf8ff; border: 1px solid #bee3f8; border-radius: 10px; padding: 20px 25px; margin-bottom: 15px; }}
      .vibe-examples li strong {{ display: block; color: #2b6cb0; font-size: 1.1em; margin-bottom: 8px; }}
      .vibe-examples li p {{ margin: 0; color: #2c5282; font-size: 0.95em; }}
      
      /* 하단 마무리 홍보 배너 */
      .vibe-promo {{ background-color: #f0f4f8; padding: 20px; border-radius: 10px; text-align: center; margin: 50px 0 30px 0; color: #2d3748; font-weight: 600; }}
      
      /* 태그 & 별점 영역 */
      .vibe-footer-meta {{ display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; border-top: 1px solid #e2e8f0; padding-top: 20px; font-size: 0.9em; }}
      .vibe-tags {{ color: #dd6b20; font-weight: 600; }}
      .vibe-rating {{ color: #d69e2e; font-weight: 800; }}
      .vibe-rating span {{ color: #718096; font-weight: 500; margin-left: 5px; }}
      
      /* 일반 텍스트 및 링크 */
      .vibe-container p {{ margin-bottom: 18px; }}
      .vibe-container a {{ color: #3182ce; text-decoration: none; }}
    </style>
    
    <div class="vibe-container">
      <img src="{image_url}" alt="Hero Image" class="vibe-hero-img" />
      
      {content}
      
      <div class="vibe-promo">
        📌 바이브코딩 스쿨은 코딩 없이도 AI로 앱을 만들 수 있도록 매일 아침·저녁 최신 내용을 업데이트합니다. 구독하고 놓치지 마세요! 🔔
      </div>
      
      <div class="vibe-footer-meta">
        <div class="vibe-tags">Tags: {', '.join(dynamic_tags[:4])}</div>
        <div class="vibe-rating">⭐⭐⭐⭐⭐ <span>{rating_val} / {rates_count} rates</span></div>
      </div>
    </div>
    """

    body = {"kind": "blogger#post", "title": title, "content": styled_content, "labels": ["AI자동화", "VibeCoding"] + dynamic_tags}
    
    try:
        service.posts().insert(blogId=blog_id, body=body, isDraft=False).execute()
        print(f"✅ 스크린샷 UI 기반 포스팅 완료: {title}")
    except Exception as e:
        print(f"❌ 포스팅 오류: {e}")

# ====================== 실행 ======================
if __name__ == "__main__":
    print(f"\n{'='*70}\n🚀 Vibe Coding Auto Post (UI 최적화 버전) 시작\n{'='*70}\n")
    topic = get_vibe_coding_topic(load_topics())
    title, body, img_prompt, tags = generate_content(topic)
    
    if title and body:
        image_url = generate_and_upload_image(img_prompt)
        post_to_blogger(title, body, image_url, tags)
    else:
        print("\n❌ 콘텐츠 생성 실패")