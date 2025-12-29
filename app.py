import streamlit as st
import google.generativeai as genai

# ==========================================
# 1. 核心配置
# ==========================================
st.set_page_config(page_title="外贸数字指挥官 (Pro稳健版)", page_icon="🧠", layout="wide")

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ 未检测到 API Key，请在 Streamlit 后台 Secrets 里配置。")
    st.stop()

# ==========================================
# 2. 智能模型获取 (带自动降级功能)
# ==========================================
@st.cache_resource
def get_model_options():
    # 这里的逻辑是：只找我们确定能用的稳定版本，不找 "latest" 这种不确定的
    available = [m.name for m in genai.list_models()]
    return available

# ==========================================
# 3. 侧边栏：指挥官控制台
# ==========================================
st.sidebar.title("🚀 指挥官控制台")

# 让用户自己选模型（双保险）
model_options = ["自动智能选择 (推荐)", "强制 Flash (速度快)", "强制 Pro (深度思考)"]
selected_mode = st.sidebar.selectbox("🧠 AI 思考模式:", model_options)

app_mode = st.sidebar.radio("任务选择：", ["📧 询盘深度分析", "🕵️‍♂️ 客户背景侦探"])

st.sidebar.markdown("---")

# 定义一个通用的调用函数，带自动重试
def ask_gemini(prompt):
    # 1. 确定想用的模型名字
    target_model = "models/gemini-1.5-pro" # 默认想用 Pro
    
    if "Flash" in selected_mode:
        target_model = "models/gemini-1.5-flash"
    elif "自动" in selected_mode:
        # 自动模式优先试 Pro
        target_model = "models/gemini-1.5-pro"
        
    try:
        model = genai.GenerativeModel(target_model)
        return model.generate_content(prompt)
    except Exception as e:
        # 如果 Pro 报错 (比如 429 限流)，自动降级到 Flash
        if "Flash" not in target_model: # 如果本来就是 Flash 错，那就没办法了
            st.toast(f"⚠️ Pro 模型繁忙，正在自动切换至 Flash 极速版...", icon="⚡")
            fallback_model = genai.GenerativeModel("models/gemini-1.5-flash")
            return fallback_model.generate_content(prompt)
        else:
            raise e

# ==========================================
# 4. 功能一：询盘深度分析
# ==========================================
if app_mode == "📧 询盘深度分析":
    st.title("📧 深度询盘分析")
    st.info("💡 提示：如果发现 'Pro' 报错，请在左侧切换为 'Flash' 模式。")

    INTENT_PROMPT = """
    You are a Senior Cross-border E-commerce Sales Director.
    Analyze the user input deeply. Output a structured report:
    1. **Detected Language:**
    2. **Intent Category:**
    3. **Lead Score (0-10):**
    4. **Sentiment & Tone:**
    5. **Key Extraction:**
    6. **Strategic Advice:**
    7. **Draft Response (Dual Language):** - Version A (English) - Version B (Native)
    Constraint: If input is spam, output "🚫 SPAM".
    """

    user_input = st.text_area("请粘贴客户邮件：", height=200)

    if st.button("🚀 开始分析"):
        if not user_input:
            st.warning("请输入内容")
        else:
            with st.spinner('AI 正在思考...'):
                try:
                    response = ask_gemini(f"{INTENT_PROMPT}\n\nUser Input:\n{user_input}")
                    st.success("分析完成！")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"发生错误，请稍后重试: {e}")

# ==========================================
# 5. 功能二：客户背调
# ==========================================
elif app_mode == "🕵️‍♂️ 客户背景侦探":
    st.title("🕵️‍♂️ B2B 深度背调侦探")
    
    INVESTIGATOR_PROMPT = """
    You are an expert B2B Corporate Investigator.
    Analyze the provided website text deeply to construct a Client Profile.
    1. **Business Identity Analysis:** (End User / Distributor / Builder?)
    2. **Company Strength:** (Tier 1/2/3)
    3. **Commercial Intent:**
    4. **Cold Email Strategy:**
    """

    bg_input = st.text_area("请粘贴客户网站文本 (About Us/Home):", height=300)

    if st.button("🔍 开始侦查"):
        if not bg_input:
            st.warning("请粘贴文本")
        else:
            with st.spinner('侦探正在分析...'):
                try:
                    response = ask_gemini(f"{INVESTIGATOR_PROMPT}\n\nClient Text:\n{bg_input}")
                    st.success("报告已生成！")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"发生错误: {e}")
