import streamlit as st
import google.generativeai as genai
import requests
import json

# ==========================================
# 1. 核心配置
# ==========================================
st.set_page_config(page_title="外贸数字指挥官 (深度情报版)", page_icon="🕵️", layout="wide")

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ 未检测到 API Key，请在 Streamlit 后台 Secrets 里配置。")
    st.stop()

# ==========================================
# 2. 模型锁定 (直接用 2.5-flash)
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
    "🌐 全网情报深挖 (联网版)" 
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

# --- 功能三：全网深挖 (⭐ 深度情报版) ---
elif app_mode == "🌐 全网情报深挖 (联网版)":
    st.title("🌐 全网深度商业情报 (Google Search)")
    st.info("💡 现在的 AI 已经变身为‘商业侦探’，它会尝试挖掘战略、痛点和竞争对手。")
    
    search_query = st.text_input("输入客户公司名：", placeholder="例如：Costco Wholesale")
    
    if st.button("🌍 启动深度挖掘"):
        if not search_query:
            st.warning("请输入公司名！")
        else:
            with st.spinner('正在全网搜集情报并进行商业推理...'):
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/{valid_model_name}:generateContent?key={api_key}"
                    
                    # 构造深度分析的指令
                    payload = {
                        "contents": [{
                            "parts": [{
                                "text": f"""
                                I want you to act as a **Senior B2B Market Intelligence Analyst**. 
                                Your goal is not just to summarize basic info, but to dig for **sales opportunities**.
                                
                                Please use Google Search to investigate this company: "{search_query}".
                                
                                Produce a **"Deep-Dive Intelligence Report"** containing:

                                1.  **🏢 Business DNA Check:**
                                    * **Real Identity:** Are they a Manufacturer, Distributor, Wholesaler, or Retailer? (Verify this carefully)
                                    * **Market Position:** Are they high-end luxury, mass market, or discount?
                                
                                2.  **🎯 Strategic Radar (Crucial):**
                                    * **Latest Moves:** Check recent news (last 12 months). Are they expanding? Opening new stores? Laying off people? Launching new brands?
                                    * **Pain Points:** Based on news/reviews, what problems might they be facing? (e.g., supply chain issues, quality complaints, financial pressure?)
                                
                                3.  **🛒 Procurement Prediction (Guessing their needs):**
                                    * Based on their product lines, what kind of products are they likely sourcing from China/Overseas?
                                    * What are their likely criteria? (Price-sensitive? Quality-focused? Innovation-focused?)
                                
                                4.  **⚔️ Competitive Landscape:**
                                    * Who are their main rivals? (Knowing this helps me pitch against them).
                                
                                5.  **⚡ Actionable Cold Email Strategy:**
                                    * Suggest a **"Hook"** for my first email based on the news/strategy you found above. (e.g., "I saw you are expanding in Europe, maybe you need...")

                                Please cite sources where possible. If info is not found, make a logical deduction based on their industry.
                                """
                            }]
                        }],
                        "tools": [{"google_search": {}}]
                    }
                    
                    headers = {'Content-Type': 'application/json'}
                    
                    # ⚠️ 注意这里：这行就是刚才报错的地方，这次我写完整了
                    response = requests.post(url, headers=headers, data=json.dumps(payload))
                    
                    if response.status_code == 200:
                        result = response.json()
                        try:
                            # 提取回答
                            answer = result['candidates'][0]['content']['parts'][0]['text']
                            
                            # 尝试显示搜索来源
                            try:
                                grounding = result['candidates'][0]['groundingMetadata']['searchEntryPoint']['renderedContent']
                                st.success("✅ 搜索完成，情报如下：")
                                st.markdown(grounding, unsafe_allow_html=True)
                            except:
                                pass
                                
                            st.markdown(answer)
                        except KeyError:
                            st.error("AI 搜索到了数据，但整理失败，请重试。")
                    else:
                        st.error(f"请求失败 (代码 {response.status_code})")
                        st.text(response.text)
                        
                except Exception as e:
                    st.error(f"发生错误: {str(e)}")
