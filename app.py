import streamlit as st
import google.generativeai as genai
import requests
import json

# ==========================================
# 1. 核心配置
# ==========================================
st.set_page_config(page_title="外贸数字指挥官 (双引擎版)", page_icon="🦁", layout="wide")

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ 未检测到 API Key，请在 Streamlit 后台 Secrets 里配置。")
    st.stop()

# ==========================================
# 2. 侧边栏 & 模型选择 (⭐ 核心升级)
# ==========================================
st.sidebar.title("🦁 指挥官控制台")

# 新增：手动切换模型，防止一个被限流导致全挂
model_choice = st.sidebar.selectbox(
    "⚙️ 切换 AI 引擎 (报错时请换一个):",
    ["models/gemini-2.5-flash", "models/gemini-1.5-flash", "models/gemini-1.5-pro"]
)

st.sidebar.success(f"🚀 当前引擎: `{model_choice}`")
st.sidebar.markdown("---")

app_mode = st.sidebar.radio("任务选择：", [
    "📧 询盘深度分析", 
    "🕵️‍♂️ 粘贴文本背调 (稳)", 
    "🌐 全网情报深挖 (联网版)",
    "⛔ 谈判与异议粉碎 (新!)"
])

# ==========================================
# 3. 功能逻辑
# ==========================================

# --- 功能一：询盘分析 ---
if app_mode == "📧 询盘深度分析":
    st.title("📧 深度询盘分析")
    user_input = st.text_area("请粘贴客户邮件：", height=200)
    if st.button("🚀 开始分析"):
        if not user_input:
            st.warning("请输入内容")
        else:
            with st.spinner('AI 正在分析...'):
                try:
                    model = genai.GenerativeModel(model_choice) # 使用你选的模型
                    PROMPT = "Act as Sales Manager. Analyze email. Output: Language, Intent, Score, Advice, Draft Response."
                    response = model.generate_content(f"{PROMPT}\nInput: {user_input}")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"出错: {e}")

# --- 功能二：文本背调 ---
elif app_mode == "🕵️‍♂️ 粘贴文本背调 (稳)":
    st.title("🕵️‍♂️ 静态背景侦探")
    bg_input = st.text_area("请粘贴网站文本：", height=300)
    if st.button("🔍 开始侦查"):
        if not bg_input:
            st.warning("请粘贴文本")
        else:
            with st.spinner('侦探正在分析...'):
                try:
                    model = genai.GenerativeModel(model_choice) # 使用你选的模型
                    PROMPT = "Analyze company text. Output: Identity, Scale, Pain Points, Pitch Strategy."
                    response = model.generate_content(f"{PROMPT}\nText: {bg_input}")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"出错: {e}")

# --- 功能三：全网深挖 ---
elif app_mode == "🌐 全网情报深挖 (联网版)":
    st.title("🌐 全网深度商业情报 (Google Search)")
    search_query = st.text_input("输入客户公司名：", placeholder="例如：Costco Wholesale")
    
    if st.button("🌍 启动深度挖掘"):
        if not search_query:
            st.warning("请输入公司名！")
        else:
            with st.spinner('正在全网搜集情报...'):
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/{model_choice}:generateContent?key={api_key}"
                    payload = {
                        "contents": [{
                            "parts": [{
                                "text": f"""
                                I want you to act as a Senior B2B Market Intelligence Analyst.
                                Search info about: "{search_query}".
                                Report: 1. Business DNA 2. Strategic Radar (Latest News/Pain Points) 3. Procurement Prediction 4. Competitors 5. Cold Email Hook.
                                """
                            }]
                        }],
                        "tools": [{"google_search": {}}]
                    }
                    headers = {'Content-Type': 'application/json'}
                    response = requests.post(url, headers=headers, data=json.dumps(payload))
                    if response.status_code == 200:
                        result = response.json()
                        try:
                            answer = result['candidates'][0]['content']['parts'][0]['text']
                            try:
                                grounding = result['candidates'][0]['groundingMetadata']['searchEntryPoint']['renderedContent']
                                st.success("✅ 搜索完成")
                                st.markdown(grounding, unsafe_allow_html=True)
                            except: pass
                            st.markdown(answer)
                        except: st.error("数据解析失败")
                    else: st.error(f"请求失败 {response.status_code}\n{response.text}")
                except Exception as e: st.error(f"错误: {e}")

# --- 功能四：谈判与异议粉碎 ---
elif app_mode == "⛔ 谈判与异议粉碎 (新!)":
    st.title("⛔ B2B 谈判与异议粉碎机")
    
    col1, col2 = st.columns(2)
    with col1:
        objection = st.text_input("客户的拒绝理由:", placeholder="例如：Price is too high.")
    with col2:
        my_product = st.text_input("我的优势:", placeholder="例如：High quality, 2 year warranty.")
        
    if st.button("💣 生成谈判策略"):
        if not objection:
            st.warning("请输入客户的拒绝理由")
        else:
            with st.spinner('谈判专家正在构思...'):
                try:
                    model = genai.GenerativeModel(model_choice) # 使用你选的模型
                    PROMPT = f"""
                    You are a B2B Sales Negotiation Coach.
                    Objection: "{objection}"
                    My Context: "{my_product}"
                    Provide 3 strategies (Value Pivot, Empathy, Alternative) with email scripts.
                    """
                    response = model.generate_content(PROMPT)
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"出错: {e}")
                    st.caption("💡 提示：如果显示 429 Quota Exceeded，请在左侧侧边栏切换另一个模型试试！")
