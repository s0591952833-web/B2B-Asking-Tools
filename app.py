import streamlit as st
import google.generativeai as genai
import requests
import json

# ==========================================
# 1. 核心配置
# ==========================================
st.set_page_config(page_title="外贸数字指挥官 (防封号稳健版)", page_icon="🛡️", layout="wide")

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ 未检测到 API Key，请在 Streamlit 后台 Secrets 里配置。")
    st.stop()

# ==========================================
# 2. 侧边栏 & 状态初始化
# ==========================================
st.sidebar.title("🦁 指挥官控制台")

# ⚠️ 建议：如果 2.5 一直报错，请在这里手动选 1.5-flash，它通常更耐用
model_choice = st.sidebar.selectbox(
    "⚙️ AI 引擎选择 (报错请切换):",
    ["models/gemini-2.5-flash", "models/gemini-1.5-flash"]
)

app_mode = st.sidebar.radio("任务选择：", [
    "📧 询盘深度分析", 
    "🕵️‍♂️ 粘贴文本背调 (稳)", 
    "🌐 全网情报深挖 (联网版)",
    "⛔ 谈判与异议粉碎"
])

st.sidebar.info(f"🛡️ 当前模式：结果自动缓存\n🚀 引擎：{model_choice}")

# ==========================================
# 3. 核心功能函数 (带缓存逻辑)
# ==========================================

# 通用请求函数，用来处理所有 AI 调用
def ask_ai(payload, api_url):
    headers = {'Content-Type': 'application/json'}
    response = requests.post(api_url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        return response.json()
    else:
        # 如果报错，直接抛出异常，让外层捕获
        raise Exception(f"Google 拒绝了请求: {response.text}")

# ==========================================
# 4. 界面逻辑
# ==========================================

# --- 功能一：询盘分析 ---
if app_mode == "📧 询盘深度分析":
    st.title("📧 深度询盘分析")
    user_input = st.text_area("请粘贴客户邮件：", height=200)
    
    # 检查 Session State 里有没有存旧结果，防止页面刷新丢失
    if 'email_result' not in st.session_state:
        st.session_state.email_result = None

    if st.button("🚀 开始分析"):
        if not user_input:
            st.warning("请输入内容")
        else:
            with st.spinner('AI 正在思考...'):
                try:
                    model = genai.GenerativeModel(model_choice)
                    PROMPT = "Act as Sales Manager. Analyze email. Output: Language, Intent, Score, Advice, Draft Response."
                    response = model.generate_content(f"{PROMPT}\nInput: {user_input}")
                    # ✅ 保存结果到“内存”
                    st.session_state.email_result = response.text
                except Exception as e:
                    st.error(f"出错: {e}")

    # 如果内存里有结果，直接显示（不消耗额度）
    if st.session_state.email_result:
        st.success("✅ 分析完成 (已缓存)")
        st.markdown(st.session_state.email_result)

# --- 功能二：文本背调 ---
elif app_mode == "🕵️‍♂️ 粘贴文本背调 (稳)":
    st.title("🕵️‍♂️ 静态背景侦探")
    bg_input = st.text_area("请粘贴网站文本：", height=300)
    
    if 'bg_result' not in st.session_state:
        st.session_state.bg_result = None
        
    if st.button("🔍 开始侦查"):
        if not bg_input:
            st.warning("请粘贴文本")
        else:
            with st.spinner('侦探正在分析...'):
                try:
                    model = genai.GenerativeModel(model_choice)
                    PROMPT = "Analyze company text. Output: Identity, Scale, Pain Points, Pitch Strategy."
                    response = model.generate_content(f"{PROMPT}\nText: {bg_input}")
                    st.session_state.bg_result = response.text
                except Exception as e:
                    st.error(f"出错: {e}")

    if st.session_state.bg_result:
        st.success("✅ 报告已生成 (已缓存)")
        st.markdown(st.session_state.bg_result)

# --- 功能三：全网深挖 (重灾区优化) ---
elif app_mode == "🌐 全网情报深挖 (联网版)":
    st.title("🌐 全网深度商业情报")
    st.caption("💡 提示：此功能消耗额度较大。如果 2.5 版报错，请左侧切换 1.5 版。")
    
    search_query = st.text_input("输入客户公司名：", placeholder="例如：Costco Wholesale")
    
    # 专门为搜索结果设置缓存
    if 'search_result' not in st.session_state:
        st.session_state.search_result = None
    
    if st.button("🌍 启动深度挖掘"):
        if not search_query:
            st.warning("请输入公司名！")
        else:
            # 只有点击按钮时，才清空旧结果，强制开始新搜索
            st.session_state.search_result = None 
            
            with st.spinner('正在全网搜集情报...'):
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/{model_choice}:generateContent?key={api_key}"
                    payload = {
                        "contents": [{
                            "parts": [{
                                "text": f"""
                                Act as B2B Market Analyst. Search for: "{search_query}".
                                Report: 1. Business DNA 2. Strategic Radar 3. Procurement Prediction 4. Competitors 5. Cold Email Hook.
                                """
                            }]
                        }],
                        "tools": [{"google_search": {}}]
                    }
                    
                    # 调用 API
                    data = ask_ai(payload, url)
                    
                    # 解析结果
                    try:
                        ans = data['candidates'][0]['content']['parts'][0]['text']
                        # 尝试获取来源
                        grounding = ""
                        try:
                            grounding = data['candidates'][0]['groundingMetadata']['searchEntryPoint']['renderedContent']
                        except: pass
                        
                        # ✅ 存入缓存
                        st.session_state.search_result = (grounding, ans)
                        
                    except:
                        st.error("AI 返回数据异常，请重试。")
                        
                except Exception as e:
                    st.error(f"❌ 请求失败: {str(e)}")
                    st.warning("💡 建议：请等待 1 分钟后再试，或者在左侧切换为 'gemini-1.5-flash'。")

    # 显示缓存的结果
    if st.session_state.search_result:
        grounding_html, answer_text = st.session_state.search_result
        if grounding_html:
            st.success("✅ 搜索完成")
            st.markdown(grounding_html, unsafe_allow_html=True)
        st.markdown(answer_text)

# --- 功能四：谈判 (缓存优化) ---
elif app_mode == "⛔ 谈判与异议粉碎":
    st.title("⛔ B2B 谈判与异议粉碎机")
    
    if 'neg_result' not in st.session_state:
        st.session_state.neg_result = None

    col1, col2 = st.columns(2)
    with col1:
        objection = st.text_input("客户拒绝理由:", placeholder="Price is too high")
    with col2:
        my_product = st.text_input("我的优势:", placeholder="Good quality")
        
    if st.button("💣 生成策略"):
        if not objection:
            st.warning("请输入理由")
        else:
            with st.spinner('构思中...'):
                try:
                    model = genai.GenerativeModel(model_choice)
                    PROMPT = f"Negotiation Coach. Objection: {objection}. My Context: {my_product}. Provide 3 strategies."
                    response = model.generate_content(PROMPT)
                    st.session_state.neg_result = response.text
                except Exception as e:
                    st.error(f"出错: {e}")

    if st.session_state.neg_result:
        st.markdown(st.session_state.neg_result)
