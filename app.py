import streamlit as st
import google.generativeai as genai
import requests
import json
import time
import pypdf
import os
from streamlit_option_menu import option_menu

# ==========================================
# 1. 核心配置与 TradeNexus 级 UI 引擎
# ==========================================
st.set_page_config(
    page_title="TradeNexus AI | 外贸销售专家", 
    page_icon="🦁", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 注入深度定制的 SaaS CSS
st.markdown("""
<style>
    /* 1. 全局色彩基调：深蓝黑背景，高对比度文字 */
    .stApp {
        background-color: #010409; /* 极深黑背景 */
    }
    
    /* 2. 侧边栏：独立的深色区块 */
    section[data-testid="stSidebar"] {
        background-color: #0D1117; /* 稍微亮一点的黑 */
        border-right: 1px solid #30363D;
    }
    
    /* 3. 输入框优化：卡片式，深灰底，亮白字 */
    .stTextArea textarea, .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #161B22 !important; 
        color: #E6EDF3 !important;
        border: 1px solid #30363D !important;
        border-radius: 6px;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #2962FF !important; /* 聚焦高亮蓝 */
        box-shadow: 0 0 0 1px #2962FF !important;
    }
    
    /* 4. 按钮优化：TradeNexus 同款电光蓝 */
    .stButton>button {
        background-color: #2962FF; /* 鲜艳的电光蓝 */
        color: white;
        border: none;
        border-radius: 6px;
        height: 42px;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.2s;
        width: 100%; /* 按钮撑满 */
    }
    .stButton>button:hover {
        background-color: #1E88E5;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(41, 98, 255, 0.4);
    }
    
    /* 5. 标题与文字颜色强制修正 */
    h1, h2, h3, h4, h5, h6 {
        color: #F0F6FC !important; /* 亮白标题 */
        font-family: 'Inter', system-ui, sans-serif;
    }
    p, label, span {
        color: #C9D1D9 !important; /* 灰白正文 */
    }
    
    /* 6. 隐藏顶部烦人的红线和菜单 */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    
    /* 7. 卡片容器样式 (用于结果展示) */
    .result-card {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 8px;
        padding: 20px;
        margin-top: 15px;
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
# 2. 逻辑内核 (保持不变，稳健第一)
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
# 3. 侧边栏 (⭐ 修复重点：SaaS 模块化导航)
# ==========================================

with st.sidebar:
    # 顶部品牌区
    st.markdown("### 🦁 **TradeNexus AI**")
    st.caption("B2B 外贸销售专家 | 工业级")
    st.markdown("---")

    # ⭐ 导航栏：使用 styles 参数实现“方块模块”效果
    # 这里的关键是 'nav-link' 的背景色和 margin，让它们看起来像独立的按钮
    selected = option_menu(
        menu_title=None, # 隐藏标题，更简洁
        options=[
            "综合助手 / 总控", 
            "开发信生成", 
            "客户背景调查", 
            "谈判策略", 
            "社媒内容引擎", 
            "风控与合规",
            "订单复盘"
        ],
        # 这里虽然有图标，但我们通过样式让它们看起来更像 SaaS 菜单
        icons=["grid", "envelope", "search", "chat-square-quote", "share", "shield-check", "clipboard-data"],
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#8b949e", "font-size": "14px"}, 
            # 导航项：深色方块，带边框
            "nav-link": {
                "font-size": "14px", 
                "text-align": "left", 
                "margin": "6px 0px", 
                "padding": "10px 15px",
                "background-color": "#161B22", 
                "border": "1px solid #30363D",
                "border-radius": "6px",
                "color": "#C9D1D9"
            },
            # 选中项：电光蓝高亮，白色文字
            "nav-link-selected": {
                "background-color": "#2962FF", 
                "color": "white",
                "border": "1px solid #2962FF"
            },
        }
    )

    st.markdown("---")

    # ⭐ 知识库区域：显眼的卡片设计
    st.markdown("**📚 知识库状态**")
    current_mem = load_memory()
    mem_len = len(current_mem)
    
    if mem_len > 50:
        st.success(f"🟢 已激活 ({mem_len} 字符)")
    else:
        st.info("⚪ 暂无数据")

    # 投喂入口 (直接展开)
    with st.expander("📥 导入数据", expanded=True):
        new_txt = st.text_area("粘贴文本:", height=80, placeholder="产品参数/公司介绍...")
        if st.button("💾 保存"): 
            if new_txt: save_memory(new_txt); st.rerun()
        
        up_file = st.file_uploader("或上传 PDF:", type=['pdf'])
        if up_file:
            try:
                reader = pypdf.PdfReader(up_file)
                txt = "".join([p.extract_text() or "" for p in reader.pages])
                if len(txt)>50: save_memory(txt); st.success("已保存"); time.sleep(1); st.rerun()
            except: st.error("失败")

    if st.button("🗑️ 清空知识库"): clear_memory(); st.rerun()

KB_INJECTION = f"[内部知识库数据]: {current_mem}" if mem_len > 50 else ""

# ==========================================
# 4. 主界面逻辑 (卡片式布局优化)
# ==========================================

# --- 🏠 综合助手 ---
if selected == "综合助手 / 总控":
    st.title("🚀 综合指挥中心")
    st.markdown("这里是您的 AI 业务副驾驶。选择下方快捷指令或直接对话。")
    
    # 快捷指令卡片
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("💡 **市场洞察**")
        if st.button("分析 2026 欧洲机械市场趋势"):
            q = "分析 2026 欧洲机械市场趋势"
            st.session_state.chat_q = q
    with col2:
        st.success("💡 **内容优化**")
        if st.button("润色这段公司介绍 (英文)"):
            q = "帮我润色这段公司介绍，使其更具国际范：[请粘贴文本]"
            st.session_state.chat_q = q
    with col3:
        st.warning("💡 **物流咨询**")
        if st.button("当前红海局势对海运的影响"):
            q = "当前红海局势对中国出口欧洲的海运费有何影响？"
            st.session_state.chat_q = q

    st.markdown("---")
    
    # 聊天式交互
    if 'chat_q' not in st.session_state: st.session_state.chat_q = ""
    
    user_q = st.chat_input("输入指令、客户邮件或任何问题...")
    # 处理点击按钮的情况
    if st.session_state.chat_q:
        user_q = st.session_state.chat_q
        st.session_state.chat_q = "" # 重置

    if user_q:
        with st.chat_message("user"): st.write(user_q)
        with st.chat_message("assistant"):
            with st.spinner('Thinking...'):
                res = robust_generate(f"{KB_INJECTION}\nUser: {user_q}", valid_model_name)
                st.write(res)

# --- 📧 开发信 ---
elif selected == "开发信生成":
    st.title("📧 客户开发 (Outreach)")
    
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown("**1. 目标客户画像**")
        target = st.text_input("描述客户:", placeholder="例如：德国汽车配件分销商，采购经理")
        
        st.markdown("**2. 核心痛点/价值**")
        pain = st.text_input("痛点:", placeholder="例如：现有供应商交期不稳定，寻求替代方案")
        
        if st.button("🚀 生成高转化开发信"):
            if not target: st.warning("请填写目标客户")
            else:
                with st.spinner('AI 正在撰写...'):
                    prompt = f"{KB_INJECTION}\n写一封B2B开发信。目标: {target}。痛点: {pain}。要求: 简短, 勾起兴趣, 无废话, Call to action."
                    st.session_state.mail_res = robust_generate(prompt, valid_model_name)
    
    with c2:
        st.markdown("**📝 生成结果**")
        if 'mail_res' in st.session_state:
            st.markdown(f'<div class="result-card">{st.session_state.mail_res}</div>', unsafe_allow_html=True)
        else:
            st.info("结果将显示在这里")

# --- 🕵️‍♂️ 背调 ---
elif selected == "客户背景调查":
    st.title("🕵️‍♂️ 客户背景调查 (Intelligence)")
    query = st.text_input("请输入客户公司名或网址:", placeholder="例如：Home Depot")
    
    if st.button("🔍 全网深度扫描"):
        if query:
            with st.spinner('正在分析数百万个网页...'):
                prompt = f"Role: Analyst. Search: '{query}'. Report: 1.Company Identity 2.Key Decision Makers 3.Recent News 4.Competitors."
                data = robust_api_search({"contents":[{"parts":[{"text":prompt}]}],"tools":[{"google_search":{}}]}, valid_model_name, api_key)
                
                if "error" in data: st.error(data['error'])
                else:
                    try:
                        ans = data['candidates'][0]['content']['parts'][0]['text']
                        st.markdown(f'<div class="result-card">{ans}</div>', unsafe_allow_html=True)
                    except: st.error("未找到相关信息")

# --- ⛔ 谈判 ---
elif selected == "谈判策略":
    st.title("⚖️ 谈判策略军师")
    
    c1, c2 = st.columns(2)
    with c1: 
        obj = st.text_input("客户提出的异议:", placeholder="Price is too high")
    with c2:
        lev = st.text_input("我方现有筹码:", placeholder="库存充足，24小时发货")
        
    if st.button("💣 生成回击话术"):
        if obj:
            with st.spinner('谈判专家思考中...'):
                res = robust_generate(f"{KB_INJECTION}\n谈判专家。客户说: {obj}。我方优势: {lev}。请提供3种回击策略(Empathetic, Logical, Aggressive)。", valid_model_name)
                st.markdown(f'<div class="result-card">{res}</div>', unsafe_allow_html=True)

# --- 📱 社媒 ---
elif selected == "社媒内容引擎":
    st.title("📱 社媒内容引擎")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        topic = st.text_input("营销主题:", placeholder="例如：新产品发布 / 展会预告")
    with col2:
        plat = st.selectbox("发布平台:", ["LinkedIn (深度文)", "TikTok (脚本)", "Instagram (图文)", "Cold DM (私信)"])
        
    if st.button("✨ 生成多语言素材"):
        if topic:
            with st.spinner('创作中...'):
                res = robust_generate(f"{KB_INJECTION}\n社媒专家。主题:{topic}。平台:{plat}。生成内容。严格基于知识库。", valid_model_name)
                st.markdown(f'<div class="result-card">{res}</div>', unsafe_allow_html=True)

# --- 其他模块 ---
elif selected == "风控与合规":
    st.title("🛡️ 风控与合规")
    st.info("此模块将连接海关数据与信用保险数据库 (Demo阶段暂未开放 API)")
    
elif selected == "订单复盘":
    st.title("📊 订单复盘")
    st.info("请上传历史订单 Excel 表格进行分析。")
