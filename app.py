import streamlit as st
import google.generativeai as genai

# ==========================================
# 1. 核心配置
# ==========================================
st.set_page_config(page_title="外贸数字指挥官 (Pro版)", page_icon="🧠", layout="wide")

# 获取 API Key
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ 未检测到 API Key，请在 Streamlit 后台 Secrets 里配置。")
    st.stop()

# ==========================================
# 2. 智能模型选择逻辑 (Pro 优先!)
# ==========================================
@st.cache_resource
def get_best_model():
    # 我们定义一个“愿望单”，按优先级排列
    # 1.5-pro 是目前最强的，我们把它排第一
    preferred_models = [
        "gemini-1.5-pro",          # 最新、最强的 Pro
        "gemini-1.5-pro-latest",   # 备选 Pro
        "gemini-pro",              # 旧版 Pro
        "gemini-1.5-flash"         # 最后的保底 (如果 Pro 挂了才用这个)
    ]
    
    available_models = [m.name.replace("models/", "") for m in genai.list_models()]
    
    # 遍历愿望单，找到第一个能用的
    for model_name in preferred_models:
        # 有些账号返回名字带 models/ 前缀，有些不带，模糊匹配一下
        for av_model in available_models:
            if model_name in av_model:
                return av_model  # 找到了最好的！直接返回
    
    return "gemini-1.5-flash" # 万一都没有，用 Flash 兜底

# 获取模型
current_model_name = get_best_model()

# ==========================================
# 3. 侧边栏
# ==========================================
st.sidebar.title("🚀 指挥官控制台")
app_mode = st.sidebar.radio("任务选择：", ["📧 询盘深度分析", "🕵️‍♂️ 客户背景侦探"])

st.sidebar.markdown("---")
# 显示当前使用的模型 (让你确认是不是 Pro)
if "pro" in current_model_name:
    st.sidebar.success(f"🧠 深度思考模式已开启\n引擎: `{current_model_name}`")
else:
    st.sidebar.warning(f"⚡ 极速模式运行中\n引擎: `{current_model_name}`")

# ==========================================
# 4. 功能一：询盘深度分析
# ==========================================
if app_mode == "📧 询盘深度分析":
    st.title("📧 深度询盘分析 (Pro)")
    st.markdown("已启用 **Gemini 1.5 Pro** 模型，进行更深层的语义理解和情感分析。")

    INTENT_PROMPT = """
    You are a Senior Cross-border E-commerce Sales Director.
    Analyze the user input deeply. 
    
    Output a structured report:
    1. **Detected Language:** 2. **Intent Category:** [Purchase Inquiry / Product Question / Order Status / Complaint / Spam]
    3. **Lead Score (0-10):** (Evaluate based on urgency, specificity, and budget hints)
    4. **Sentiment & Tone:** (e.g., Anxious, Professional, Casual, Angry)
    5. **Key Extraction:** (Product, Specs, Qty, Destination)
    6. **Strategic Advice:** (Hidden needs analysis)
    7. **Draft Response (Dual Language):** - Version A (English - Professional & Persuasive)
       - Version B (Native Language of Customer)
    
    Constraint: If input is spam, output "🚫 SPAM".
    """

    user_input = st.text_area("请粘贴客户邮件：", height=200)

    if st.button("🚀 开始深度分析"):
        if not user_input:
            st.warning("请输入内容")
        else:
            with st.spinner('Pro 模型正在深度思考 (可能需要多几秒)...'):
                try:
                    model = genai.GenerativeModel(current_model_name)
                    response = model.generate_content(f"{INTENT_PROMPT}\n\nUser Input:\n{user_input}")
                    st.success("分析完成！")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"出错: {e}")

# ==========================================
# 5. 功能二：客户背调 (Pro 版最适合这个!)
# ==========================================
elif app_mode == "🕵️‍♂️ 客户背景侦探":
    st.title("🕵️‍♂️ B2B 深度背调侦探")
    st.markdown("利用 Pro 模型的长上下文能力，精准推断客户的商业模式。")

    INVESTIGATOR_PROMPT = """
    You are an expert B2B Corporate Investigator.
    Analyze the provided website text deeply to construct a Client Profile.

    1. **Business Identity Analysis (Crucial):**
       - Is it an End User, Distributor, Wholesaler, or Contractor?
       - *Evidence:* Quote specific words from the text that support your judgment.

    2. **Company Strength Estimation:**
       - Look for: Years established, Number of employees, Project gallery size.
       - Grade: [Tier 1 (Big Player) / Tier 2 (SMB) / Tier 3 (Startup/Individual)]

    3. **Commercial Intent & Pain Points:**
       - What value proposition do they emphasize to THEIR customers? (e.g. Speed? Luxury? Low Cost?)
       - How can WE pitch to them based on that?

    4. **Risk Assessment:**
       - Any red flags? (e.g., text looks like a scam site, generic template?)

    5. **Cold Email Strategy:**
       - Write a high-level "Angle" for the first approach.
    """

    bg_input = st.text_area("请粘贴客户网站文本 (About Us/Home):", height=300)

    if st.button("🔍 开始深度侦查"):
        if not bg_input:
            st.warning("请粘贴文本")
        else:
            with st.spinner('Pro 侦探正在分析蛛丝马迹...'):
                try:
                    model = genai.GenerativeModel(current_model_name)
                    response = model.generate_content(f"{INVESTIGATOR_PROMPT}\n\nClient Text:\n{bg_input}")
                    st.success("调查报告已生成！")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"出错: {e}")
