import streamlit as st
import google.generativeai as genai
import pandas as pd
from PIL import Image

# 1. 页面基本配置
st.set_page_config(page_title="B2B 全能 AI 助手", layout="wide")

# 2. 安全读取 API Key
try:
    # 确保在 Streamlit Secrets 中键名是 GEMINI_API_KEY
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.sidebar.error("❌ 未找到 Secrets 配置，请检查 Streamlit 后台设置。")
    api_key = None

# 3. 侧边栏导航
with st.sidebar:
    st.title("🛠️ 业务功能菜单")
    # 使用目前最稳定的 API 标识符
    model_choice = st.selectbox(
        "选择 AI 模型", 
        ["gemini-2.0-flash-exp", "gemini-1.5-pro", "gemini-1.5-flash"],
        index=0,
        help="2.0-flash-exp 是目前最推荐的快速测试版本"
    )
    
    menu = st.radio(
        "选择工作模块", 
        ["🌍 客户开发", "📊 财务审计", "📸 多媒体分析", "🗄️ 数据库模拟"]
    )
    st.divider()
    st.info("目标：半年学习亚马逊并拿 9 万补贴")

# 4. 主逻辑
if not api_key:
    st.warning("⚠️ 请先配置 API Key。")
else:
    model = genai.GenerativeModel(model_choice)

    # --- 模块 1：客户开发 ---
    if menu == "🌍 客户开发":
        st.header("🌍 全球客户开发")
        task = st.selectbox("任务", ["开发信润色", "德国市场分析", "询盘模拟"])
        context = st.text_area("输入背景信息", placeholder="例如：分析德国跨境电商市场")
        if st.button("🚀 开始生成"):
            with st.spinner("AI 正在处理..."):
                response = model.generate_content(f"请作为外贸专家处理：{task}\n内容：{context}")
                st.success("生成成功：")
                st.write(response.text)

    # --- 模块 2：财务审计 ---
    elif menu == "📊 财务审计":
        st.header("📊 成本利润审计")
        uploaded_file = st.file_uploader("上传 Excel/CSV", type=['csv', 'xlsx'])
        if uploaded_file:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('csv') else pd.read_excel(uploaded_file)
            st.dataframe(df)
            if st.button("🔍 智能分析"):
                # 针对你学习 Excel 成本利润表的需求
                response = model.generate_content(f"请审计此财务表并给优化建议：\n{df.to_string()}")
                st.write(response.text)

    # --- 模块 3：多媒体分析 ---
    elif menu == "📸 多媒体分析":
        st.header("📸 产品图文/视频分析")
        media = st.file_uploader("上传图片或视频", type=['png', 'jpg', 'jpeg', 'mp4'])
        query = st.text_input("你想问什么？", value="请分析这个产品的卖点")
        if media and st.button("⚡ 开始分析"):
            if media.type.startswith('image'):
                img = Image.open(media)
                st.image(img, width=400)
                response = model.generate_content([query, img])
                st.write(response.text)
            else:
                st.video(media)
                st.warning("视频深度分析建议先测试图片模式，或使用 Pro 模型。")

    # --- 模块 4：数据库模拟 ---
    elif menu == "🗄️ 数据库模拟":
        st.header("🗄️ 业务记录")
        if 'db' not in st.session_state: st.session_state.db = []
        entry = st.text_input("录入新信息")
        if st.button("💾 保存"):
            st.session_state.db.append(entry)
        st.write("历史记录：", st.session_state.db)
