import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# ==========================================
# 1. 核心配置
# ==========================================
st.set_page_config(page_title="外贸数字指挥官 (联网终极版)", page_icon="🌍", layout="wide")

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ 未检测到 API Key，请在 Streamlit 后台配置。")
    st.stop()

# ==========================================
# 2. 模型自检 (Self-Healing)
# ==========================================
@st.cache_resource
def find_working_model():
    candidates = [
        "models/gemini-2.5-flash",    # 你的主力王牌
        "models/gemini-1.5-pro",
        "models/gemini-1.5-flash",
        "models/gemini-pro",
    ]
    for model_name in candidates:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Hi")
            if response.text:
                return model_name
        except:
            continue
    return None

with st.spinner("正在连接 Google AI 大脑..."):
    valid_model_name = find_working_model()

if not valid_model_name:
    st.error("❌ 无法连接任何模型。")
    st.stop()

# ==========================================
# 3. 联网搜索工具配置 (Search Tool)
# ==========================================
# 只有在用户选择联网模式时，我们才尝试加载这个工具
def get_search_model():
    try:
        # 尝试开启 Google Search 工具
        tools = [
            {"google_search_retrieval": {
                "dynamic_retrieval_config": {
                    "mode": "dynamic",
                    "dynamic_threshold": 0.3,
                }
            }}
        ]
        return genai.GenerativeModel(valid_model_name, tools=tools)
    except Exception:
        return None

# ==========================================
# 4. 侧边栏
# ==========================================
st.sidebar.title("🌍 指挥官控制台")
app_mode = st.sidebar.radio("任务选择：", [
    "📧 询盘深度分析", 
    "🕵️‍♂️ 粘贴文本背调 (稳)", 
    "🌐 全网背景深挖 (联网版)"  # <--- 新增的功能
])
st.sidebar.markdown("---")
st.sidebar.success(f"🚀 引擎在线: `{valid_model_name}`")

# ==========================================
# 5. 功能逻辑
# ==========================================

# --- 功能一：询盘分析 ---
if app_mode == "📧 询盘深度分析":
    st.title("📧 深度询盘分析")
    user_input = st.text_area("请粘贴客户邮件：", height=200)
    if st.button("🚀 分析"):
        if not user_input:
            st.warning("请输入内容")
        else:
            with st.spinner('AI 正在思考...'):
                try:
                    model = genai.GenerativeModel(valid_model_name)
                    PROMPT = """
                    Act as an Expert Sales Manager. Analyze this email.
                    Output: 1.Language 2.Intent 3.Lead Score(0-10) 4.Key Info 5.Draft Response(Dual Language).
                    """
                    response = model.generate_content(f"{PROMPT}\nInput: {user_input}")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"出错: {e}")

# --- 功能二：文本背调 (稳) ---
elif app_mode == "🕵️‍♂️ 粘贴文本背调 (稳)":
    st.title("🕵️‍♂️ 静态背景侦探")
    st.caption("适用场景：你已经打开了客户网站，复制了 'About Us' 的文字。")
    bg_input = st.text_area("粘贴网站文本：", height=300)
    if st.button("🔍 侦查"):
        if not bg_input:
            st.warning("请粘贴文本")
        else:
            with st.spinner('分析中...'):
                try:
                    model = genai.GenerativeModel(valid_model_name)
                    PROMPT = """
                    Analyze this company text. Report:
                    1. Identity (Wholesaler/Builder/End User?) 2. Scale 3. Pain Points 4. Pitch Strategy.
                    """
                    response = model.generate_content(f"{PROMPT}\nText: {bg_input}")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"出错: {e}")

# --- 功能三：全网深挖 (新!) ---
elif app_mode == "🌐 全网背景深挖 (联网版)":
    st.title("🌐 全网背景深挖 (Google Search)")
    st.caption("⚠️ 注意：此功能需要调用 Google 搜索权限。如果报错，说明你的免费账号暂不支持此功能。")
    
    search_query = st.text_input("输入客户公司名 或 网址：", placeholder="例如：Ningbo ABC Trading Co., Ltd")
    
    if st.button("🌍 联网搜索分析"):
        if not search_query:
            st.warning("请输入公司名！")
        else:
            with st.spinner('正在连接 Google Search 检索全网信息...'):
                try:
                    # 获取带搜索功能的模型
                    search_model = get_search_model()
                    if not search_model:
                        st.error("你的账号似乎不支持联网搜索组件。请使用功能二。")
                    else:
                        # 专门的联网提示词
                        SEARCH_PROMPT = f"""
                        Please use Google Search to find detailed information about this company: "{search_query}".
                        
                        Write a "Company Investigation Report" including:
                        1. **Business Type:** What exactly do they do? (Distributor? Retailer? Contractor?)
                        2. **Key Products:** What are they selling?
                        3. **Location & Scale:** Where are they? Do they look big?
                        4. **Latest News/Activity:** Any recent projects or news found?
                        5. **Website Summary:** Brief summary of their homepage if found.
                        
                        If you cannot find specific info, state "Not Found".
                        """
                        
                        response = search_model.generate_content(SEARCH_PROMPT)
                        
                        # 检查有没有用到搜索
                        try:
                            grounding_metadata = response.candidates[0].grounding_metadata
                            if grounding_metadata.search_entry_point:
                                st.info("✅ 已成功调用 Google 搜索数据")
                                st.markdown(grounding_metadata.search_entry_point.rendered_content)
                        except:
                            pass
                            
                        st.markdown(response.text)
                        
                except Exception as e:
                    st.error(f"联网搜索失败: {e}")
                    st.warning("原因可能是：免费 API Key 额度不支持搜索，或网络超时。建议使用'功能二'手动复制文本。")
