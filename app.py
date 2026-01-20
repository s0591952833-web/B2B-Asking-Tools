import streamlit as st
import google.generativeai as genai
import requests
import json
import time
import pypdf
import os
from streamlit_option_menu import option_menu  # 引入高级导航库

# ==========================================
# 1. 核心配置与 SaaS 深色 UI
# ==========================================
st.set_page_config(
    page_title="外贸数字指挥官 | Global Command Center", 
    page_icon="🦁", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 注入 CSS (针对新导航栏微调)
st.markdown("""
<style>
    /* 全局深色背景 */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* 隐藏 Streamlit 默认的顶部红条和菜单 */
    header {visibility: hidden;}
    
    /* 输入框优化 */
    .stTextArea textarea, .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #21262D !important;
        color: #FFFFFF !important;
        border: 1px solid #30363D;
    }
    
    /* 按钮优化 */
    .stButton>button {
        background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 100%);
        color: white;
        border: none;
        border-radius: 8px;
        height: 3em;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        box-shadow: 0 4px 15px rgba(124, 58, 237, 0.4);
        transform: translateY(-2px);
    }
    
    /* 标题优化 */
    h1, h2, h3 {
        color: #FFFFFF !important;
        font-family: 'PingFang SC', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

MEMORY_FILE = "b2b_kb_memory.json"

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ 系统错误: API Key 未配置")
    st.stop()

# ==========================================
# 2. 逻辑内核
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
    model = genai.GenerativeModel(model_name)
    max_retries = 5
    for i in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            if "429" in str(e): time.sleep((i+1)*5); continue
            else: time.sleep(2); continue
    return "⚠️ 网络繁忙，请稍后重试。"

def robust_api_search(payload, model_name, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    for i in range(3):
        try:
            res = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
            if res.status_code == 200: return res.json()
            elif res.status_code == 429: time.sleep(5); continue
            else: return {"error": f"错误 {res.status_code}"}
        except Exception as e: return {"error": str(e)}
    return {"error": "请求超时"}

# ==========================================
# 3. 侧边栏 (⭐ UI 核心升级：Option Menu)
# ==========================================

# 侧边栏顶部品牌区
st.sidebar.markdown("### 🦁 **外贸数字指挥官**")
st.sidebar.caption(f"🚀 引擎: {valid_model_name.split('/')[-1]} | 🟢 在线")
st.sidebar.write("") # 占位符

# ⭐ 这里使用了新的 option_menu 组件，替换了原来的 radio
with st.sidebar:
    selected = option_menu(
        "系统导航",  # 菜单标题 (可留空)
        [
            "总控仪表盘", 
            "全域社媒营销", 
            "深度询盘分析", 
            "全球情报深挖", 
            "客户背景背调", 
            "谈判策略军师", 
            "智能技术支持"
        ],
        icons=[
            "speedometer2", # 仪表盘图标
            "phone",        # 社媒图标
            "envelope",     # 邮件图标
            "globe",        # 地球图标
            "person-check", # 背调图标
            "chat-dots",    # 谈判图标
            "tools"         # 技术支持图标
        ],
        menu_icon="cast",   # 菜单左上角图标
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#161B22"},
            "icon": {"color": "#4F46E5", "font-size": "18px"}, 
            "nav-link": {"font-size": "15px", "text-align": "left", "margin":"0px", "--hover-color": "#21262D"},
            "nav-link-selected": {"background-color": "#4F46E5"},
        }
    )

# 知识库状态区 (保持在下方)
st.sidebar.markdown("---")
current_mem = load_memory()
mem_len = len(current_mem)
kb_status = "🟢 已激活" if mem_len > 50 else "⚪ 空闲中"
st.sidebar.metric("🧠 企业知识库", kb_status, f"{mem_len} 字符")

with st.sidebar.expander("📂 知识库管理"):
    new_txt = st.text_area("粘贴资料:", height=100)
    if st.button("💾 保存文本"): 
        if new_txt: save_memory(new_txt); st.rerun()
    
    up_file = st.file_uploader("上传 PDF:", type=['pdf'])
    if up_file:
        try:
            reader = pypdf.PdfReader(up_file)
            txt = "".join([p.extract_text() or "" for p in reader.pages])
            if len(txt)>50: save_memory(txt); st.success("已保存"); time.sleep(1); st.rerun()
            else: st.error("PDF 无文字内容")
        except: st.error("读取失败")

    if st.button("🗑️ 清空记忆"): clear_memory(); st.rerun()

KB_INJECTION = f"[内部知识库数据]: {current_mem}" if mem_len > 50 else ""

# ==========================================
# 4. 主界面逻辑 (映射新菜单名称)
# ==========================================

# --- 🏠 仪表盘 ---
if selected == "总控仪表盘":
    st.title("🚀 指挥官总控台")
    st.markdown("欢迎回来，这里是您的全球业务增长引擎。")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("目标市场", "全球 / B2B", "Active")
    c2.metric("社媒引擎", "已就绪", "New")
    c3.metric("知识资产", f"{mem_len} 字符", "Loaded")
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.info("📱 **全域社媒营销**\n\n一键生成 LinkedIn 深度文、TikTok 脚本及开发信。")
        st.success("🌐 **全球情报深挖**\n\n实时连接 Google 搜索，挖掘隐秘信息。")
    with col2:
        st.warning("⛔ **谈判策略军师**\n\n哈佛谈判专家视角，提供回击话术。")
        st.error("🛠️ **智能技术支持**\n\n基于 PDF 手册自动回答技术问题。")

# --- 📱 社媒营销 ---
elif selected == "全域社媒营销":
    st.title("📱 全域社媒营销引擎")
    col_input, col_opt = st.columns([3, 1])
    with col_input:
        campaign_topic = st.text_input("📢 营销主题 / 产品焦点:", placeholder="例如：新款 X500 发布")
    with col_opt:
        platform = st.selectbox("发布平台:", ["👔 LinkedIn (专业领袖)", "🎥 TikTok/IG (视频脚本)", "🤝 Cold DM (私信)"])
    
    if st.button("🚀 生成素材"):
        if not campaign_topic: st.warning("请输入主题")
        else:
            with st.spinner('AI 撰写中...'):
                prompt = f"{KB_INJECTION}\n角色:社媒专家。主题: '{campaign_topic}'。平台: {platform}。规则: LinkedIn用Hook结构; TikTok用脚本表格; DM要简短。严格基于知识库。"
                st.session_state.social_res = robust_generate(prompt, valid_model_name)
    if 'social_res' in st.session_state: st.markdown("---"); st.markdown(st.session_state.social_res)

# --- 📧 询盘分析 ---
elif selected == "深度询盘分析":
    st.title("📧 深度询盘分析")
    c1, c2 = st.columns([2, 1])
    with c1: user_input = st.text_area("粘贴客户邮件:", height=300)
    with c2: 
        st.info("AI 分析意图并生成回复。")
        if st.button("🚀 开始分析"):
            if user_input:
                with st.spinner('分析中...'):
                    prompt = f"{KB_INJECTION}\n销售总监。分析邮件: {user_input}。输出: 意图, 评分, 建议, 回复(中英)。"
                    st.session_state.res_email = robust_generate(prompt, valid_model_name)
    if 'res_email' in st.session_state: st.markdown("---"); st.markdown(st.session_state.res_email)

# --- 🌐 搜情报 ---
elif selected == "全球情报深挖":
    st.title("🌐 全球市场情报")
    query = st.text_input("客户公司名 / 关键词:")
    if st.button("🌍 深度挖掘"):
        if query:
            with st.spinner('检索中...'):
                prompt = f"Role: Analyst. Search: '{query}'. Report: Identity, News, Competitors, Hook."
                data = robust_api_search({"contents":[{"parts":[{"text":prompt}]}],"tools":[{"google_search":{}}]}, valid_model_name, api_key)
                if "error" in data: st.error(data['error'])
                else:
                    try:
                        ans = data['candidates'][0]['content']['parts'][0]['text']
                        st.success("✅ 获取成功"); st.markdown(ans)
                    except: st.error("解析失败")

# --- 🕵️‍♂️ 背调 ---
elif selected == "客户背景背调":
    st.title("🕵️‍♂️ 客户背景静态分析")
    txt_input = st.text_area("粘贴 About Us 文本:", height=200)
    if st.button("🔍 生成画像"):
        if txt_input:
            with st.spinner('分析中...'):
                st.markdown(robust_generate(f"分析公司文本: {txt_input}。输出: 模式, 规模, 痛点, 策略。", valid_model_name))

# --- ⛔ 谈判 ---
elif selected == "谈判策略军师":
    st.title("⛔ 谈判与异议粉碎机")
    c1, c2 = st.columns(2)
    obj = c1.text_input("拒绝理由:")
    lev = c2.text_input("我方筹码:")
    if st.button("💣 生成策略"):
        if obj:
            with st.spinner('思考中...'):
                st.markdown(robust_generate(f"{KB_INJECTION}\n谈判专家。拒绝: '{obj}'。优势: '{lev}'。提供3个回击策略。", valid_model_name))

# --- 🛠️ 售后 ---
elif selected == "智能技术支持":
    st.title("🛠️ 智能技术支持")
    if mem_len < 50: st.warning("请先上传产品手册 PDF。")
    else: st.success("✅ 知识库已就绪，请提问。")
    q = st.chat_input("输入关于产品的问题...")
    if q:
        with st.chat_message("user"): st.write(q)
        with st.chat_message("assistant"):
            with st.spinner('查询中...'):
                st.write(robust_generate(f"{KB_INJECTION}\n技术支持。问题: '{q}'。基于知识库回答。", valid_model_name))
