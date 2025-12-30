import streamlit as st
import google.generativeai as genai
import requests
import json
import time

# ==========================================
# 1. 核心配置 (保持不变)
# ==========================================
st.set_page_config(page_title="外贸数字指挥官 (完美修复版)", page_icon="🦁", layout="wide")

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ 未检测到 API Key，请配置 Secrets。")
    st.stop()

# ==========================================
# 2. 智能模型锁定 (你只有 2.5，所以锁定它)
# ==========================================
@st.cache_resource
def get_best_model():
    # 既然刚才截图显示 2.5-flash 已连接，我们直接用它
    return "models/gemini-2.5-flash"

valid_model_name = get_best_model()

# ==========================================
# 3. 自动抗压函数 (防止报错 429)
# ==========================================
def robust_generate(prompt, model_name):
    model = genai.GenerativeModel(model_name)
    for i in range(3): # 自动重试 3 次
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            if "429" in str(e): # 如果限流
                time.sleep(5)   # 休息 5 秒
                continue        # 重试
            else:
                return f"❌ 错误: {str(e)}"
    return "⚠️ 系统繁忙，请稍后再试。"

def robust_api_search(payload, model_name, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    for i in range(3):
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                time.sleep(5)
                continue
            else:
                return {"error": f"Error {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    return {"error": "网络超时"}

# ==========================================
# 4. 侧边栏菜单 (⭐ 修复重点：统一变量)
# ==========================================
st.sidebar.title("🦁 控制台")

# 定义菜单选项列表，确保一一对应
MENU_OPTIONS = [
    "📧 询盘深度分析", 
    "🕵️‍♂️ 文本背调 (稳)", 
    "🌐 全网情报深挖 (联网)", 
    "⛔ 谈判与异议粉碎"
]

# 创建单选按钮
app_mode = st.sidebar.radio("功能选择：", MENU_OPTIONS)

st.sidebar.markdown("---")
st.sidebar.caption(f"🚀 核心引擎: `{valid_model_name.split('/')[-1]}`")
st.sidebar.caption("🛡️ 自动抗压: 已开启")

# ==========================================
# 5. 功能内容区 (保证不留白)
# ==========================================

# --- 功能一 ---
if app_mode == MENU_OPTIONS[0]: # 对应 "询盘深度分析"
    st.subheader("📧 深度询盘分析")
    st.info("💡 粘贴客户邮件，分析意图并生成回复。")
    user_input = st.text_area("粘贴邮件：", height=200)
    
    if 'res_1' not in st.session_state: st.session_state.res_1 = None
    if st.button("🚀 分析邮件"):
        if not user_input: st.warning("请粘贴内容")
        else:
            with st.spinner('正在分析...'):
                PROMPT = "Act as Sales Manager. Analyze email. Output: Language, Intent, Score, Advice, Draft Response."
                res = robust_generate(f"{PROMPT}\nInput: {user_input}", valid_model_name)
                st.session_state.res_1 = res
    if st.session_state.res_1: st.markdown(st.session_state.res_1)

# --- 功能二 ---
elif app_mode == MENU_OPTIONS[1]: # 对应 "文本背调"
    st.subheader("🕵️‍♂️ 网站文本分析")
    st.info("💡 复制 About Us 文本，快速了解客户背景。")
    bg_input = st.text_area("粘贴文本：", height=200)
    
    if 'res_2' not in st.session_state: st.session_state.res_2 = None
    if st.button("🔍 分析背景"):
        if not bg_input: st.warning("请粘贴内容")
        else:
            with st.spinner('分析中...'):
                PROMPT = "Analyze company text. Output: Identity, Scale, Pain Points, Pitch Strategy."
                res = robust_generate(f"{PROMPT}\nText: {bg_input}", valid_model_name)
                st.session_state.res_2 = res
    if st.session_state.res_2: st.markdown(st.session_state.res_2)

# --- 功能三 ---
elif app_mode == MENU_OPTIONS[2]: # 对应 "全网深挖"
    st.subheader("🌐 全网商业情报 (Google Search)")
    st.info("💡 输入公司名，挖掘官网看不到的深层信息。")
    query = st.text_input("公司名/关键词：")
    
    if 'res_3' not in st.session_state: st.session_state.res_3 = None
    if st.button("🌍 深度挖掘"):
        if not query: st.warning("请输入关键词")
        else:
            st.session_state.res_3 = None # 清空旧结果
            with st.spinner('正在全网检索 (约10-15秒)...'):
                prompt = f"""
                Role: Senior B2B Market Analyst.
                Task: Search for "{query}" and write a Deep-Dive Report.
                Output: 1. Real Identity 2. Latest News/Strategy 3. Procurement Prediction 4. Competitors 5. Cold Email Hook.
                """
                payload = {"contents": [{"parts": [{"text": prompt}]}], "tools": [{"google_search": {}}]}
                data = robust_api_search(payload, valid_model_name, api_key)
                
                if "error" in data: st.error(data["error"])
                else:
                    try:
                        ans = data['candidates'][0]['content']['parts'][0]['text']
                        grounding = ""
                        try: grounding = data['candidates'][0]['groundingMetadata']['searchEntryPoint']['renderedContent']
                        except: pass
                        st.session_state.res_3 = (grounding, ans)
                    except: st.error("解析失败，请重试")
    
    if st.session_state.res_3:
        g, a = st.session_state.res_3
        if g: st.markdown(g, unsafe_allow_html=True)
        st.markdown(a)

# --- 功能四 ---
elif app_mode == MENU_OPTIONS[3]: # 对应 "谈判与异议粉碎"
    st.subheader("⛔ 谈判与异议粉碎机")
    st.info("💡 客户嫌贵？嫌量大？让 AI 教你回击。")
    
    col1, col2 = st.columns(2)
    with col1: obj = st.text_input("客户拒绝理由:", placeholder="例如: Price is too high")
    with col2: lev = st.text_input("我的优势:", placeholder="例如: High quality")
    
    if 'res_4' not in st.session_state: st.session_state.res_4 = None
    if st.button("💣 生成谈判策略"):
        if not obj: st.warning("请输入拒绝理由")
        else:
            with st.spinner('军师正在思考...'):
                PROMPT = f"Negotiation Coach. Objection: {obj}. Context: {lev}. Provide 3 strategies (Value, Empathy, Alternative)."
                res = robust_generate(PROMPT, valid_model_name)
                st.session_state.res_4 = res
    if st.session_state.res_4: st.markdown(st.session_state.res_4)
