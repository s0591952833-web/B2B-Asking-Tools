import streamlit as st
import google.generativeai as genai
import requests # 引入直接发包工具
import json

# ==========================================
# 1. 核心配置
# ==========================================
st.set_page_config(page_title="外贸数字指挥官 (API直连版)", page_icon="🦁", layout="wide")

# 获取 API Key
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ 未检测到 API Key，请在 Streamlit 后台 Secrets 里配置。")
    st.stop()

# ==========================================
# 2. 简单的模型自检
# ==========================================
@st.cache_resource
def get_working_model_name():
    # 既然之前验证了 2.5-flash 能用，我们就直接锁定它
    return "models/gemini-2.5-flash"

valid_model_name = get_working_model_name()

# ==========================================
# 3. 侧边栏
# ==========================================
st.sidebar.title("🦁 指挥官控制台")
app_mode = st.sidebar.radio("任务选择：", [
    "📧 询盘深度分析", 
    "🕵️‍♂️ 粘贴文本背调 (稳)", 
    "🌐 全网背景深挖 (联网版)" 
])
st.sidebar.markdown("---")
st.sidebar.success(f"🚀 引擎在线: `{valid_model_name}`")

# ==========================================
# 4. 功能逻辑
# ==========================================

# --- 功能一：询盘分析 (保持 SDK 调用) ---
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

# --- 功能二：文本背调 (保持 SDK 调用) ---
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

# --- 功能三：全网深挖 (⭐ 改用 API 直连!) ---
elif app_mode == "🌐 全网背景深挖 (联网版)":
    st.title("🌐 全网背景深挖 (Google Search)")
    st.info("💡 技术说明：采用 REST API 直连模式，绕过 Python 库版本限制。")
    
    search_query = st.text_input("输入客户公司名：", placeholder="例如：Costco Wholesale")
    
    if st.button("🌍 联网搜索分析"):
        if not search_query:
            st.warning("请输入公司名！")
        else:
            with st.spinner('正在直连 Google 服务器检索...'):
                try:
                    # 1. 构造直连请求的 URL
                    url = f"https://generativelanguage.googleapis.com/v1beta/{valid_model_name}:generateContent?key={api_key}"
                    
                    # 2. 构造请求体 (Payload) - 这里我们可以随心所欲写最新的语法
                    payload = {
                        "contents": [{
                            "parts": [{
                                "text": f"""
                                Use Google Search to find info about: "{search_query}".
                                Write a B2B investigation report including:
                                1. Business Type 2. Key Products 3. Size & Location 4. Latest News 5. Website URL.
                                """
                            }]
                        }],
                        "tools": [{"google_search": {}}] # ⭐ 核心：直接传 JSON，不再经过库的检查
                    }
                    
                    # 3. 发送请求
                    headers = {'Content-Type': 'application/json'}
                    response = requests.post(url, headers=headers, data=json.dumps(payload))
                    
                    # 4. 解析结果
                    if response.status_code == 200:
                        result = response.json()
                        try:
                            # 提取 AI 回复的文本
                            answer = result['candidates'][0]['content']['parts'][0]['text']
                            
                            # 尝试提取搜索来源 (Grounding Metadata)
                            try:
                                grounding = result['candidates'][0]['groundingMetadata']['searchEntryPoint']['renderedContent']
                                st.success("✅ 数据来源：Google Search")
                                st.markdown(grounding, unsafe_allow_html=True)
                            except:
                                pass
                                
                            st.markdown(answer)
                            
                        except KeyError:
                            # 如果返回结构不对，打印出来看
                            st.error("AI 返回了无法解析的数据，可能是被风控拦截。")
                            st.json(result)
                    else:
                        st.error(f"请求失败 (状态码 {response.status_code})")
                        st.text(response.text)
                        
                except Exception as e:
                    st.error(f"直连发生错误: {str(e)}")
