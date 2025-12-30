import streamlit as st
import google.generativeai as genai
import time

# ==========================================
# 1. 核心配置
# ==========================================
st.set_page_config(page_title="外贸数字指挥官 (终极修复版)", page_icon="🦁", layout="wide")

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ 未检测到 API Key，请在 Streamlit 后台配置。")
    st.stop()

# ==========================================
# 2. 实弹测试：寻找真正能说话的模型
# ==========================================
@st.cache_resource
def find_working_model():
    # 候选名单：按优先级排列
    # 既然 Pro 没额度，我们把 proven winner (2.5-flash) 放前面，或者放后面作为保底
    candidates = [
        "models/gemini-1.5-pro",      # 1. 还是先试探一下 Pro (万一能用呢)
        "models/gemini-2.5-flash",    # 2. 你之前成功过的版本 (重点！)
        "models/gemini-1.5-flash",    # 3. 普通 Flash
        "models/gemini-pro",          # 4. 老款 Pro
    ]
    
    # 遍历尝试
    for model_name in candidates:
        try:
            # 建立模型
            model = genai.GenerativeModel(model_name)
            # 实弹射击：真的生成一个字试试，看报不报错
            response = model.generate_content("Hi")
            if response.text:
                return model_name # 成功了！就是它！
        except Exception as e:
            # 失败了(404或429)，默默跳过，试下一个
            continue
            
    return None # 如果所有都挂了

# 获取经过验证的模型
with st.spinner("正在进行模型链路自检，请稍候..."):
    valid_model_name = find_working_model()

if not valid_model_name:
    st.error("❌ 无法找到任何可用的模型。请检查 API Key 额度。")
    st.stop()

# ==========================================
# 3. 侧边栏
# ==========================================
st.sidebar.title("🦁 指挥官控制台")
app_mode = st.sidebar.radio("任务选择：", ["📧 询盘深度分析", "🕵️‍♂️ 客户背景侦探"])
st.sidebar.markdown("---")

# 显示最终胜出的模型
if "pro" in valid_model_name.lower():
    st.sidebar.success(f"🧠 深度模式 (Pro)\n引擎: `{valid_model_name}`")
elif "2.5" in valid_model_name:
    st.sidebar.success(f"🚀 最新极速版 (2.5)\n引擎: `{valid_model_name}`")
else:
    st.sidebar.info(f"⚡ 稳定极速版\n引擎: `{valid_model_name}`")

# ==========================================
# 4. 通用调用函数
# ==========================================
def ask_gemini(prompt):
    # 直接用刚才测试通过的那个模型，不需要再 fallback 了，因为它是肯定能用的
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
