import streamlit as st
import google.generativeai as genai
import requests
import json
import time
import pypdf
import os

# ==========================================
# 1. 核心配置与视觉风格 (高级感 UI)
# ==========================================
st.set_page_config(
    page_title="Global Growth Pilot | 外贸数字指挥官", 
    page_icon="🦁", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 注入自定义 CSS
st.markdown("""
<style>
    .main {background-color: #f8f9fa;}
    .stTextArea, .stTextInput, .stSelectbox {
        background-color: white;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        padding: 10px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        font-weight: 600;
        border: none;
        transition: all 0.3s;
    }
    h1, h2, h3 {color: #1e3a8a; font-family: 'Helvetica Neue', sans-serif;}
    section[data-testid="stSidebar"] {background-color: #ffffff; border-right: 1px solid #f0f0f0;}
    div[data-testid="metric-container"] {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        border: 1px solid #eee;
    }
</style>
""", unsafe_allow_html=True)

MEMORY_FILE = "b2b_kb_memory.json"

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ System Error: API Key missing in Secrets.")
    st.stop()

# ==========================================
# 2. 记忆与逻辑核心
# ==========================================
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f).get("text", "")
        except: return ""
    return ""

def save_memory(new_text):
    current = load_memory()
    if new_text.strip() in current: return False
    updated = current + "\n" + new_text
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump({"text": updated}, f, ensure_ascii=False)
    return True

def clear_memory():
    if os.path.exists(MEMORY_FILE): os.remove(MEMORY_FILE)

@st.cache_resource
def get_best_model(): return "models/gemini-2.5-flash"
valid_model_name = get_best_model()

def robust_generate(prompt, model_name):
    """
    这里就是连接 Google AI Studio 的核心管道。
    它会把你的 Prompt 发送给 Google，并处理网络波动。
    """
    model = genai.GenerativeModel(model_name)
    max_retries = 5
    for i in range(max_retries):
        try:
            # 这里的配置可以根据需要调整温度等，但默认的最稳
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            if "429" in str(e): time.sleep((i+1)*5); continue
            else: time.sleep(2); continue
    return "⚠️ Network Busy. Please retry."

def robust_api_search(payload, model_name, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    for i in range(3):
        try:
            res = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
            if res.status_code == 200: return res.json()
            elif res.status_code == 429: time.sleep(5); continue
            else: return {"error": f"Error {res.status_code}"}
        except Exception as e: return {"error": str(e)}
    return {"error": "Timeout"}

# ==========================================
# 3. 侧边栏 (新增社媒入口)
# ==========================================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2583/2583166.png", width=50) 
st.sidebar.markdown("### **Global Growth Pilot**")
st.sidebar.caption(f"Engine: {valid_model_name.split('/')[-1]} | Status: Online")

st.sidebar.markdown("---")

# 导航菜单 (加入 Social Engine)
MENU = {
    "home": "🏠 Intelligence Hub (总控)",
    "social": "📱 Global Social Engine (社媒)",  # <--- 新增
    "email": "📧 Inquiry Analysis (转化)",
    "bg": "🕵️‍♂️ Background Check (背调)",
    "search": "🌐 Market Deep-Dive (拓客)",
    "neg": "⛔ Negotiation Coach (谈判)",
    "support": "🛠️ Smart Support (售后)"
}

selected_page = st.sidebar.radio("Navigation", list(MENU.values()))

# 记忆状态
st.sidebar.markdown("---")
current_mem = load_memory()
mem_len = len(current_mem)
st.sidebar.metric("🧠 Knowledge Base", f"{mem_len} chars", delta="Active" if mem_len>50 else "Empty")

# 投喂入口
with st.sidebar.expander("📂 Upload Data (Knowledge)"):
    new_txt = st.text_area("Paste Text:", height=100)
    if st.button("Save Text"): 
        if new_txt: save_memory(new_txt); st.rerun()
    
    up_file = st.file_uploader("Upload PDF:", type=['pdf'])
    if up_file:
        try:
            reader = pypdf.PdfReader(up_file)
            txt = "".join([p.extract_text() or "" for p in reader.pages])
            if len(txt)>50: save_memory(txt); st.success("Saved!"); time.sleep(1); st.rerun()
            else: st.error("PDF is empty/image-only.")
        except: st.error("Error reading PDF")

    if st.button("Clear Memory"): clear_memory(); st.rerun()

KB_INJECTION = f"[INTERNAL KNOWLEDGE]: {current_mem}" if mem_len > 50 else ""

# ==========================================
# 4. 主界面逻辑
# ==========================================

# --- 🏠 首页仪表盘 ---
if selected_page == MENU["home"]:
    st.title("🚀 Intelligence Hub")
    st.markdown("The strategic backbone of your global outreach.")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Target Market", "Global / B2B", "Active")
    c2.metric("Social Engine", "Activated", "New") # 更新状态
    c3.metric("Knowledge Assets", f"{mem_len} Characters", "Loaded")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("📱 **Social Engine**\n\nOne-click content generation for LinkedIn, TikTok, and Cold DM outreach.")
        st.success("🌐 **Market Deep-Dive**\n\nReal-time Google Search integration to validate demand.")
    with col2:
        st.warning("⛔ **Negotiation Coach**\n\nHarvard-style negotiation strategies to crush objections.")
        st.error("🛠️ **Smart Support (RAG)**\n\nInstant answers from your uploaded PDF manuals.")

# --- 📱 社媒营销 (新增核心模块) ---
elif selected_page == MENU["social"]:
    st.header("📱 Global Social Engine")
    st.caption("Content Atomization: Write Once, Distribute Everywhere.")
    
    # 1. 输入区
    campaign_topic = st.text_input("📢 Campaign Topic / Product Focus:", placeholder="e.g. New Eco-friendly Packaging Material Launch")
    
    # 2. 平台选择 (三合一)
    st.markdown("#### Choose Platform Strategy:")
    platform = st.radio(
        "Select Output Format:",
        ["👔 LinkedIn (Thought Leadership)", "🎥 TikTok/IG (Viral Script)", "🤝 Cold DM (Outreach)"],
        horizontal=True
    )
    
    # 3. 生成按钮
    if st.button("🚀 Generate Assets", type="primary"):
        if not campaign_topic:
            st.warning("Please enter a topic first.")
        else:
            with st.spinner('Analyzing Knowledge Base & Writing Copy...'):
                # 4. 后端核心逻辑 (Prompt Engineering)
                # 这里植入了你从 AI Studio 获得的“灵魂”
                
                social_prompt = f"""
                {KB_INJECTION}
                
                **Role:** You are a B2B Social Media Strategist.
                **Task:** Generate content for topic: "{campaign_topic}"
                **Platform:** {platform}
                
                **Rules:**
                1. IF LinkedIn: Use Hook-Insight-Solution-CTA structure. Professional tone.
                2. IF TikTok: Create a table with [Visual Scene] and [Audio Script]. Under 45s.
                3. IF Cold DM: Short, non-salesy, focus on value. No links in first message.
                
                **Constraint:** ALWAYS verify product specs from the [INTERNAL KNOWLEDGE] provided above.
                """
                
                res = robust_generate(social_prompt, valid_model_name)
                st.session_state.social_res = res

    # 5. 结果展示
    if 'social_res' in st.session_state:
        st.markdown("---")
        st.markdown("### ✨ Generated Content")
        st.markdown(st.session_state.social_res)

# --- 📧 询盘分析 ---
elif selected_page == MENU["email"]:
    st.header("📧 Inquiry Analysis")
    c1, c2 = st.columns([2, 1])
    with c1:
        user_input = st.text_area("Paste Client Email:", height=250)
    with c2:
        st.markdown("#### 💡 Pro Tip")
        st.caption("AI will analyze tone, intent, and suggest a strategy.")
        if st.button("🚀 Analyze Now", type="primary"):
            if user_input:
                with st.spinner('Thinking...'):
                    prompt = f"{KB_INJECTION}\nAct as Sales Manager. Analyze email. Output: Intent, Score, Advice, Draft Response."
                    st.session_state.res_email = robust_generate(f"{prompt}\nInput: {user_input}", valid_model_name)
    
    if 'res_email' in st.session_state:
        st.markdown("---")
        st.markdown(st.session_state.res_email)

# --- 🕵️‍♂️ 背调 ---
elif selected_page == MENU["bg"]:
    st.header("🕵️‍♂️ Static Background Check")
    txt_input = st.text_area("Paste 'About Us' Text:", height=200)
    if st.button("🔍 Analyze Company"):
        if txt_input:
            with st.spinner('Profiling...'):
                prompt = "Analyze company text. Output: Identity, Scale, Pain Points, Pitch Strategy."
                st.markdown(robust_generate(f"{prompt}\nText: {txt_input}", valid_model_name))

# --- 🌐 联网搜索 ---
elif selected_page == MENU["search"]:
    st.header("🌐 Global Market Intelligence")
    query = st.text_input("Enter Company Name or Keyword:")
    if st.button("🌍 Deep Search", type="primary"):
        if query:
            with st.spinner('Searching global web...'):
                prompt = f"Role: Analyst. Search: '{query}'. Report: Identity, News, Competitors, Email Hook."
                data = robust_api_search({"contents":[{"parts":[{"text":prompt}]}],"tools":[{"google_search":{}}]}, valid_model_name, api_key)
                if "error" in data: st.error(data['error'])
                else:
                    try:
                        ans = data['candidates'][0]['content']['parts'][0]['text']
                        st.success("✅ Intelligence Retrieved")
                        st.markdown(ans)
                    except: st.error("Parsing failed.")

# --- ⛔ 谈判 ---
elif selected_page == MENU["neg"]:
    st.header("⛔ Negotiation & Objection Crusher")
    c1, c2 = st.columns(2)
    obj = c1.text_input("Client Objection:", placeholder="Price is too high")
    lev = c2.text_input("My Leverage (Optional):")
    
    if st.button("💣 Generate Strategy", type="primary"):
        if obj:
            with st.spinner('Consulting experts...'):
                prompt = f"{KB_INJECTION}\nNegotiation Coach. Objection: '{obj}'. Leverage: '{lev}'. Provide 3 strategies."
                st.markdown(robust_generate(prompt, valid_model_name))

# --- 🛠️ 售后 ---
elif selected_page == MENU["support"]:
    st.header("🛠️ Smart Technical Support")
    if mem_len < 50: st.warning("⚠️ Knowledge Base is empty. Upload PDFs in the sidebar first.")
    else: st.success("✅ Knowledge Base Active. Ask anything.")
    
    q = st.chat_input("Ask a question...")
    if q:
        with st.chat_message("user"): st.write(q)
        with st.chat_message("assistant"):
            with st.spinner('Checking docs...'):
                prompt = f"{KB_INJECTION}\nRole: Tech Support. Question: '{q}'. Answer strictly based on data."
                st.write(robust_generate(prompt, valid_model_name))
