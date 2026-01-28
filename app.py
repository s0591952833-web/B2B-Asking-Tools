import streamlit as st
import google.generativeai as genai
import pandas as pd
from PIL import Image
import io

# 1. 页面配置
st.set_page_config(page_title="B2B 全能 AI 助手", layout="wide", initial_sidebar_state="expanded")

# 2. 从 Streamlit Secrets 安全读取 API Key
# 请确保你在 Streamlit Cloud 的 Settings -> Secrets 里配置了 GEMINI_API_KEY
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.sidebar.error("❌ 未在 Secrets 中找到 API Key，请检查配置。")
    api_key = None

# 3. 侧边栏导航
with st.sidebar:
    st.title("🛠️ 业务功能菜单")
    # 自动适配 Gemini 3 系列模型
    model_choice = st.selectbox(
        "选择 AI 模型", 
        ["gemini-3-flash", "gemini-3-pro-preview"],
        help="Flash 速度快，Pro 推理强（适合审计和深度分析）"
    )
    
    menu = st.radio(
        "选择工作模块", 
        ["🌍 客户开发", "📊 财务审计", "📸 多媒体分析", "🗄️ 数据库模拟"]
    )
    
    st.divider()
    st.info(f"当前城市：宁波 | 目标：半年拿9万补贴")

# 4. 主逻辑实现
if not api_key:
    st.warning("⚠️ 请先在 Streamlit Secrets 中配置 API Key 才能使用功能。")
else:
    model = genai.GenerativeModel(model_choice)

    # --- 模块 1：客户开发 ---
    if menu == "🌍 客户开发":
        st.header("🌍 全球客户开发 (B2B)")
        col1, col2 = st.columns(2)
        with col1:
            task_type = st.selectbox("任务类型", ["开发信润色", "询盘模拟回复", "外贸术语翻译"])
            context = st.text_area("输入背景信息（如产品卖点、客户痛点）", height=200)
        with col2:
            if st.button("🚀 开始生成"):
                with st.spinner("AI 正在深度思考..."):
                    prompt = f"你是一位资深外贸专家，请针对以下内容进行{task_type}：\n{context}"
                    response = model.generate_content(prompt)
                    st.success("生成结果：")
                    st.write(response.text)

    # --- 模块 2：财务审计 ---
    elif menu == "📊 财务审计":
        st.header("📊 成本利润分析与审计")
        uploaded_file = st.file_uploader("上传 Excel 或 CSV 财务报表", type=['csv', 'xlsx'])
        if uploaded_file:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('csv') else pd.read_excel(uploaded_file)
            st.dataframe(df, use_container_width=True)
            if st.button("🔍 开始 AI 审计"):
                with st.spinner("正在分析财务数据结构..."):
                    # 将 DataFrame 转为文本供模型分析
                    response = model.generate_content(f"请作为财务审计师，分析以下表格数据是否存在异常，并给出成本优化建议：\n{df.to_string()}")
                    st.markdown("### 审计建议")
                    st.write(response.text)

    # --- 模块 3：多媒体分析 ---
    elif menu == "📸 多媒体分析":
        st.header("📸 产品图文/视频深度分析")
        st.write("利用 Gemini 3 的原生多模态能力分析你的产品素材")
        
        media_file = st.file_uploader("上传产品图或拍摄素材", type=['png', 'jpg', 'jpeg', 'mp4'])
        user_query = st.text_input("询问 AI 关于此素材的问题", value="请总结该产品的 3 个核心卖点，并写一段英文推文")
        
        if media_file:
            if media_file.type.startswith('image'):
                image = Image.open(media_file)
                st.image(image, caption="已上传图片", width=500)
                if st.button("⚡ 执行视觉分析"):
                    response = model.generate_content([user_query, image])
                    st.subheader("分析结果")
                    st.write(response.text)
            elif media_file.type.startswith('video'):
                st.video(media_file)
                st.info("💡 提示：视频分析建议使用 Gemini 3 Pro 获得更精准的时间轴理解")
                # 视频处理逻辑（Gemini 1.5/3 API 需先上传 File API，这里做基础占位）
                if st.button("🎬 执行视频总结"):
                    st.warning("视频深度分析接口需对接 Google File API，建议先测试图片分析。")

    # --- 模块 4：数据库模拟 ---
    elif menu == "🗄️ 数据库模拟":
        st.header("🗄️ 简易业务数据库 (Session 存储)")
        if 'b2b_db' not in st.session_state:
            st.session_state.b2b_db = []
        
        c1, c2 = st.columns([3, 1])
        with c1:
            new_data = st.text_input("录入客户或订单信息（如：澳洲 ACIC 咨询记录）")
        with c2:
            if st.button("💾 存入数据库"):
                st.session_state.b2b_db.append(new_data)
        
        st.divider()
        st.write("### 历史记录清单")
        for i, item in enumerate(st.session_state.b2b_db):
            st.write(f"{i+1}. {item}")
