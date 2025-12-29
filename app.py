import streamlit as st
import google.generativeai as genai

# 1. 页面基础设置
st.set_page_config(page_title="外贸数字指挥官", page_icon="🌍")
st.title("🌍 跨境电商·客户意图识别助手")
st.markdown("此工具由 Google Gemini Pro 驱动，完全免费供内部使用。")

# 2. 获取 API Key (从 Streamlit 后台获取，安全！)
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ 未检测到 API Key，请联系系统管理员在后台配置 Secrets。")
    st.stop()

# 3. 定义你的“超级提示词” (在这里修改你的指令)
SYSTEM_PROMPT = """
You are a Senior Cross-border E-commerce Sales Specialist.
Analyze the user input (customer message) and output a structured report:

1. **Intent Category:** [Purchase Inquiry / Product Question / Order Status / Complaint / Spam]
2. **Lead Score (0-10):** (10 is immediate purchase)
3. **Sentiment:** [Positive / Neutral / Negative]
4. **Key Information:** (Product, Quantity, Location)
5. **Next Best Action:** (What should I do?)
6. **Draft Response:** (Write a professional English reply)

Constraint: If input is spam, output "🚫 SPAM".
"""

# 4. 界面交互区
user_input = st.text_area("请粘贴客户的邮件或聊天记录：", height=150, placeholder="例如：Hi, do you have stock for the outdoor pods in Sydney?")

if st.button("🚀 开始分析"):
    if not user_input:
        st.warning("请先输入内容！")
    else:
        with st.spinner('AI 正在思考中...'):
            try:
                # 调用 Gemini 模型 (这里已修正为 pro)
                model = genai.GenerativeModel('gemini-pro')
                
                # 组合提示词
                full_prompt = f"{SYSTEM_PROMPT}\n\nUser Input:\n{user_input}"
                
                response = model.generate_content(full_prompt)
                st.success("分析完成！")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"发生错误: {e}")
