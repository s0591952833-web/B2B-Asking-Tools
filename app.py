import streamlit as st
import google.generativeai as genai
import requests
import json
import time
import pypdf
import os
from streamlit_option_menu import option_menu

# ==========================================
# 1. 核心配置与 SaaS 极简深色 UI
# ==========================================
st.set_page_config(
    page_title="TradeNexus AI | B2B 外贸销售专家", 
    page_icon="🦁", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 注入 CSS (实现无圆点、模块化导航、高级黑金风)
st.markdown("""
<style>
    /* 1. 全局背景：深空灰黑 */
    .stApp {
        background-color: #0d1117; /* GitHub Dark Dimmed */
        color: #c9d1d9;
    }
    
    /* 2. 隐藏顶部红条 */
    header {visibility: hidden;}
    
    /* 3. 侧边栏优化：更深的背景，右侧分割线 */
    section[data-testid="stSidebar"] {
        background-color: #010409; /* 纯黑背景 */
        border-right: 1px solid #30363d;
        width: 300px !important;
    }
    
    /* 4. 输入框优化：极简扁平风格 */
    .stTextArea textarea, .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #0d1117 !important; 
        color: #e6edf3 !important;
        border: 1px solid #30363d !important;
        border-radius: 6px;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #58a6ff !important; /* 聚焦时变蓝 */
    }
    
    /* 5. 按钮优化：TradeNexus 风格的蓝色按钮 */
    .stButton>button {
        background-color: #238636; /* 绿色主按钮 */
        color: white;
        border: 1px solid rgba(240,246,252,0.1);
        border-radius: 6px;
        height: 40px;
        font-size: 14px;
        font-weight: 500;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background-color: #2ea043;
        border-color: #8b949e;
    }
    
    /* 6. 关键修复：隐藏 Option Menu 的图标间距，实现纯文字“模块感” */
    .nav-link .icon { 
        display: none !important; /* 强制隐藏图标 */
    }
    .nav-link {
        text-align: center !important; /* 文字居中 */
        padding-left: 0px !important;
        margin: 4px 0 !important;
        font-weight: 600 !important;
        letter-spacing: 1px;
    }
    
    /* 7. 标题样式 */
    h1, h2, h3 {
        color: #e6edf3 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    }
    
    /* 8. 知识库状态栏 */
    div[data-testid="metric-container"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 10px;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

MEMORY_FILE = "b2b_kb_memory.json"

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ API Key 未配置")
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
    max_retries = 3
    for i in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            if "429" in str(e): time.sleep((i+1)*5); continue
            else: time.sleep(2); continue
    return "⚠️ 网络繁忙，请重试。"

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
# 3. 侧边栏 (⭐ 模块化纯文字导航)
# ==========================================

# 顶部 Logo 区域
st.sidebar.markdown("### **TradeNexus AI**")
st.sidebar.caption("B2B 外贸销售专家 | 工业机械与零部件")
st.sidebar.write("")

# 导航菜单 (Option Menu 但隐藏图标)
with st.sidebar:
    selected = option_menu(
        None, # 不显示菜单标题
        [
            "综合面板 / 助手", 
            "开发信生成", 
            "客户背景调查", 
            "谈判策略", 
            "风控与合规", 
            "社媒内容引擎", 
            "订单复盘"
        ],
        icons=["circle", "circle", "circle", "circle", "circle", "circle", "circle"], # 图标设为 circle 但会被 CSS 隐藏
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            # 导航项样式：像按钮一样的模块
            "nav-link": {
                "font-size": "14px", 
                "text-align": "left", 
                "margin": "5px 0px", 
                "color": "#8b949e",
                "background-color": "#161b22", # 默认背景色
                "border": "1px solid #30363d",
                "border-radius": "6px",
                "height": "40px",
                "line-height": "40px",
                "padding-left": "15px" # 强制左对齐
            },
            # 选中项样式：高亮蓝紫色
            "nav-link-selected": {
                "background-color": "#1f6feb", # 选中的蓝色
                "color": "white",
                "border": "1px solid #1f6feb"
            },
        }
    )

st.sidebar.markdown("---")

# ⭐ 知识库管理区 (直接展开，不折叠)
st.sidebar.markdown("**📚 知识库配置**")
current_mem = load_memory()
mem_len = len(current_mem)

if mem_len > 50:
    st.sidebar.success(f"🟢 已加载 {mem_len} 字符")
else:
    st.sidebar.info("⚪ 知识库为空")

# 显眼的投喂入口
new_txt = st.sidebar.text_area("📄 粘贴文本:", height=80, placeholder="描述产品信息...")
if st.sidebar.button("💾 保存资料"): 
    if new_txt: save_memory(new_txt); st.rerun()

up_file = st.sidebar.file_uploader("📂 上传 PDF:", type=['pdf'])
if up_file:
    try:
        reader = pypdf.PdfReader(up_file)
        txt = "".join([p.extract_text() or "" for p in reader.pages])
        if len(txt)>50: save_memory(txt); st.success("已保存"); time.sleep(1); st.rerun()
    except: st.sidebar.error("读取失败")

if st.sidebar.button("🗑️ 清空知识库"): clear_memory(); st.rerun()

KB_INJECTION = f"[内部知识库数据]: {current_mem}" if mem_len > 50 else ""

# ==========================================
# 4. 主界面逻辑 (匹配新导航名)
# ==========================================

# --- 🏠 综合面板 ---
if selected == "综合面板 / 助手":
    st.title("综合助手")
    st.markdown("专为外贸任务设计的 AI 模块。上传知识库文件以获得更精准的定制建议。")
    
    # 快速开始按钮组
    c1, c2, c3 = st.columns(3)
    if c1.button("💡 制定欧洲市场开发计划"):
        pass # 这里可以联动
    if c2.button("💡 帮我优化这段公司介绍"):
        pass 
    if c3.button("💡 现在的海运费趋势如何"):
        pass

    st.markdown("---")
    # 对话框
    q = st.chat_input("输入客户信息、邮件内容或当前情况...")
    if q:
        with st.chat_message("user"): st.write(q)
        with st.chat_message("assistant"):
            with st.spinner('Thinking...'):
                st.write(robust_generate(f"{KB_INJECTION}\nUser: {q}", valid_model_name))

# --- 📧 开发信 ---
elif selected == "开发信生成":
    st.title("📧 开发信生成")
    col1, col2 = st.columns([2,1])
    with col1:
        target = st.text_input("描述目标客户 (国家, 行业, 职位):")
        pain = st.text_input("客户痛点:")
        if st.button("🚀 生成开发信"):
            with st.spinner('撰写中...'):
                prompt = f"{KB_INJECTION}\n写一封B2B开发信。目标: {target}。痛点: {pain}。要求: 简短, 勾起兴趣, Call to action."
                st.session_state.mail_res = robust_generate(prompt, valid_model_name)
    with col2:
        if 'mail_res' in st.session_state:
            st.info("生成结果:")
            st.markdown(st.session_state.mail_res)

# --- 🕵️‍♂️ 背调 ---
elif selected == "客户背景调查":
    st.title("🕵️‍♂️ 客户背景调查")
    query = st.text_input("输入客户网址或公司名:")
    if st.button("🔍 开始背调"):
        with st.spinner('全网搜索中...'):
            prompt = f"Role: Analyst. Search: '{query}'. Report: Identity, News, Competitors."
            data = robust_api_search({"contents":[{"parts":[{"text":prompt}]}],"tools":[{"google_search":{}}]}, valid_model_name, api_key)
            if "error" in data: st.error(data['error'])
            else:
                try: st.markdown(data['candidates'][0]['content']['parts'][0]['text'])
                except: st.error("无结果")

# --- ⛔ 谈判 ---
elif selected == "谈判策略":
    st.title("⚖️ 谈判策略")
    obj = st.text_input("客户提出的异议/压价:")
    if st.button("💣 生成回击话术"):
        st.write(robust_generate(f"{KB_INJECTION}\n谈判专家。客户说: {obj}。请提供3种回击策略。", valid_model_name))

# --- 📱 社媒 ---
elif selected == "社媒内容引擎":
    st.title("📱 社媒内容引擎")
    topic = st.text_input("营销主题:")
    plat = st.selectbox("平台:", ["LinkedIn", "TikTok", "Email"])
    if st.button("✨ 生成内容"):
        st.write(robust_generate(f"{KB_INJECTION}\n社媒专家。主题:{topic}。平台:{plat}。生成内容。", valid_model_name))

# --- 📦 订单/其他 ---
else:
    st.title(f"{selected}")
    st.info("该模块正在开发中...")
