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

GEMINI_TEXT_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash:generateContent?key={GEMINI_API_KEY}"

# ====================== 데이터 로드 (카테고리 구조 반영) ======================
def load_topics(filepath="topics.json"):
    """
    topics.json 딕셔너리 구조 (대주제: [소주제들])
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data.get("topics"), list):
                return {"AI 실무 활용": data["topics"]}
            return data
    except Exception as e:
        print(f"⚠️ 주제 파일 로드 실패: {e}")
        return {"Vibe Coding 시작하기 (초보)": ["AI를 활용한 업무 자동화 혁명"]}

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

def get_vibe_coding_topic(topics_dict):
    published_titles = get_published_titles()
    
    categories = list(topics_dict.keys())
    random.shuffle(categories) 
    
    for category in categories:
        topics = topics_dict[category]
        random.shuffle(topics) 
        for topic in topics:
            if topic.lower() not in published_titles:
                return category, topic
                
    return "AI 실무 가이드", "2026 실전 AI 코딩 활용 가이드"

# ====================== 콘텐츠 생성 ======================
def generate_content(category, topic):
    print(f"✍️ 콘텐츠 생성 중... | 대주제: {category} | 주제: {topic}")

    prompt = f"""
    당신은 2026년 AI 코딩 트렌드를 이끄는 '실전 AI 코딩 랩'의 수석 에디터입니다.
    주제: "{topic}"에 대해 독자가 겪고 있는 문제를 해결해주고 실질적인 가치를 제공하는 **고퀄리티 가이드**를 작성하세요.

    --- STRICT HTML STRUCTURE (FOR UI) ---
    - <div class="vibe-keypoint">: 도입부 핵심 요약
    - <details class="vibe-toc" open>: 앵커 링크가 포함된 아코디언 목차
    - <h2 id="sec1">, <h2 id="sec2"> ... : 목차와 연결된 섹션 제목
    - <ol class="vibe-steps">: 숫자 뱃지가 달린 단계별 카드 UI
    - <ul class="vibe-examples">: 결과물 사례 박스 디자인
    - Markdown(##, ** 등) 사용 절대 금지, 오직 HTML 태그만 사용할 것.

    --- WRITING STYLE ---
    - "아직도 ~하시나요?" 같은 질문으로 독자의 공감을 유도하세요.
    - 친절하면서도 전문적인 블로거 말투(~해요, ~보세요)를 유지하세요.

    [FEATURED_IMAGE_PROMPT: (High-quality thumbnail prompt in English)]
    [TAGS: 태그1, 태그2, 태그3] (주제와 관련된 핵심 키워드 정확히 3개만 쉼표로 구분하여 작성)
    
    <article>
    [위 구조를 엄격히 준수한 본문 내용 전체]
    </article>
    """

    try:
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        response = requests.post(GEMINI_TEXT_URL, json=payload, timeout=150)
        response.raise_for_status()
        
        full_text = response.json()['candidates'][0]['content']['parts'][0]['text']
        
        image_prompt = re.search(r'\[FEATURED_IMAGE_PROMPT:\s*(.*?)\]', full_text, re.IGNORECASE)
        image_prompt = image_prompt.group(1).strip() if image_prompt else topic
        
        tags_match = re.search(r'\[TAGS:\s*(.*?)\]', full_text, re.IGNORECASE)
        dynamic_tags = [t.strip() for t in tags_match.group(1).split(',')] if tags_match else []

        article_start = full_text.find('<article>')
        body = full_text[article_start:].strip() if article_start != -1 else full_text
        
        title_match = re.search(r'<h1>(.*?)</h1>', body, re.IGNORECASE)
        final_title = title_match.group(1).strip() if title_match else topic
        
        # 프롬프트 찌꺼기 완벽 제거
        body = re.sub(r'<h1>.*?</h1>', '', body, flags=re.IGNORECASE | re.DOTALL)
        body = re.sub(r'\[FEATURED_IMAGE_PROMPT:.*?\]', '', body, flags=re.IGNORECASE | re.DOTALL)
        body = re.sub(r'\[TAGS:.*?\]', '', body, flags=re.IGNORECASE | re.DOTALL)
        body = body.replace('<article>', '').replace('</article>', '').strip()
        
        return final_title, body, image_prompt, dynamic_tags
    except Exception as e:
        print(f"❌ 콘텐츠 생성 오류: {e}")
        return None, None, "", []

# ====================== 이미지 및 포스팅 로직 ======================
def generate_and_upload_image(image_prompt):
    print("🎨 주제 맞춤형 썸네일 생성 중...")
    if not HF_TOKEN: return "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=1024"
    
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    url = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
    try:
        res = requests.post(url, headers=headers, json={"inputs": f"Modern tech lifestyle, {image_prompt}, high resolution, professional design"}, timeout=60)
        if res.status_code == 200:
            return upload_to_imgbb(res.content)
    except: pass
    return "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=1024"

def upload_to_imgbb(image_bytes):
    try:
        url = "https://api.imgbb.com/1/upload"
        payload = {"key": IMGBB_API_KEY, "image": base64.b64encode(image_bytes).decode('utf-8')}
        response = requests.post(url, data=payload, timeout=30)
        return response.json()["data"]["url"]
    except: return "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=1024"

def post_to_blogger(title, content, image_url, category, dynamic_tags):
    if not title or not content: return
    service = get_blogger_service()
    blog_id = os.environ["BLOGGER_BLOG_ID"]
    
    rating_val = round(random.uniform(4.8, 5.0), 1)
    rates_count = random.randint(1500, 5500)
    
    # 📌 대주제 1개 + 동적 생성 관련 태그 3개 = 총 4개
    final_tags = [category] + dynamic_tags[:3]
    
    styled_content = f"""
    <div class="reading-progress-container">
      <div class="reading-progress-bar" id="myProgressBar"></div>
    </div>

    <style>
      html {{ scroll-behavior: smooth; }}
      
      /* 스크롤 진행률 바 CSS (상단 고정 & 빨간색) */
      .reading-progress-container {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 5px; /* 바 두께 */
        background-color: transparent;
        z-index: 99999; /* 항상 최상단에 위치 */
      }}
      .reading-progress-bar {{
        height: 100%;
        width: 0%;
        background-color: #e53e3e; /* 요청하신 빨간색 계열 */
        transition: width 0.1s ease-out;
      }}

      /* 본문 디자인 CSS */
      .vibe-wrap {{ font-family: 'Pretendard', 'Noto Sans KR', sans-serif; color: #333; line-height: 1.8; max-width: 850px; margin: auto; word-break: keep-all; padding-top: 10px; }}
      .hero-img {{ width: 100%; border-radius: 12px; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
      
      .vibe-keypoint {{ background: #f5f3ff; border: 1px solid #ede9fe; border-radius: 10px; padding: 20px 25px; margin-bottom: 35px; }}
      .vibe-keypoint-title {{ font-weight: 800; color: #6d28d9; margin-bottom: 8px; font-size: 1.1em; }}
      .vibe-keypoint p {{ margin: 0; color: #4c1d95; font-size: 0.95em; }}
      
      .vibe-toc {{ background: #fffaf0; border: 1px solid #feebc8; border-radius: 10px; padding: 20px 25px; margin: 40px 0; }}
      .vibe-toc summary {{ font-weight: 800; font-size: 1.2em; color: #2d3748; cursor: pointer; outline: none; }}
      .vibe-toc .toc-list {{ margin-top: 15px; padding-top: 15px; border-top: 1px solid #fbd38d; }}
      .vibe-toc a {{ display: block; color: #3182ce; text-decoration: none; padding: 6px 0; font-weight: 600; transition: 0.2s; }}
      .vibe-toc a:hover {{ color: #2b6cb0; text-decoration: underline; }}
      
      h2 {{ font-size: 1.5em; font-weight: 800; border-bottom: 1px solid #3182ce; padding-bottom: 12px; margin-top: 60px; margin-bottom: 25px; scroll-margin-top: 80px; color: #1a202c; }}
      h3 {{ font-size: 1.2em; font-weight: 700; color: #2d3748; margin-top: 40px; margin-bottom: 15px; }}
      
      .vibe-steps {{ list-style: none; padding: 0; counter-reset: step-counter; margin-bottom: 40px; }}
      .vibe-steps li {{ position: relative; background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 20px 25px 20px 65px; margin-bottom: 16px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }}
      .vibe-steps li::before {{ counter-increment: step-counter; content: counter(step-counter); position: absolute; left: 18px; top: 22px; background-color: #5a67d8; color: #fff; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.9em; }}
      .vibe-steps li strong {{ display: block; color: #434190; font-size: 1.1em; margin-bottom: 8px; }}
      .vibe-steps li p {{ margin: 0; color: #4a5568; font-size: 0.95em; line-height: 1.6; }}
      
      .vibe-examples {{ list-style: none; padding: 0; margin-bottom: 40px; }}
      .vibe-examples li {{ background-color: #ebf8ff; border: 1px solid #bee3f8; border-radius: 10px; padding: 20px 25px; margin-bottom: 15px; }}
      .vibe-examples li strong {{ display: block; color: #2b6cb0; font-size: 1.1em; margin-bottom: 8px; }}
      
      .vibe-promo {{ background-color: #f0f4f8; padding: 20px; border-radius: 10px; text-align: center; margin: 50px 0 30px 0; color: #2d3748; font-weight: 600; font-size: 0.95em; }}
      
      .footer-meta {{ display: flex; justify-content: space-between; flex-wrap: wrap; border-top: 1px solid #e2e8f0; margin-top: 20px; padding-top: 20px; font-size: 0.9em; }}
      .vibe-tags {{ color: #dd6b20; font-weight: 600; }}
      .vibe-rating {{ color: #d69e2e; font-weight: 800; }}
      .vibe-rating span {{ color: #718096; font-weight: 500; margin-left: 5px; }}
    </style>
    
    <div class="vibe-wrap">
      <img src="{image_url}" class="hero-img" alt="{title}" />
      
      {content}
      
      <div class="vibe-promo">
        📌 <strong>실전 AI 코딩 랩</strong>은 코딩 없이도 AI로 수익형 앱을 만들 수 있도록 매일 아침·저녁 실무 노하우를 업데이트합니다. 구독하고 놓치지 마세요! 🔔
      </div>
      
      <div class="footer-meta">
        <div class="vibe-tags">Tags: {', '.join(final_tags)}</div>
        <div class="vibe-rating">⭐⭐⭐⭐⭐ <span>{rating_val} / {rates_count} rates</span></div>
      </div>
    </div>

    <script>
      window.addEventListener('scroll', function() {{
        var winScroll = document.body.scrollTop || document.documentElement.scrollTop;
        var height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        var scrolled = (winScroll / height) * 100;
        var progressBar = document.getElementById("myProgressBar");
        if (progressBar) {{
            progressBar.style.width = scrolled + "%";
        }}
      }});
    </script>
    """
    
    body = {"kind": "blogger#post", "title": title, "content": styled_content, "labels": final_tags}
    try:
        service.posts().insert(blogId=blog_id, body=body, isDraft=False).execute()
        print(f"✅ 스크롤 바 포함 포스팅 완료! 태그: {final_tags}")
    except Exception as e:
        print(f"❌ 포스팅 오류: {e}")

# ====================== 실행 ======================
if __name__ == "__main__":
    topics_dict = load_topics("topics.json")
    category, topic = get_vibe_coding_topic(topics_dict)
    
    title, body, img_prompt, dynamic_tags = generate_content(category, topic)
    if title and body:
        image_url = generate_and_upload_image(img_prompt)
        post_to_blogger(title, body, image_url, category, dynamic_tags)