import streamlit as st
import google.generativeai as genai

# ==========================================
# 1. 核心配置
# ==========================================
st.set_page_config(page_title="外贸数字指挥官 (智能版)", page_icon="🧠", layout="wide")

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ 未检测到 API Key，请在 Streamlit 后台 Secrets 里配置。")
    st.stop()

# ==========================================
# 2. 动态模型搜索 (核心修复)
# ==========================================
@st.cache_resource
def get_best_available_model():
    try:
        # 1. 获取你账号里所有真实存在的模型
        all_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # 2. 定义搜索优先级：先找 Pro，再找 Flash
        # 你的账号里可能有 gemini-1.5-pro, gemini-2.0-pro 等等，我们只认 "pro"
        pro_candidates = [m for m in all_models if 'pro' in m.lower()]
        flash_candidates = [m for m in all_models if 'flash' in m.lower()]
        
        # 3. 决策
        if pro_candidates:
            # 找到了 Pro！直接用列表里的第一个（通常是最新版）
            return pro_candidates[0]
        elif flash_candidates:
            # 没 Pro，但在你之前的截图里证明你有 2.5-flash，那就用它
            return flash_candidates[0]
        elif all_models:
            # 实在不行，随便拿一个能用的
            return all_models[0]
        else:
            return "models/gemini-pro" # 最后的救命稻草
            
    except Exception as e:
        return "models/gemini-pro"

# 获取那个唯一正确的模型名字
valid_model_name = get_best_available_model()

# ==========================================
# 3. 侧边栏
# ==========================================
st.sidebar.title("🚀 指挥官控制台")
app_mode = st.sidebar.radio("任务选择：", ["📧 询盘深度分析", "🕵️‍♂️ 客户背景侦探"])
st.sidebar.markdown("---")

# 显示当前到底连上了哪个大神
if "pro" in valid_model_name.lower():
    st.sidebar.success(f"🧠 深度思考模式 (Pro)\n引擎: `{valid_model_name}`")
else:
    st.sidebar.info(f"⚡ 极速响应模式\n引擎: `{valid_model_name}`")

# ==========================================
# 4. 通用调用函数
# ==========================================
def ask_gemini(prompt):
    model = genai.GenerativeModel(valid_model_name)
    return model.generate_content(prompt)

# ==========================================
# 5. 功能一：询盘深度分析
# ==========================================
if app_mode == "📧 询盘深度分析":
    st.title("📧 深度询盘分析")
    
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
            with st.spinner(f'AI ({valid_model_name}) 正在思考...'):
                try:
                    response = ask_gemini(f"{INTENT_PROMPT}\n\nUser Input:\n{user_input}")
                    st.success("分析完成！")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"发生错误: {e}")

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
            with st.spinner(f'侦探 ({valid_model_name}) 正在分析...'):
                try:
                    response = ask_gemini(f"{INVESTIGATOR_PROMPT}\n\nClient Text:\n{bg_input}")
                    st.success("报告已生成！")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"发生错误: {e}")
