import streamlit as st
import google.generativeai as genai

# ==========================================
# 1. 核心配置与模型连接 (自动适配版)
# ==========================================
st.set_page_config(page_title="外贸数字指挥官", page_icon="🌍", layout="wide")

# 获取 API Key
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ 未检测到 API Key，请在 Streamlit 后台 Secrets 里配置。")
    st.stop()

# 自动寻找可用模型函数
@st.cache_resource
def get_valid_model():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'gemini' in m.name:
                    return m.name
        return "models/gemini-pro"
    except Exception:
        return None

valid_model_name = get_valid_model()

if not valid_model_name:
    st.error("❌ 无法连接 Google 模型，请检查网络或 Key。")
    st.stop()

# ==========================================
# 2. 侧边栏：功能选择中心
# ==========================================
st.sidebar.title("🚀 功能导航")
app_mode = st.sidebar.radio("请选择你要执行的任务：", 
    ["📧 询盘意图识别", "🕵️‍♂️ 客户背景背调"])

st.sidebar.markdown("---")
st.sidebar.info(f"✅ AI 引擎已就绪\n模型: `{valid_model_name}`")

# ==========================================
# 3. 功能一：询盘意图识别
# ==========================================
if app_mode == "📧 询盘意图识别":
    st.title("📧 跨境电商·询盘意图分析")
    st.markdown("把客户的邮件扔进来，AI 帮你判断是不是垃圾询盘，并写好回复。")

    # 提示词 A
    INTENT_PROMPT = """
    You are a Senior Cross-border E-commerce Sales Specialist.
    Analyze the user input and output a structured report:
    1. **Detected Language:** (e.g., French, Japanese)
    2. **Intent Category:** [Purchase Inquiry / Product Question / Order Status / Complaint / Spam]
    3. **Lead Score (0-10):** (10 is immediate purchase)
    4. **Sentiment:** [Positive / Neutral / Negative]
    5. **Key Information:** (Product, Quantity, Location)
    6. **Next Best Action:** (What should I do?)
    7. **Draft Response (Dual Language):** - Version A (English)
       - Version B (Customer's Native Language)
    Constraint: If input is spam, output "🚫 SPAM".
    """

    user_input = st.text_area("请粘贴客户邮件/聊天记录：", height=200, placeholder="例如：Hi, do you have stock for the outdoor pods in Sydney?")

    if st.button("🚀 开始分析询盘"):
        if not user_input:
            st.warning("请先输入内容！")
        else:
            with st.spinner('AI 正在拆解询盘...'):
                try:
                    model = genai.GenerativeModel(valid_model_name)
                    response = model.generate_content(f"{INTENT_PROMPT}\n\nUser Input:\n{user_input}")
                    st.success("分析完成！")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"出错啦: {e}")

# ==========================================
# 4. 功能二：客户背景背调 (新功能！)
# ==========================================
elif app_mode == "🕵️‍♂️ 客户背景背调":
    st.title("🕵️‍♂️ B2B 客户背景侦探")
    st.markdown("打开客户的网站，**复制 'About Us' 或首页的文字**，AI 帮你分析它是不是大客户。")

    # 提示词 B (侦探模式)
    INVESTIGATOR_PROMPT = """
    你是一名拥有20年经验的 B2B 商业侦探。
    请根据用户提供的【客户网站文本/邮件签名/简介】，生成一份《客户背景深度调查报告》：

    1. **客户画像 (Business Identity):**
       - 它是 End User (个人/自用)? 还是 Dealer/Distributor (经销商)? 还是 Builder (建筑商)?
       - *判定依据是什么？* (引用原文里的关键词)

    2. **规模与实力 (Company Scale):**
       - 员工数量、成立时间、是否有分公司？
       - 预估年采购潜力：(High/Medium/Low)

    3. **痛点与需求 (Needs & Pain Points):**
       - 他们的网站强调什么？(比如强调 Fast Delivery，说明他们缺库存；强调 Quality，说明看重质量)

    4. **销售切入建议 (Sales Strategy):**
       - 针对这个客户，我第一封开发信该主打什么卖点？

    5. **风险提示:**
       - 有没有看起来像皮包公司的迹象？
    """

    bg_input = st.text_area("请粘贴客户网站 'About Us' 或首页文本：", height=300, placeholder="把客户网站上的英文介绍全部复制粘贴到这里...")

    if st.button("🔍 开始侦查"):
        if not bg_input:
            st.warning("请先粘贴客户网站的文本！")
        else:
            with st.spinner('侦探正在分析线索...'):
                try:
                    model = genai.GenerativeModel(valid_model_name)
                    response = model.generate_content(f"{INVESTIGATOR_PROMPT}\n\nClient Website Text:\n{bg_input}")
                    st.success("调查报告已生成！")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"出错啦: {e}")
