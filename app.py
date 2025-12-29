import streamlit as st
import google.generativeai as genai

# 1. 页面配置
st.set_page_config(page_title="外贸数字指挥官", page_icon="🌍")
st.title("🌍 跨境电商·客户意图识别助手 (自动适配版)")

# 2. 安全配置
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ 未检测到 API Key，请在 Streamlit 后台配置 Secrets。")
    st.stop()

# 3. 自动寻找可用的模型 (核心修复逻辑)
@st.cache_resource
def get_valid_model():
    try:
        # 遍历所有可用模型，寻找第一个名字里带 "gemini" 且能生成内容的
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'gemini' in m.name:
                    return m.name
        return "models/gemini-pro" # 兜底默认值
    except Exception as e:
        return None

# 获取模型
valid_model_name = get_valid_model()

if valid_model_name:
    st.caption(f"✅ 系统已自动连接至模型: `{valid_model_name}`")
else:
    st.error("❌ 无法连接 Google 服务器，请检查 API Key 是否正确或网络是否通畅。")
    st.stop()

# 4. 定义提示词
SYSTEM_PROMPT = """
You are a Senior Cross-border E-commerce Sales Specialist.
Analyze the user input and output a structured report:
1. Intent Category
2. Lead Score (0-10)
3. Sentiment
4. Key Information
5. Draft Response
Constraint: If input is spam, output "🚫 SPAM".
"""

# 5. 界面交互
user_input = st.text_area("请粘贴客户邮件:", height=150)

if st.button("🚀 开始分析"):
    if not user_input:
        st.warning("请输入内容")
    else:
        with st.spinner('AI 正在思考中...'):
            try:
                # 使用自动检测到的模型名字
                model = genai.GenerativeModel(valid_model_name)
                full_prompt = f"{SYSTEM_PROMPT}\n\nUser Input:\n{user_input}"
                response = model.generate_content(full_prompt)
                st.success("分析完成！")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"发生错误: {e}")
