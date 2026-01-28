import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. 基础配置
st.set_page_config(page_title="B2B 全能助手 (稳定版)", layout="wide")

# 2. 读取 Secrets 里的 API Key
try:
    # 确保在 Streamlit 控制台配置的键名为 GEMINI_API_KEY
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.sidebar.error("❌ 没找到 API Key。请在 Streamlit Settings -> Secrets 填入 GEMINI_API_KEY")
    api_key = None

# 3. 侧边栏
with st.sidebar:
    st.title("🛠️ 功能面板")
    # 按照兼容性排序：从最稳到最新
    model_id = st.selectbox(
        "选择模型", 
        ["gemini-pro", "gemini-1.5-flash", "gemini-1.5-pro"],
        help="如果报错，请尝试切换到 gemini-pro"
    )
    menu = st.radio("功能模块", ["🌍 客户开发", "📸 视频/图片分析"])
    st.divider()
    st.info("宁波外贸实战 | 目标 9 万补贴")

# 4. 主逻辑
if api_key:
    # 这里的 try 捕获模型初始化的错误
    try:
        model = genai.GenerativeModel(model_id)

        if menu == "🌍 客户开发":
            st.header("🌍 客户开发与市场分析")
            user_text = st.text_area("输入内容 (例如：分析德国跨境电商市场)")
            if st.button("🚀 开始生成"):
                with st.spinner("AI 正在思考..."):
                    # 针对文字任务的调用
                    response = model.generate_content(user_text)
                    st.success("分析结果：")
                    st.write(response.text)

        elif menu == "📸 视频/图片分析":
            st.header("📸 多模态素材分析")
            st.write("明天拍完视频可以传上来提炼卖点")
            
            uploaded_file = st.file_uploader("上传产品图", type=["jpg", "jpeg", "png"])
            prompt = st.text_input("想问 AI 什么？", value="请总结该产品的 3 个核心卖点")
            
            if uploaded_file and st.button("🔍 开始视觉分析"):
                img = Image.open(uploaded_file)
                st.image(img, width=400)
                # 针对多模态的调用：第一个参数是 prompt，第二个是图片对象
                with st.spinner("解析图片中..."):
                    response = model.generate_content([prompt, img])
                    st.write(response.text)

    except Exception as e:
        st.error(f"⚠️ 发生错误: {str(e)}")
        st.info("提示：如果报 404，请确认你的 API Key 已经在 Google Cloud 中启用了 'Generative Language API'")
