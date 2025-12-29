import streamlit as st
import google.generativeai as genai

# ==========================================
# 1. 核心配置
# ==========================================
st.set_page_config(page_title="外贸数字指挥官 (稳健版)", page_icon="🛡️", layout="wide")

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ 未检测到 API Key，请在 Streamlit 后台配置。")
    st.stop()

# ==========================================
# 2. 模型选择 (精准锁定 1.5 Pro)
# ==========================================
@st.cache_resource
def get_safe_model_name():
    try:
        # 获取列表
        all_models = [m.name for m in genai.list_models()]
        
        # ⚠️ 关键逻辑：按照优先级去找，而不是随便找
        # 1. 第一顺位：Gemini 1.5 Pro (目前最强且免费额度稳定的)
        if "models/gemini-1.5-pro" in all_models:
            return "models/gemini-1.5-pro"
        
        # 2. 第二顺位：Gemini 1.5 Pro Latest (备选)
        if "models/gemini-1.5-pro-latest" in all_models:
            return "models/gemini-1.5-pro-latest"
            
        # 3. 第三顺位：Gemini 1.0 Pro (老款稳定版)
        if "models/gemini-pro" in all_models:
            return "models/gemini-pro"
            
        # 4. 保底：Flash (速度快，一定能用)
        return "models/gemini-1.5-flash"
        
    except Exception:
        return "models/gemini-1.5-flash"

# 获取选定的模型
target_model = get_safe_model_name()

# ==========================================
# 3. 智能调用函数 (带自动急救包)
# ==========================================
def ask_gemini_safe(prompt):
    try:
        # 尝试使用选定的 Pro 模型
        model = genai.GenerativeModel(target_model)
        return model.generate_content(prompt)
    except Exception as e:
        # 🚨 能够捕获 429 限流错误或其他错误
        # 如果 Pro 报错，立刻切 Flash 进行急救，不再显示红框报错
        st.toast(f"⚠️ Pro 模型繁忙，已自动无缝切换至 Flash 极速通道。", icon="⚡")
        fallback_model = genai.GenerativeModel("models/gemini-1.5-flash")
        return fallback_model.generate_content(prompt)

# ==========================================
# 4. 侧边栏
# ==========================================
st.sidebar.title("🚀 指挥官控制台")
app_mode = st.sidebar.radio("任务选择：", ["📧 询盘深度分析", "🕵️‍♂️ 客户背景侦探"])
st.sidebar.markdown("---")
st.sidebar.info(f"🛡️ 当前主力引擎: `{target_model}`\n(自带自动降级保护)")

# ==========================================
# 5. 功能一：询盘分析
# ==========================================
if app_mode == "📧 询盘深度分析":
    st.title("📧 深度询盘分析")
    st.caption("优先使用 Pro 模型进行深度思考，遇阻自动切换。")

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
            with st.spinner('AI 正在深度思考中...'):
                try:
                    response = ask_gemini_safe(f"{INTENT_PROMPT}\n\nUser Input:\n{user_input}")
                    st.success("分析完成！")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"最终错误: {e}")

# ==========================================
# 6. 功能二：客户背调
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
                    response = ask_gemini_safe(f"{INVESTIGATOR_PROMPT}\n\nClient Text:\n{bg_input}")
                    st.success("报告已生成！")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"最终错误: {e}")
