import streamlit as st
import google.generativeai as genai
import requests
import json
import time
import pypdf
import os
from streamlit_option_menu import option_menu

# ==========================================
# 1. 核心配置与 SaaS 深色 UI (增强对比度)
# ==========================================
st.set_page_config(
    page_title="外贸数字指挥官 | Global Command Center", 
    page_icon="🦁", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 注入 CSS (增强左侧输入框可见性)
st.markdown("""
<style>
    /* 全局深色背景 */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* 隐藏顶部红条 */
    header {visibility: hidden;}
    
    /* 左侧侧边栏背景 */
    section[data-testid="stSidebar"] {
        background-color: #161B22;
        border-right: 1px solid #30363D;
    }
    
    /* 核心修改：输入框背景加深，边框变亮，防止“看不见” */
    .stTextArea textarea, .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #0d1117 !important; 
        color: #e6edf3 !important;
        border: 1px solid #7d8590 !important; /* 亮灰色边框 */
        border-radius: 6px;
    }
    
    /* 按钮优化：高亮蓝紫渐变 */
    .stButton>button {
        background: linear-gradient(90deg, #238636 0%, #2ea043 100%); /* 类似 GitHub 的绿色按钮，更显眼 */
        color: white;
        border: none;
        border-radius: 6px;
        height: 3em;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(46, 160, 67, 0.4);
    }

    /* 状态提示框优化 */
    div[data-baseweb="notification"] {
        border-radius: 8px;
        font-weight: bold;
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
# 3. 侧边栏 (⭐ 找回“对话框”感觉)
# ==========================================

# 顶部品牌
st.sidebar.markdown("### 🦁 **外贸数字指挥官**")
st.sidebar.caption(f"🚀 引擎: {valid_model_name.split('/')[-1]} | 🟢 在线")
st.sidebar.write("") 

# 导航菜单
with st.sidebar:
    selected = option_menu(
        "系统导航",
        [
            "总控仪表盘", 
            "全域社媒营销", 
            "深度询盘分析", 
            "全球情报深挖", 
            "客户背景背调", 
            "谈判策略军师", 
            "智能技术支持"
        ],
        icons=["speedometer2", "phone", "envelope", "globe", "person-check", "chat-dots", "tools"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#161B22"},
            "icon": {"color": "#8b949e", "font-size": "16px"}, 
            "nav-link": {"font-size": "14px", "text-align": "left", "margin":"0px", "color": "#e6edf3"},
            "nav-link-selected": {"background-color": "#238636", "color": "white"}, # 选中绿色高亮
        }
    )

st.sidebar.markdown("---")

# ⭐ 修复点：找回显眼的状态框 (Success/Info Box)
current_mem = load_memory()
mem_len = len(current_mem)

if mem_len > 50:
    st.sidebar.success(f"🧠 知识库已激活\n\n包含 {mem_len} 字符")
else:
    st.sidebar.info("🧠 知识库空闲中\n\n请在下方投喂资料")

# ⭐ 修复点：默认展开输入区域，让输入框直接可见
with st.sidebar.expander("📥 投喂/管理数据", expanded=True):
    new_txt = st.text_area("粘贴文本资料:", height=100, placeholder="在此粘贴产品参数...")
    if st.button("💾 保存到记忆"): 
        if new_txt: save_memory(new_txt); st.rerun()
    
    st.write("---")
    up_file = st.file_uploader("或上传 PDF:", type=['pdf'])
    if up_file:
        try:
            reader = pypdf.PdfReader(up_file)
            txt = "".join([p.extract_text() or "" for p in reader.pages])
            if len(txt)>50: save_memory(txt); st.success("已保存"); time.sleep(1); st.rerun()
            else: st.error("PDF 无文字")
        except: st.error("读取失败")

    st.write("---")
    if st.button("🗑️ 清空记忆"): clear_memory(); st.rerun()

KB_INJECTION = f"[内部知识库数据]: {current_mem}" if mem_len > 50 else ""

# ==========================================
# 4. 主界面逻辑
# ==========================================

# --- 🏠 仪表盘 ---
if selected == "总控仪表盘":
    st.title("🚀 指挥官总控台")
    st.markdown("欢迎回来，这里是您的全球业务增长引擎。")
    
    # 指标卡片
    col1, col2, col3 = st.columns(3)
    col1.metric("目标市场", "Global / B2B", "Active")
    col2.metric("社媒引擎", "Ready", "New")
    col3.metric("知识资产", f"{mem_len} Char", "Loaded")
    
    st.markdown("---")
    
    # 功能入口卡片
    c1, c2 = st.columns(2)
    with c1:
        st.info("📱 **全域社媒营销**\n\n一键生成多平台爆款内容。")
        st.success("🌐 **全球情报深挖**\n\n实时连接 Google 搜索。")
    with c2:
        st.warning("⛔ **谈判策略军师**\n\n针对性回击客户压价。")
        st.error("🛠️ **智能技术支持**\n\n基于知识库回答技术问题。")

# --- 📱 社媒营销 ---
elif selected == "全域社媒营销":
    st.title("📱 全域社媒营销引擎")
    col_input, col_opt = st.columns([3, 1])
    with col_input:
        campaign_topic = st.text_input("📢 营销主题 / 产品焦点:", placeholder="例如：新款环保材料发布")
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
        st.caption("AI 分析意图并生成回复。")
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
    if mem_len < 50: st.warning("请先在左侧上传 PDF 手册。")
    else: st.success("✅ 知识库已就绪，请提问。")
    q = st.chat_input("输入关于产品的问题...")
    if q:
        with st.chat_message("user"): st.write(q)
        with st.chat_message("assistant"):
            with st.spinner('查询中...'):
                st.write(robust_generate(f"{KB_INJECTION}\n技术支持。问题: '{q}'。基于知识库回答。", valid_model_name))
