import streamlit as st
import google.generativeai as genai
import requests
import json
import time
import pypdf
import os
from streamlit_option_menu import option_menu

# ==========================================
# 1. 核心配置与 SaaS 级 UI 引擎 (修复版)
# ==========================================
st.set_page_config(
    page_title="TradeNexus AI | 外贸销售专家", 
    page_icon="🦁", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 注入深度定制的 CSS (确保文字可见，背景深黑)
st.markdown("""
<style>
    /* 1. 全局背景：深空灰黑 */
    .stApp {
        background-color: #010409;
        color: #e6edf3;
    }
    
    /* 2. 侧边栏优化 */
    section[data-testid="stSidebar"] {
        background-color: #0d1117;
        border-right: 1px solid #30363d;
    }
    
    /* 3. 输入框：必须有边框和背景色，否则在黑底上看不见 */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        background-color: #161b22 !important;
        color: #ffffff !important;
        border: 1px solid #30363d !important;
        border-radius: 6px;
    }
    /* 聚焦时边框变蓝 */
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #2962ff !important;
        box-shadow: 0 0 0 1px #2962ff !important;
    }
    
    /* 4. 按钮：TradeNexus 同款电光蓝 */
    .stButton>button {
        background-color: #238636; /* 默认绿色 (类似GitHub Action) */
        color: white;
        border: 1px solid rgba(240,246,252,0.1);
        border-radius: 6px;
        font-weight: 600;
        height: 40px;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background-color: #2ea043;
        transform: scale(1.01);
    }
    
    /* 5. 隐藏 Streamlit 默认头部 */
    header {visibility: hidden;}
    
    /* 6. 结果卡片样式 */
    .result-box {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 20px;
        margin-top: 20px;
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
    return "⚠️ 网络繁忙，请稍后重试。"

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
# 3. 侧边栏 (⭐ 核心：模块化导航)
# ==========================================

with st.sidebar:
    st.markdown("### 🦁 **TradeNexus AI**")
    st.caption("B2B 外贸销售专家 | 工业级引擎")
    st.write("") 

    # ⭐ 导航模块：使用 styles 实现“方块”效果，无圆点
    selected = option_menu(
        menu_title=None, 
        options=[
            "综合面板 / 助手", 
            "开发信生成", 
            "客户背景调查", 
            "谈判策略", 
            "风控与合规", 
            "社媒内容引擎", 
            "订单复盘"
        ],
        # 使用方形/网格类图标增强“模块感”
        icons=["grid-fill", "envelope-fill", "search", "chat-quote-fill", "shield-check", "share-fill", "clipboard-data"], 
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#8b949e", "font-size": "14px"}, 
            # 导航项：像一个个独立的按钮模块
            "nav-link": {
                "font-size": "14px", 
                "text-align": "left", 
                "margin": "6px 0px", 
                "padding": "10px 15px",
                "background-color": "#161b22",  # 模块背景
                "border": "1px solid #30363d",  # 模块边框
                "border-radius": "6px",
                "color": "#c9d1d9"
            },
            # 选中状态：高亮蓝
            "nav-link-selected": {
                "background-color": "#1f6feb", 
                "color": "white",
                "border": "1px solid #1f6feb"
            },
        }
    )
    
    st.markdown("---")
    
    # 知识库区域
    st.markdown("**🧠 知识库状态**")
    current_mem = load_memory()
    mem_len = len(current_mem)
    
    if mem_len > 50:
        st.success(f"🟢 已加载 ({mem_len} 字符)")
    else:
        st.info("⚪ 暂无数据")

    with st.expander("📂 知识库管理", expanded=True):
        new_txt = st.text_area("粘贴文本:", height=80, placeholder="粘贴公司介绍...")
        if st.button("💾 保存"): 
            if new_txt: save_memory(new_txt); st.rerun()
        
        up_file = st.file_uploader("上传 PDF:", type=['pdf'])
        if up_file:
            try:
                reader = pypdf.PdfReader(up_file)
                txt = "".join([p.extract_text() or "" for p in reader.pages])
                if len(txt)>50: save_memory(txt); st.success("已保存"); time.sleep(1); st.rerun()
            except: st.error("读取失败")

    if st.button("🗑️ 清空知识库"): clear_memory(); st.rerun()

KB_INJECTION = f"[内部知识库数据]: {current_mem}" if mem_len > 50 else ""

# ==========================================
# 4. 主界面逻辑 (全功能复刻)
# ==========================================

# --- 1. 综合面板 / 助手 ---
if selected == "综合面板 / 助手":
    st.title("🚀 综合指挥中心")
    st.markdown("您的 AI 业务副驾驶。请直接下达指令或从下方快捷开始。")
    
    col1, col2, col3 = st.columns(3)
    # 快捷按钮
    with col1:
        if st.button("💡 欧洲市场趋势分析"):
            st.session_state.q = "分析 2026 欧洲机械市场的最新趋势与机会点"
    with col2:
        if st.button("💡 润色公司英文介绍"):
            st.session_state.q = "帮我润色这段公司介绍，使其更地道、专业：[请粘贴文本]"
    with col3:
        if st.button("💡 海运费/物流咨询"):
            st.session_state.q = "当前红海局势对中国出口欧洲的海运费有何影响？"

    st.markdown("---")
    
    # 聊天框
    if 'q' not in st.session_state: st.session_state.q = ""
    user_input = st.chat_input("输入指令...")
    
    if st.session_state.q: # 如果点了按钮
        user_input = st.session_state.q
        st.session_state.q = "" # 重置

    if user_input:
        with st.chat_message("user"): st.write(user_input)
        with st.chat_message("assistant"):
            with st.spinner('Thinking...'):
                res = robust_generate(f"{KB_INJECTION}\nUser: {user_input}", valid_model_name)
                st.markdown(res)

# --- 2. 开发信生成 ---
elif selected == "开发信生成":
    st.title("📧 客户开发 (Outreach)")
    
    c1, c2 = st.columns([1, 1])
    with c1:
        target = st.text_input("目标客户 (Who):", placeholder="例：德国汽车配件采购商")
    with c2:
        pain = st.text_input("客户痛点 (Why Us):", placeholder="例：原厂交期太慢，需要现货")
        
    if st.button("🚀 生成高转化开发信", use_container_width=True):
        if target:
            with st.spinner('撰写中...'):
                prompt = f"{KB_INJECTION}\n写一封B2B开发信。目标: {target}。痛点: {pain}。要求: 简短, 勾起兴趣, Call to action."
                res = robust_generate(prompt, valid_model_name)
                st.markdown(f'<div class="result-box">{res}</div>', unsafe_allow_html=True)
        else:
            st.warning("请填写目标客户信息")

# --- 3. 客户背景调查 ---
elif selected == "客户背景调查":
    st.title("🕵️‍♂️ 客户背调 (Intelligence)")
    query = st.text_input("输入公司名或网址:", placeholder="例如：Home Depot Procurement")
    
    if st.button("🔍 全网深度扫描", use_container_width=True):
        if query:
            with st.spinner('正在检索全球数据...'):
                prompt = f"Role: Analyst. Search: '{query}'. Report: 1.Identity 2.Decision Makers 3.News 4.Competitors."
                data = robust_api_search({"contents":[{"parts":[{"text":prompt}]}],"tools":[{"google_search":{}}]}, valid_model_name, api_key)
                if "error" in data: st.error(data['error'])
                else:
                    try:
                        ans = data['candidates'][0]['content']['parts'][0]['text']
                        st.markdown(f'<div class="result-box">{ans}</div>', unsafe_allow_html=True)
                    except: st.error("未找到信息")

# --- 4. 谈判策略 ---
elif selected == "谈判策略":
    st.title("⚖️ 谈判策略军师")
    obj = st.text_input("客户提出的异议:", placeholder="Price is too high / Delivery time is too long")
    
    if st.button("💣 生成回击话术", use_container_width=True):
        if obj:
            with st.spinner('军师思考中...'):
                res = robust_generate(f"{KB_INJECTION}\n谈判专家。客户说: {obj}。请提供3种回击策略(共情/逻辑/利益交换)。", valid_model_name)
                st.markdown(f'<div class="result-box">{res}</div>', unsafe_allow_html=True)

# --- 5. 风控与合规 ---
elif selected == "风控与合规":
    st.title("🛡️ 风控与合规")
    st.info("⚠️ 提示：此模块用于查询海关数据、信用黑名单及出口合规性检查。")
    st.markdown("当前处于演示模式，请手动输入公司名进行模拟查询。")
    risk_q = st.text_input("输入公司名进行风险扫描:")
    if st.button("🔍 扫描风险"):
        st.success("✅ 未发现该公司在制裁名单中。信用评分：A- (模拟数据)")

# --- 6. 社媒内容引擎 ---
elif selected == "社媒内容引擎":
    st.title("📱 社媒内容引擎")
    c1, c2 = st.columns([3, 1])
    with c1:
        topic = st.text_input("营销主题:", placeholder="例如：新款环保包装材料发布")
    with c2:
        plat = st.selectbox("发布平台:", ["LinkedIn (深度文)", "TikTok (脚本)", "Cold DM (私信)"])
        
    if st.button("✨ 生成多语言素材", use_container_width=True):
        if topic:
            with st.spinner('创作中...'):
                res = robust_generate(f"{KB_INJECTION}\n社媒专家。主题:{topic}。平台:{plat}。严格基于知识库生成内容。", valid_model_name)
                st.markdown(f'<div class="result-box">{res}</div>', unsafe_allow_html=True)

# --- 7. 订单复盘 ---
elif selected == "订单复盘":
    st.title("📊 订单复盘")
    st.info("请上传历史订单 Excel/CSV 表格，AI 将自动分析利润率、退货率及改进建议。")
    st.file_uploader("上传订单表格:", type=['csv', 'xlsx'])
