import streamlit as st
import google.generativeai as genai
import pandas as pd
from PIL import Image

# 1. 页面配置与 API 初始化
st.set_page_config(page_title="B2B 外贸全能助手", layout="wide")

with st.sidebar:
    st.title("🛠️ 功能面板")
    api_key = st.text_input("输入 Gemini API Key", type="password")
    # 功能导航
    menu = st.radio("选择业务模块", ["客户开发", "财务审计", "多媒体分析 (图文/视频)", "数据库模拟"])
    
    if api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')

# 2. 各模块逻辑实现
if not api_key:
    st.warning("请先在侧边栏输入 API Key。")
else:
    # --- 模块 1：客户开发 ---
    if menu == "客户开发":
        st.header("🌍 全球客户开发 (开发信润色/询盘模拟)")
        target_role = st.selectbox("目标角色", ["采购经理", "CEO", "技术主管"])
        draft_text = st.text_area("输入你的开发信草稿或客户信息")
        if st.button("生成高转化率回复"):
            response = model.generate_content(f"作为外贸专家，请针对{target_role}优化以下内容，使其更具吸引力且专业：\n{draft_text}")
            st.write(response.text)

    # --- 模块 2：财务审计 ---
    elif menu == "财务审计":
        st.header("📊 财务审计与成本分析")
        uploaded_file = st.file_uploader("上传成本/利润 Excel 或 CSV", type=['csv', 'xlsx'])
        if uploaded_file:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('csv') else pd.read_excel(uploaded_file)
            st.dataframe(df)
            st.info("AI 正在分析异常数据或利润点...")
            # 将表格数据转为文本给 AI 审计
            response = model.generate_content(f"请审计以下财务数据并给出优化建议：\n{df.to_string()}")
            st.write(response.text)

    # --- 模块 3：多媒体分析 ---
    elif menu == "多媒体分析 (图文/视频)":
        st.header("📸 产品图文/视频深度分析")
        media_file = st.file_uploader("上传产品图片或短视频", type=['png', 'jpg', 'jpeg', 'mp4'])
        user_query = st.text_input("你想让 AI 观察什么？", "请描述该产品的卖点和潜在缺陷")
        
        if media_file:
            if media_file.type.startswith('image'):
                img = Image.open(media_file)
                st.image(img, caption="待分析图片", width=400)
                if st.button("开始图片分析"):
                    response = model.generate_content([user_query, img])
                    st.write(response.text)
            elif media_file.type.startswith('video'):
                st.video(media_file)
                st.info("视频分析由于 API 限制，通常需要先上传至 Google 云端或使用特定的 File API 处理。这里建议先验证图片功能。")

    # --- 模块 4：数据库模拟 ---
    elif menu == "数据库模拟":
        st.header("🗄️ 业务数据库简易管理")
        st.write("此处可用于记录客户档案或订单状态（当前为 Session 存储演示）")
        if 'db' not in st.session_state:
            st.session_state.db = []
        
        new_entry = st.text_input("添加新记录 (如：澳洲客户A - 订单号123)")
        if st.button("存入数据库"):
            st.session_state.db.append(new_entry)
            st.success("记录已保存")
        st.write("当前记录：", st.session_state.db)
