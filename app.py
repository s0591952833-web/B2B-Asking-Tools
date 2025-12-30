import streamlit as st
import google.generativeai as genai
import requests
import json
import time

# ==========================================
# 1. 核心配置
# ==========================================
st.set_page_config(page_title="外贸数字指挥官 (自动抗压版)", page_icon="🦁", layout="wide")

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ 未检测到 API Key，请配置 Secrets。")
    st.stop()

# ==========================================
# 2. 智能模型锁定 (修正版：把 2.5 加回来了!)
# ==========================================
@st.cache_resource
def get_best_model():
    # 你的账号特殊，优先检测 2.5，如果有限流风险，后续代码会处理
    candidates = [
        "models/gemini-2.5-flash",  # 你唯一的王牌
        "models/gemini-1.5-flash",  # 备选
        "models/gemini-pro"         # 老备选
    ]
    
    print("正在为您的账号寻找可用模型...")
    for model in candidates:
        try:
            m = genai.GenerativeModel(model)
            m.generate_content("test") 
            return model
        except:
            continue
            
    # 如果全挂了，还是返回 2.5 让他去试
    return "models/gemini-2.5-flash"

valid_model_name = get_best_model()

# ==========================================
# 3. 核心黑科技：自动重试机制 (解决限流问题)
# ==========================================
def robust_generate(prompt, model_name):
    """
    带重试机制的生成函数。
    如果遇到限流 (429)，自动等待并重试，不再报错。
    """
    model = genai.GenerativeModel(model_name)
    max_retries = 3
    
    for i in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            if "429" in str(e): # 如果是限流报错
                if i < max_retries - 1:
                    time.sleep(5) # 休息5秒
                    continue # 重试
                else:
                    return f"⚠️ 请求过于频繁，请稍等1分钟后再试。(系统已自动重试{max_retries}次)"
            else:
                return f"❌ 发生错误: {str(e)}"

def robust_api_search(payload, model_name, api_key):
    """
    带重试机制的联网搜索
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    max_retries = 3
    for i in range(max_retries):
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429: # 限流
                time.sleep(5) # 等待
                continue # 重试
            else:
                return {"error": f"API Error {response.status_code}: {response.text}"}
        except Exception as e:
            return {"error": str(e)}
    return {"error": "网络繁忙，请稍后再试。"}

# ==========================================
# 4. 侧边栏 (极简)
# ==========================================
st.sidebar.title("🦁 控制台")
app_mode = st.sidebar.radio("功能菜单：", [
    "📧 询盘分析", 
    "🕵️‍♂️ 文本背调", 
    "🌐 全网深挖 (联网)",
    "⛔ 谈判军师"
])
st.sidebar.markdown("---")
st.sidebar.caption(f"🚀 内核: `{valid_model_name.split('/')[-1]}`")
st.sidebar.caption("🛡️ 自动抗压系统：已开启")

# ==========================================
# 5. 功能实现
# ==========================================

# --- 功能一：询盘分析 ---
if app_mode == "📧 询盘分析":
    st.subheader("📧 深度询盘分析")
    user_input = st.text_area("粘贴邮件内容：", height=200)
    
    if 'email_res' not in st.session_state: st.session_state.email_res = None

    if st.button("🚀 分析"):
        if not user_input: st.warning("内容为空")
        else:
            with st.spinner('AI 正在分析 (若慢请稍等，正在自动排队)...'):
                PROMPT = "Act as Sales Manager. Analyze email. Output: Language, Intent, Score, Advice, Draft Response."
                # 使用抗压函数
                res_text = robust_generate(f"{PROMPT}\nInput: {user_input}", valid_model_name)
                st.session_state.email_res = res_text

    if st.session_state.email_res:
        st.markdown(st.session_state.email_res)

# --- 功能二：文本背调 ---
elif app_mode == "🕵️‍♂️ 文本背调":
    st.subheader("🕵️‍♂️ 网站文本分析")
    bg_input = st.text_area("粘贴 About Us 文本：", height=300)
    
    if 'bg_res' not in st.session_state: st.session_state.bg_res = None
        
    if st.button("🔍 分析"):
        if not bg_input: st.warning("内容为空")
        else:
            with st.spinner('分析中...'):
                PROMPT = "Analyze company text. Output: Identity, Scale, Pain Points, Pitch Strategy."
                res_text = robust_generate(f"{PROMPT}\nText: {bg_input}", valid_model_name)
                st.session_state.bg_res = res_text

    if st.session_state.bg_res:
        st.markdown(st.session_state.bg_res)

# --- 功能三：全网深挖 (联网) ---
elif app_mode == "🌐 全网深挖 (联网)":
    st.subheader("🌐 商业情报搜索")
    search_query = st.text_input("输入公司名/产品词：", placeholder="例如：Costco")
    
    if 'search_res' not in st.session_state: st.session_state.search_res = None
    
    if st.button("🌍 深度挖掘"):
        if not search_query: st.warning("请输入关键词")
        else:
            st.session_state.search_res = None
            with st.spinner('正在检索全网情报 (约需15秒)...'):
                prompt_text = f"""
                Role: Senior B2B Market Analyst.
                Task: Search for "{search_query}" and write a Deep-Dive Report.
                Output:
                1. 🏢 Real Identity (Factory/Distributor?)
                2. 🎯 Strategic Radar (Recent News/Expansions)
                3. 🛒 Procurement Preferences (Price vs Quality)
                4. ⚔️ Main Competitors
                5. ⚡ Cold Email Hook Sentence
                """
                
                payload = {
                    "contents": [{"parts": [{"text": prompt_text}]}],
                    "tools": [{"google_search": {}}]
                }
                
                # 使用抗压联网函数
                data = robust_api_search(payload, valid_model_name, api_key)
                
                if "error" in data:
                    st.error(data["error"])
                else:
                    try:
                        ans = data['candidates'][0]['content']['parts'][0]['text']
                        grounding = ""
                        try: grounding = data['candidates'][0]['groundingMetadata']['searchEntryPoint']['renderedContent']
                        except: pass
                        st.session_state.search_res = (grounding, ans)
                    except: st.error("搜索成功但解析失败，请重试。")

    if st.session_state.search_res:
        g, a = st.session_state.search_res
        if g: st.markdown(g, unsafe_allow_html=True)
        st.markdown(a)

# --- 功能四：谈判军师 ---
