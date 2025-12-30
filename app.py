import streamlit as st
import google.generativeai as genai
import requests
import json

# ==========================================
# 1. 核心配置
# ==========================================
st.set_page_config(page_title="外贸数字指挥官 (全链路转化版)", page_icon="🦁", layout="wide")

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ 未检测到 API Key，请在 Streamlit 后台 Secrets 里配置。")
    st.stop()

# ==========================================
# 2. 模型锁定
# ==========================================
@st.cache_resource
def get_working_model_name():
    return "models/gemini-2.5-flash"

valid_model_name = get_working_model_name()

# ==========================================
# 3. 侧边栏
# ==========================================
st.sidebar.title("🦁 指挥官控制台")
app_mode = st.sidebar.radio("任务选择：", [
    "📧 询盘深度分析", 
    "🕵️‍♂️ 粘贴文本背调 (稳)", 
    "🌐 全网情报深挖 (联网版)",
    "⛔ 谈判与异议粉碎 (新!)"  # <--- 新增的选项
])
st.sidebar.markdown("---")
st.sidebar.success(f"🚀 引擎在线: `{valid_model_name}`")

# ==========================================
# 4. 功能逻辑
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
                    model = genai.GenerativeModel(valid_model_name)
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
                    model = genai.GenerativeModel(valid_model_name)
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
                    url = f"https://generativelanguage.googleapis.com/v1beta/{valid_model_name}:generateContent?key={api_key}"
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
                    else: st.error(f"请求失败 {response.status_code}")
                except Exception as e: st.error(f"错误: {e}")

# --- 功能四：谈判与异议粉碎 (⭐ 新增功能) ---
elif app_mode == "⛔ 谈判与异议粉碎 (新!)":
    st.title("⛔ B2B 谈判与异议粉碎机")
    st.info("💡 场景：客户回复了 '价格太贵'、'MOQ太高' 或 '已有供应商'。让 AI 教你如何优雅回击。")
    
    col1, col2 = st.columns(2)
    with col1:
        objection = st.text_input("客户的拒绝理由 (Objection):", placeholder="例如：Your price is 20% higher than my current supplier.")
    with col2:
        my_product = st.text_input("我的产品/优势 (可选):", placeholder="例如：We use 304 stainless steel, 2-year warranty.")
        
    if st.button("💣 生成谈判策略"):
        if not objection:
            st.warning("请至少输入客户的拒绝理由！")
        else:
            with st.spinner('谈判专家正在构思话术...'):
                try:
                    model = genai.GenerativeModel(valid_model_name)
                    PROMPT = f"""
                    You are a **World-Class B2B Sales Negotiation Coach** (Harvard Negotiation Project style).
                    
                    **The Situation:**
                    * **Client Objection:** "{objection}"
                    * **My Leverage (Context):** "{my_product}"
                    
                    **Your Task:**
                    Provide 3 distinct response strategies to handle this objection. Do not just apologize or lower the price immediately.
                    
                    **Output Format:**
                    
                    ### 🛡️ Strategy 1: The "Value Pivot" (Logic & ROI focus)
                    * **Logic:** Explain why the price is higher based on value/ROI.
                    * **Script (English):** [Draft email text]
                    
                    ### 🤝 Strategy 2: The "Empathy & Probe" (Psychological focus)
                    * **Logic:** Acknowledge their concern and ask a question to uncover the *real* blocker.
                    * **Script (English):** [Draft email text]
                    
                    ### 🔪 Strategy 3: The "Alternative Option" (Downsell/Unbundle)
                    * **Logic:** Offer a way to meet their price target by removing non-essential features/services.
                    * **Script (English):** [Draft email text]
                    
                    ---
                    **💡 Pro Tip:** One sentence advice on how to close this deal.
                    """
                    
                    response = model.generate_content(PROMPT)
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"出错: {e}")
